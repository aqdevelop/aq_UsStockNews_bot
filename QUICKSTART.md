# 🚀 5분 안에 Railway 배포하기

## ⚡ 빠른 시작

### Step 1: 텔레그램 봇 만들기 (1분)
1. 텔레그램에서 `@BotFather` 검색
2. `/newbot` 입력
3. 봇 이름 입력 → Token 받기
4. 봇에게 `/start` 또는 아무 메시지 보내기

### Step 2: Chat ID 확인 (30초)
브라우저에서 열기 (YOUR_BOT_TOKEN 부분만 교체):
```
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
```

결과에서 `"chat":{"id":123456789` ← 이 숫자가 Chat ID

### Step 3: OpenAI API 키 (2분)
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. 키 복사 (sk-로 시작)

### Step 4: Railway 배포 (2분)
1. https://railway.app 접속 → GitHub 로그인
2. "New Project" → "Empty Project"
3. "GitHub Repo" → 업로드한 레포 선택
4. "Variables" 탭 클릭 → 아래 추가:
   ```
   TELEGRAM_BOT_TOKEN = 여기에_봇_토큰
   TELEGRAM_CHAT_ID = 여기에_숫자만
   OPENAI_API_KEY = 여기에_sk_키
   ```
5. 자동 배포 완료!

### Step 5: 확인
- "Logs" 탭에서 "스케줄 등록 완료" 메시지 확인
- 다음 발송 시간 대기 (한국시간 기준):
  - **평일**: 오전 7시, 오후 10시 30분 (2회)
  - **주말**: 오전 7시만 (1회)
- 섬머타임 자동 반영됨

## 💡 즉시 테스트하려면?

Railway에서:
1. Settings → Deploy
2. Start Command: `python news_summary_gpt.py`
3. Redeploy
4. 텔레그램 확인!
5. 다시 `python scheduler.py`로 변경

완료! 🎉

## ❓ 문제 해결

### 봇이 응답 없음
- Bot Token 재확인
- Chat ID가 숫자만 입력되었는지 확인 (따옴표 없이)

### OpenAI 오류
- API 키 확인
- 크레딧 잔액 확인

### Railway 무료 한도
- 월 $5 크레딧 무료
- 이 봇은 월 $1-2 정도 사용

## 📞 문의
contact@aqresearch.com
