# 🇺🇸 해외주식 뉴스 자동 요약 텔레그램 봇

GPT-4o-mini를 활용한 해외주식 뉴스 자동 수집 및 요약 봇입니다.  
하루 2회 (오전 7시, 오후 11시) 중요 뉴스를 선별하여 텔레그램으로 전송합니다.

## 📋 주요 기능

- **자동 뉴스 수집**: 주요 해외 금융 매체 RSS 피드 모니터링
- **GPT 기반 선별**: 투자자에게 중요한 뉴스만 자동 선별
- **한국어 요약**: 영문 뉴스를 한국어로 2-3문장 요약
- **중복 제거**: GPT 기반 유사 주제 필터링
- **🔔 여러 채팅방 지원**: 한 번에 여러 텔레그램 채팅방으로 동시 전송 가능
- **스케줄 전송**: 
  - **평일**: 오전 7시, 오후 10시 30분 (하루 2회)
  - **토요일**: 오전 7시만 (하루 1회)
  - **일요일**: 오전 7시 + 🔥 주간 핫 TOP 10 (GPT-4o)
  - **매월 1일**: 📅 월간 핫 TOP 10 추가 (GPT-4o)
  - 섬머타임 자동 반영
- **🔥 주간 핫 뉴스** (일요일):
  - Reddit r/wallstreetbets 화제 종목 분석
  - Google Trends 검색량 확인
  - 7일간 반복 등장 이슈 탐지
  - GPT-4o 고품질 분석
- **📅 월간 핫 뉴스** (매월 1일):
  - 30일간 뉴스 기록 심층 분석
  - 월간 시장 흐름 및 분위기 파악
  - 섹터별 중요 이슈 정리
  - 다음 달 전망 포함
  - GPT-4o 최고 품질 분석

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

## ⏰ 발송 시간 (한국시간 KST 고정)

### 📅 매일 정기 전송

#### 오전 8시 - 모닝브리프 ☀️
- **전송 시간**: 매일 오전 8시 (KST)
- **내용**: 미국 장 마감 후 주요 뉴스
- **포함**: 실적 발표, 장 마감 동향, 시간외 이슈

#### 오후 10시 - 이브닝브리프 🌙
- **전송 시간**: 매일 오후 10시 (KST)
- **내용**: 미국 장 시작 전후 주요 뉴스
- **포함**: 프리마켓 동향, 경제지표, 당일 이슈

### 📅 특별 전송

#### 일요일 - 주간 핫 뉴스 🔥
- **오전 8시**: 일반 모닝브리프
- **오전 8시 직후**: 🔥 **주간 핫 이슈 TOP 10** (GPT-4o)
  - 지난 7일간 뉴스 분석
  - Reddit WSB 화제 종목
  - Google Trends 검색량
  - GPT-4o 고품질 분석
  - 반복 등장 이슈 자동 탐지

#### 매월 1일 - 월간 핫 뉴스 📅
- **오전 8시**: 일반 모닝브리프
- **오전 8시 직후**: 🔥 주간 핫 이슈 (일요일인 경우)
- **오전 8시 직후**: 📅 **월간 핫 이슈 TOP 10** (GPT-4o)
  - 지난 30일간 뉴스 기록 심층 분석
  - 월간 시장 흐름 및 분위기
  - 섹터별 중요 이슈 정리
  - 다음 달 전망 포함
  - GPT-4o 최고 품질 분석

> 💡 **간단한 스케줄**: 매일 오전 8시, 오후 10시 고정. 섬머타임 고려 없이 한국시간 기준으로만 작동합니다.

## 🚀 사용 방법

### 1. 텔레그램 봇 생성

