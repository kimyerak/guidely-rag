"""
문서 및 청크 관리 서비스
"""
import logging
import json
from typing import List, Optional, Dict, Any
import numpy as np
from database.connection import get_db_cursor
from database.models import Document, DocumentChunk, SearchResult

logger = logging.getLogger(__name__)

class DocumentService:
    """문서 관리 서비스"""
    
    def create_document(self, document: Document) -> int:
        """새 문서 생성"""
        with get_db_cursor() as (cursor, conn):
            query = """
                INSERT INTO documents (title, file_name, file_type, source_url, content, metadata, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            # Document 객체의 속성을 직접 전달
            cursor.execute(query, (
                document.title,
                document.file_name,
                document.file_type,
                document.source_url,
                document.content,
                json.dumps(document.metadata) if document.metadata else None,
                document.is_active
            ))
            document_id = cursor.fetchone()['id']
            conn.commit()
            logger.info(f"문서 생성 완료: ID {document_id}")
            return document_id

    def get_document(self, document_id: int) -> Optional[Document]:
        """문서 조회"""
        with get_db_cursor() as (cursor, conn):
            query = "SELECT * FROM documents WHERE id = %s"
            cursor.execute(query, (document_id,))
            result = cursor.fetchone()
            return Document.from_dict(result) if result else None

    def get_all_documents(self, active_only: bool = True) -> List[Document]:
        """모든 문서 조회"""
        with get_db_cursor() as (cursor, conn):
            if active_only:
                query = "SELECT * FROM documents WHERE is_active = TRUE ORDER BY upload_date DESC"
            else:
                query = "SELECT * FROM documents ORDER BY upload_date DESC"
            cursor.execute(query)
            results = cursor.fetchall()
            return [Document.from_dict(row) for row in results]

    def update_document(self, document: Document) -> bool:
        """문서 업데이트"""
        with get_db_cursor() as (cursor, conn):
            query = """
                UPDATE documents 
                SET title = %(title)s, file_name = %(file_name)s, file_type = %(file_type)s,
                    source_url = %(source_url)s, content = %(content)s, metadata = %(metadata)s,
                    is_active = %(is_active)s
                WHERE id = %(id)s
            """
            cursor.execute(query, document.to_dict())
            conn.commit()
            return cursor.rowcount > 0

    def delete_document(self, document_id: int) -> bool:
        """문서 삭제 (CASCADE로 청크도 함께 삭제)"""
        with get_db_cursor() as (cursor, conn):
            query = "DELETE FROM documents WHERE id = %s"
            cursor.execute(query, (document_id,))
            conn.commit()
            return cursor.rowcount > 0

class ChunkService:
    """청크 관리 서비스"""
    
    def create_chunks_for_document(self, document_id: int, content: str, 
                                 embedding_model, chunk_size: int = 500, 
                                 chunk_overlap: int = 50) -> List[int]:
        """문서 내용을 청크로 분할하고 임베딩하여 저장"""
        from sentence_transformers import SentenceTransformer
        
        # 텍스트를 청크로 분할
        chunks = self._split_text_into_chunks(content, chunk_size, chunk_overlap)
        
        # 각 청크에 대해 임베딩 생성 및 저장
        chunk_ids = []
        for i, chunk_text in enumerate(chunks):
            # 임베딩 생성
            embedding = embedding_model.encode(chunk_text).tolist()
            
            # 청크 객체 생성
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_text=chunk_text,
                chunk_index=i,
                embedding=embedding,
                metadata={"chunk_size": len(chunk_text)}
            )
            
            # 청크 저장
            chunk_id = self.create_chunk(chunk)
            chunk_ids.append(chunk_id)
        
        return chunk_ids
    
    def _split_text_into_chunks(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """텍스트를 청크로 분할"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # 문장 경계에서 자르기 (개선된 분할)
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                last_space = chunk.rfind(' ')
                
                # 가장 적절한 분할점 찾기
                split_point = max(last_period, last_newline, last_space)
                if split_point > start + chunk_size // 2:  # 너무 작은 청크 방지
                    chunk = text[start:start + split_point + 1]
                    end = start + split_point + 1
            
            chunks.append(chunk.strip())
            start = end - chunk_overlap
            
            if start >= len(text):
                break
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def create_chunk(self, chunk: DocumentChunk) -> int:
        """단일 청크 생성"""
        with get_db_cursor() as (cursor, conn):
            query = """
                INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            # DocumentChunk 객체의 속성을 직접 전달
            cursor.execute(query, (
                chunk.document_id,
                chunk.chunk_text,
                chunk.chunk_index,
                chunk.embedding,
                json.dumps(chunk.metadata) if chunk.metadata else None
            ))
            chunk_id = cursor.fetchone()['id']
            conn.commit()
            return chunk_id
    
    def create_chunks(self, document_id: int, chunks: List[DocumentChunk]) -> List[int]:
        """문서 청크들 생성"""
        with get_db_cursor() as (cursor, conn):
            chunk_ids = []
            for chunk in chunks:
                chunk.document_id = document_id
                query = """
                    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding, metadata)
                    VALUES (%(document_id)s, %(chunk_text)s, %(chunk_index)s, %(embedding)s, %(metadata)s)
                    RETURNING id
                """
                cursor.execute(query, chunk.to_dict())
                chunk_id = cursor.fetchone()['id']
                chunk_ids.append(chunk_id)
            conn.commit()
            logger.info(f"청크 {len(chunks)}개 생성 완료: 문서 ID {document_id}")
            return chunk_ids

    def search_similar_chunks(self, query_embedding: List[float], 
                            match_threshold: float = 0.7, 
                            match_count: int = 5) -> List[SearchResult]:
        """유사한 청크 검색"""
        with get_db_cursor() as (cursor, conn):
            query = """
                SELECT 
                    dc.id as chunk_id,
                    dc.document_id,
                    dc.chunk_text,
                    1 - (dc.embedding <=> %s::vector) as similarity,
                    dc.metadata,
                    d.title as document_title,
                    d.source_url
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.is_active = TRUE
                AND 1 - (dc.embedding <=> %s::vector) > %s
                ORDER BY dc.embedding <=> %s::vector
                LIMIT %s
            """
            cursor.execute(query, (query_embedding, query_embedding, match_threshold, query_embedding, match_count))
            results = cursor.fetchall()
            
            search_results = []
            for row in results:
                # metadata 처리 - 이미 딕셔너리인 경우와 JSON 문자열인 경우 모두 처리
                metadata = row['metadata']
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except (json.JSONDecodeError, TypeError):
                        metadata = None
                elif metadata is None:
                    metadata = None
                
                search_results.append(SearchResult(
                    chunk_id=row['chunk_id'],
                    document_id=row['document_id'],
                    chunk_text=row['chunk_text'],
                    similarity=float(row['similarity']),
                    metadata=metadata,
                    document_title=row['document_title'],
                    source_url=row['source_url']
                ))
            
            return search_results

    def search_by_keywords(self, query: str, match_count: int = 5) -> List[SearchResult]:
        """키워드 기반 검색"""
        # 호랑이 관련 키워드들
        keywords = [
            "호작도", "용호도", "산신도", "호렵도", "월하송림호족도", "호호도",
            "호랑이", "범", "호", "까치", "호족도"
        ]
        
        # 쿼리에서 키워드 추출
        found_keywords = [kw for kw in keywords if kw in query]
        
        # 호호도 관련 키워드 매핑 (호호도 -> 호작도)
        if "호호도" in found_keywords and "호작도" not in found_keywords:
            found_keywords.append("호작도")
            print(f"키워드 검색 - 호호도 관련으로 호작도 추가")
        
        print(f"키워드 검색 - 쿼리: {query}")
        print(f"키워드 검색 - 찾은 키워드: {found_keywords}")
        
        if not found_keywords:
            print("키워드 검색 - 매칭되는 키워드 없음")
            return []
        
        with get_db_cursor() as (cursor, conn):
            # 키워드로 검색
            keyword_conditions = " OR ".join([f"dc.chunk_text ILIKE '%{kw}%'" for kw in found_keywords])
            
            query_sql = f"""
                SELECT 
                    dc.id as chunk_id,
                    dc.document_id,
                    dc.chunk_text,
                    0.9 as similarity,
                    dc.metadata,
                    d.title as document_title,
                    d.source_url
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.is_active = TRUE
                AND ({keyword_conditions})
                ORDER BY dc.id
                LIMIT {match_count}
            """
            
            print(f"키워드 검색 SQL: {query_sql}")
            
            cursor.execute(query_sql)
            results = cursor.fetchall()
            
            search_results = []
            for row in results:
                # metadata 처리
                metadata = row['metadata']
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except (json.JSONDecodeError, TypeError):
                        metadata = None
                elif metadata is None:
                    metadata = None
                
                search_results.append(SearchResult(
                    chunk_id=row['chunk_id'],
                    document_id=row['document_id'],
                    chunk_text=row['chunk_text'],
                    similarity=float(row['similarity']),
                    metadata=metadata,
                    document_title=row['document_title'],
                    source_url=row['source_url']
                ))
            
            return search_results

    def delete_chunks_by_document(self, document_id: int) -> bool:
        """문서의 모든 청크 삭제"""
        with get_db_cursor() as (cursor, conn):
            query = "DELETE FROM document_chunks WHERE document_id = %s"
            cursor.execute(query, (document_id,))
            conn.commit()
            return cursor.rowcount > 0
