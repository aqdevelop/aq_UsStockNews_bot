# 🔑 Reddit API 발급 가이드

주간 핫 뉴스 기능을 사용하려면 Reddit API 키가 필요합니다. (선택사항)

## 📋 발급 절차 (5분)

### 1. Reddit 계정 생성/로그인
- https://www.reddit.com 접속
- 계정이 없으면 가입

### 2. 앱 생성 페이지 접속
https://www.reddit.com/prefs/apps

또는:
1. Reddit 로그인
2. 우측 상단 프로필 → "User Settings"
3. 좌측 메뉴 "Safety & Privacy"
4. 맨 아래 "Manage third-party app authorization"

### 3. 새 앱 생성
1. **"create another app..."** 또는 **"are you a developer? create an app..."** 클릭
2. 정보 입력:
   ```
   name: US Stock News Bot
   App type: ● script (선택)
   description: Stock news analysis bot
   about url: (비워두기)
   redirect uri: http://localhost:8080
   ```
3. **"create app"** 클릭

### 4. API 키 확인
생성 후 다음 정보가 표시됩니다:

```
US Stock News Bot
personal use script

[앱 아이콘]

[14자 문자열]  ← 이것이 CLIENT_ID
secret: [27자 문자열]  ← 이것이 CLIENT_SECRET
```

**예시**:
```
CLIENT_ID: abc123def456gh
CLIENT_SECRET: xyz789uvw456rst123opq456
```

### 5. Railway 환경 변수 설정
Railway Dashboard → Variables:

```
REDDIT_CLIENT_ID=abc123def456gh
REDDIT_CLIENT_SECRET=xyz789uvw456rst123opq456
```

완료! 🎉

---

## 🔍 Reddit API 없이 사용하기

Reddit API는 **선택사항**입니다.

### Reddit 없이 사용 시:
- ✅ 일반 뉴스: 정상 작동
- ✅ 주간 핫 뉴스: 작동함 (7일치 뉴스 기록만 분석)
- ❌ WSB 화제성: 분석 안 됨
- ❌ Reddit 데이터: 수집 안 됨

### Reddit 사용 시:
- ✅ 일반 뉴스: 정상 작동
- ✅ 주간 핫 뉴스: 작동함 + WSB 데이터 추가
- ✅ WSB 화제성: 분석됨
- ✅ Reddit 트렌드: 반영됨

---

## 💰 비용

- ✅ **완전 무료!**
- Rate Limit: 60 requests/minute (충분함)
- 주간 1회 사용 시 여유롭게 운영 가능

---

## 🧪 테스트

Reddit API 설정 후 테스트:

```bash
cd us-stock-news-bot
python weekly_hot_analyzer.py
```

성공 시:
```
🔍 Reddit r/wallstreetbets 분석 중...
✅ Reddit 분석 완료: 15개 티커 발견
   TSLA: 45회 언급
   NVDA: 32회 언급
   SPY: 28회 언급
   ...
```

---

## ⚠️ 문제 해결

### "401 Unauthorized" 오류
- CLIENT_ID 또는 CLIENT_SECRET 오류
- Reddit 앱 설정 확인
- Railway Variables 재확인

### "403 Forbidden" 오류
- Reddit 계정 확인 (이메일 인증 필요)
- User Agent 문제 (코드에 이미 설정됨)

### Rate Limit 초과
- 60 requests/minute 제한
- 주간 1회만 사용하므로 문제 없음
- 혹시 초과 시 1분 대기

---

## 📞 문의

Reddit API 관련 문의:
📧 contact@aqresearch.com
