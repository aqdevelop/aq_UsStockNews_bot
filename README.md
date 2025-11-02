# 🇺🇸 해외주식 뉴스 자동 요약 텔레그램 봇

GPT-4o-mini를 활용한 해외주식 뉴스 자동 수집 및 요약 봇입니다.  
하루 2회 (오전 7시, 오후 11시) 중요 뉴스를 선별하여 텔레그램으로 전송합니다.

## 📋 주요 기능

- **자동 뉴스 수집**: 주요 해외 금융 매체 RSS 피드 모니터링
- **GPT 기반 선별**: 투자자에게 중요한 뉴스만 자동 선별
- **한국어 요약**: 영문 뉴스를 한국어로 2-3문장 요약
- **중복 제거**: GPT 기반 유사 주제 필터링
- **스케줄 전송**: 
  - 오전 7시 (KST): 미국 장 마감 후 뉴스
  - 오후 11시 (KST): 미국 장 시작 전후 뉴스

## 🌐 뉴스 소스

### 해외 매체
- MarketWatch
- Reuters Business
- Bloomberg Markets
- CNBC
- Yahoo Finance
- Investing.com
- TechCrunch
- The Verge
- Financial Times
- Wall Street Journal

### 국내 해외주식 뉴스
- 연합인포맥스
- 서울경제
- 한국경제

## ⏰ 최적 발송 시간

### 오전 7시 (한국시간) - 모닝브리프
- **미국 동부 시간**: 오후 5-6시 (전날)
- **내용**: 미국 장 마감 후 주요 뉴스
- **포함**: 실적 발표, 장 마감 동향, 시간외 이슈

### 오후 11시 (한국시간) - 이브닝브리프
- **미국 동부 시간**: 오전 9-10시 (당일)
- **내용**: 미국 장 시작 전후 주요 뉴스
- **포함**: 프리마켓 동향, 경제지표, 당일 이슈

## 🚀 사용 방법

### 1. 텔레그램 봇 생성

1. [@BotFather](https://t.me/botfather) 에게 `/newbot` 메시지 전송
2. 봇 이름 및 사용자명 설정
3. 발급받은 **Bot Token** 저장

### 2. Chat ID 확인

1. 봇에게 아무 메시지나 전송
2. 브라우저에서 다음 URL 접속:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. `"chat":{"id":` 뒤의 숫자가 **Chat ID**

### 3. OpenAI API 키 발급

1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. API Key 생성
3. 발급받은 **API Key** 저장

### 4. Railway 배포 (무료)

1. [Railway.app](https://railway.app) 가입
2. New Project → Deploy from GitHub repo
3. 환경 변수 설정:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   OPENAI_API_KEY=your_openai_key_here
   HEADER_IMAGE_URL=  (선택사항)
   ```
4. Deploy 완료 후 자동 실행

### 5. 로컬 실행

```bash
# 환경 변수 설정
cp config.env.template config.env
# config.env 파일 편집 후

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 로드
export $(cat config.env | xargs)

# 스케줄러 실행
python scheduler.py

# 또는 즉시 테스트
python news_summary_gpt.py
```

## 📊 선별 기준

GPT가 다음 기준으로 중요 뉴스를 선별합니다:

1. **주요 기업**: 실적, M&A, 신제품 발표
2. **거시경제**: 연준 금리, 경제지표
3. **규제/정책**: 정부 발표, 규제 변화
4. **시장 동향**: 주요 지수 급등락
5. **섹터 이슈**: 기술, 금융, 에너지 등

제외 항목:
- 단순 의견/분석 기사
- 소규모 기업 뉴스
- 중요도 낮은 루머

## 🎨 커스터마이징

### 발송 시간 변경

`scheduler.py`에서 시간 수정:

```python
schedule.every().day.at("07:00").do(send_morning_news)  # 오전 7시
schedule.every().day.at("23:00").do(send_evening_news)  # 오후 11시
```

### 뉴스 개수 조정

```python
bot.run(hours=12, top_n=10)  # top_n 값 변경
```

### 뉴스 소스 추가

`news_summary_gpt.py`의 `self.rss_feeds`에 RSS 피드 추가:

```python
self.rss_feeds = {
    'Your Source': 'https://example.com/rss',
    # ...
}
```

## 💰 비용 안내

- **Railway**: 월 $5 크레딧 무료 제공 (충분히 사용 가능)
- **OpenAI API**: GPT-4o-mini 사용 시 매우 저렴
  - 하루 2회 실행 시 월 $1-2 수준

## 📝 라이선스

MIT License

## 🤝 문의

뉴스 자동 포워딩 서비스 문의:  
📧 contact@aqresearch.com

## 🔧 트러블슈팅

### 뉴스가 전송되지 않을 때

1. Railway 로그 확인
2. 환경 변수 확인 (특히 TELEGRAM_CHAT_ID는 숫자만)
3. OpenAI API 크레딧 잔액 확인

### 중복 뉴스 발송

- GPT가 자동으로 7일간 중복 검사
- `sent_news_history.json` 파일 삭제 후 재실행

### 시간대 문제

- Railway 서버는 UTC 기준
- 한국시간(KST)은 UTC+9
- 스케줄러가 자동으로 한국시간 기준 실행
