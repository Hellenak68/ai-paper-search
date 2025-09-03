# 보안 가이드

## 🔐 API 키 관리

### 권장 방법 (우선순위 순)

#### 1. **환경 변수 사용** (가장 안전)
```bash
# Windows
set UPSTAGE_API_KEY=your_api_key_here

# Linux/Mac
export UPSTAGE_API_KEY=your_api_key_here
```

#### 2. **런타임 입력** (개발/테스트용)
애플리케이션 실행 시 터미널에서 안전하게 입력:
```bash
uvicorn app.main:app --reload
# API 키 입력 프롬프트가 나타남
```

#### 3. **.env 파일** (로컬 개발용)
```bash
# .env 파일에 추가
UPSTAGE_API_KEY=your_api_key_here
```

### ❌ 절대 하지 말아야 할 것들

1. **소스 코드에 API 키 하드코딩**
2. **Git에 .env 파일 커밋**
3. **공개 저장소에 API 키 노출**
4. **로그 파일에 API 키 출력**

## 🛡️ 보안 모범 사례

### 개발 환경
- `.env` 파일을 `.gitignore`에 포함
- API 키는 마스킹하여 로그 출력
- 개발용 API 키와 프로덕션용 분리

### 프로덕션 환경
- 환경 변수로만 API 키 관리
- 컨테이너 시크릿 사용 (Docker/Kubernetes)
- API 키 로테이션 정책 수립

### 배포 플랫폼별 설정

#### Render.com
```yaml
# render.yaml
envVars:
  - key: UPSTAGE_API_KEY
    sync: false  # 중요: false로 설정
```

#### Fly.io
```bash
fly secrets set UPSTAGE_API_KEY=your_api_key
```

#### Docker
```bash
docker run -e UPSTAGE_API_KEY=your_api_key your-app
```

## 🔍 보안 체크리스트

- [ ] API 키가 소스 코드에 하드코딩되지 않음
- [ ] .env 파일이 .gitignore에 포함됨
- [ ] 프로덕션에서 환경 변수 사용
- [ ] API 키가 로그에 출력되지 않음
- [ ] 개발/프로덕션 API 키 분리
- [ ] 정기적인 API 키 로테이션

## 🚨 보안 사고 대응

API 키가 노출된 경우:
1. 즉시 Upstage에서 API 키 비활성화
2. 새로운 API 키 발급
3. 모든 환경에서 새 키로 교체
4. 노출된 키 사용 내역 확인

## 📞 지원

보안 관련 문의사항이 있으시면:
- GitHub Issues 생성
- 개발팀에 직접 연락
