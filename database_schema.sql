-- RAG 시스템용 데이터베이스 스키마
-- PostgreSQL + pgvector

-- 1. 문서 테이블 (원본 문서 정보)
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255),
    file_type VARCHAR(50), -- 'pdf', 'markdown', 'url' 등
    source_url TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content TEXT, -- 원본 전체 텍스트
    metadata JSONB, -- 추가 메타데이터
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. 문서 청크 테이블 (RAG 검색용)
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL, -- 문서 내 청크 순서
    embedding VECTOR(384), -- 벡터 임베딩 (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
    metadata JSONB, -- 청크별 메타데이터
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 벡터 검색을 위한 인덱스
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 4. 일반 검색을 위한 인덱스
CREATE INDEX ON document_chunks (document_id);
CREATE INDEX ON documents (is_active);
CREATE INDEX ON documents (file_type);

-- 5. 벡터 검색 함수 (코사인 유사도)
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding VECTOR(384),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    chunk_id INT,
    document_id INT,
    chunk_text TEXT,
    similarity FLOAT,
    metadata JSONB
)
LANGUAGE SQL
AS $$
    SELECT 
        dc.id as chunk_id,
        dc.document_id,
        dc.chunk_text,
        1 - (dc.embedding <=> query_embedding) as similarity,
        dc.metadata
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE d.is_active = TRUE
    AND 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- 6. 샘플 데이터 삽입 (테스트용)
INSERT INTO documents (title, file_name, file_type, content, metadata) VALUES
('케이팝데몬헌터스', 'kpop_demon_hunters', 'url', '케이팝데몬헌터스 게임 정보...', '{"source": "namu.wiki", "category": "game"}'),
('호랑이 전시', 'tiger_exhibition', 'markdown', '국립중앙박물관 호랑이 전시 정보...', '{"source": "museum", "category": "exhibition"}');