1. [@BotFather](https://t.me/botfather) 에게 `/newbot` 메시지 전송
2. 봇 이름 및 사용자명 설정
3. 발급받은 **Bot Token** 저장

### 2. Chat ID 확인

#### 단일 채팅방
1. 봇에게 아무 메시지나 전송
2. 브라우저에서 다음 URL 접속:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. `"chat":{"id":` 뒤의 숫자가 **Chat ID**

#### 여러 채팅방 (콤마로 구분)
- 여러 개의 Chat ID를 콤마로 구분하여 입력
- 예시: `-1001234567890,-1009876543210,-1008765432109`
- 각 Chat ID는 봇이 멤버로 등록되어 있어야 함

> 💡 **그룹 채팅방 Chat ID 확인 방법**:
> 1. 봇을 그룹에 추가
> 2. 그룹에서 봇에게 아무 메시지나 전송 (예: `/start`)
> 3. `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 접속
> 4. 그룹의 Chat ID는 `-100`으로 시작하는 음수 형태

### 3. OpenAI API 키 발급

1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. API Key 생성
3. 발급받은 **API Key** 저장

### 4. Reddit API 발급 (선택사항 - 주간 핫 뉴스용)

Reddit r/wallstreetbets 데이터를 활용하려면:

1. [Reddit Apps](https://www.reddit.com/prefs/apps) 접속
2. "create another app" 클릭
3. App type: "script" 선택
4. redirect uri: `http://localhost:8080`
5. **CLIENT_ID**와 **CLIENT_SECRET** 복사

**자세한 가이드**: [REDDIT_API_GUIDE.md](REDDIT_API_GUIDE.md)

> 💡 **Reddit API 없이도 사용 가능!**  
> 주간 핫 뉴스는 Reddit 없이도 7일치 뉴스 기록만으로 분석됩니다.

### 5. Railway 배포 (무료)

1. [Railway.app](https://railway.app) 가입
2. New Project → Deploy from GitHub repo
3. 환경 변수 설정:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_IDS=your_chat_id_here  (여러 개는 콤마로 구분)
   OPENAI_API_KEY=your_openai_key_here
   HEADER_IMAGE_URL=  (선택사항)
   REDDIT_CLIENT_ID=  (선택사항, 주간 핫 뉴스용)
   REDDIT_CLIENT_SECRET=  (선택사항, 주간 핫 뉴스용)
   ```
   
   예시 (여러 채팅방):
   ```
   TELEGRAM_CHAT_IDS=-1001234567890,-1009876543210,-1008765432109
   ```

4. Deploy 완료 후 **즉시 12시간 뉴스 전송** (테스트)
5. 테스트 완료 후 정기 스케줄 자동 시작

> 💡 **배포 시 자동 테스트**: Railway에 배포하면 즉시 최근 12시간 뉴스를 분석하여 모든 채팅방에 전송합니다. 이를 통해 설정이 올바른지 바로 확인할 수 있습니다!

> ⏱️ **채팅방 간격**: 여러 채팅방에 전송할 때 각 채팅방 사이에 5초 간격을 두어 안정적으로 전송합니다.

### 6. Railway Volume 설정 (권장)

주간 핫 뉴스 기능을 위해 7일치 뉴스 기록을 저장할 Volume 설정:

1. Railway Dashboard → Settings
2. Volumes 섹션 → "New Volume"
3. Mount Path: `/data`
4. "Add" 클릭

> 무료 1GB Volume으로 충분합니다!

### 7. 로컬 실행

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
- **OpenAI API**: 
  - 일일 뉴스 (GPT-4o-mini): 월 $1.04
  - 주간 핫 뉴스 (GPT-4o): 월 $0.25
  - 월간 핫 뉴스 (GPT-4o): 월 $0.36
  - **총 월 비용**: $1.65 (약 2,200원)
- **Reddit API**: 완전 무료
- **Google Trends**: 완전 무료
- **Railway Volume**: 1GB 무료 (충분)

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
- **섬머타임 자동 반영**: 미국 섬머타임 기간에도 한국시간은 고정 (오전 7시, 오후 10시 30분)

### 발송 시간 확인

- **모닝브리프**: 오전 7시 (KST) 고정
- **이브닝브리프**: 오후 10시 30분 (KST) 고정
- 미국 동부시간은 섬머타임에 따라 자동 변경됨
