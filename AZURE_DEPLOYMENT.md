# Azure App Service 배포 가이드

## 1. Azure App Service 설정

### Python 버전 설정
- **Python 3.9** 또는 **Python 3.10** 사용 권장
- Azure Portal에서 Configuration > General Settings에서 설정

### Startup Command 설정
```
python startup.py
```

### 환경 변수 설정
Azure Portal > Configuration > Application Settings에서 다음 변수 추가:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## 2. 배포 방법

### 방법 1: Git 배포
1. Azure App Service에 Git 리포지토리 연결
2. 코드 푸시 시 자동 배포

### 방법 2: ZIP 배포
1. 프로젝트 폴더를 ZIP으로 압축
2. Azure Portal > Deployment Center > ZIP Deploy 사용

## 3. 로그 확인

### Application Logs
- Azure Portal > Monitoring > Log stream
- 또는 Kudu Console에서 `D:\home\LogFiles\python.log` 확인

### 일반적인 문제 해결

1. **ModuleNotFoundError**: 
   - `startup.py`가 올바른 경로에 있는지 확인
   - `requirements.txt`에 필요한 패키지가 모두 포함되어 있는지 확인

2. **Port 오류**:
   - `startup.py`에서 `PORT` 환경변수 사용 확인
   - Azure App Service는 동적 포트 할당

3. **메모리 부족**:
   - App Service Plan을 더 높은 등급으로 업그레이드
   - `faiss-cpu` 대신 `faiss-gpu` 사용 고려 (더 높은 등급 필요)

## 4. 성능 최적화

### 벡터스토어 캐싱
- 벡터스토어는 `/home/site/wwwroot/faiss_index/`에 저장
- 컨테이너 재시작 시에도 유지됨

### 모델 로딩 최적화
- 첫 요청 시 모델 로딩으로 인한 지연 발생 가능
- Health check로 준비 상태 확인

## 5. 모니터링

### Health Check
```
GET https://your-app.azurewebsites.net/health
```

### API 테스트
```
POST https://your-app.azurewebsites.net/rag/query
{
  "message": "케이팝에 대해 알려주세요",
  "character": "rumi"
}
```
