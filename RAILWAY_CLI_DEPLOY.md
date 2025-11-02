# Railway CLI 배포 가이드

## 1. Railway CLI 설치

### macOS/Linux
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### Windows (PowerShell)
```powershell
iwr https://railway.app/install.ps1 | iex
```

## 2. Railway 로그인
```bash
railway login
```
브라우저가 열리면 GitHub로 로그인

## 3. 프로젝트 초기화
```bash
# 프로젝트 폴더로 이동
cd us-stock-news-bot

# Railway 프로젝트 초기화
railway init
```

## 4. 환경 변수 설정
```bash
# 하나씩 추가
railway variables set TELEGRAM_BOT_TOKEN=여기에_봇_토큰
railway variables set TELEGRAM_CHAT_ID=여기에_챗_아이디
railway variables set OPENAI_API_KEY=여기에_OpenAI_키
railway variables set HEADER_IMAGE_URL=
```

## 5. 배포
```bash
railway up
```

## 6. 로그 확인
```bash
railway logs
```

## 7. 대시보드 열기
```bash
railway open
```

완료! 🎉
