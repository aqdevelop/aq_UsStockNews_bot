#!/usr/bin/env python3
"""
주간 핫 뉴스 분석기
Reddit WSB + Google Trends + 7일치 뉴스 기록 → GPT 분석 → TOP 10
"""

import json
import os
import re
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict
import requests

# Reddit & Google Trends
try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    print("⚠️ Reddit 라이브러리 없음 - Reddit 분석 스킵")

try:
    from pytrends.request import TrendReq
    TRENDS_AVAILABLE = True
except ImportError:
    TRENDS_AVAILABLE = False
    print("⚠️ Google Trends 라이브러리 없음 - Trends 분석 스킵")


class WeeklyHotNewsAnalyzer:
    def __init__(self, openai_api_key: str, sent_news_file: str):
        self.openai_api_key = openai_api_key
        self.sent_news_file = sent_news_file
        
        # Reddit 설정 (환경 변수에서 가져오기)
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
    def _load_weekly_news_history(self) -> List[Dict]:
        """지난 7일간 전송된 뉴스 기록 로드"""
        try:
            if not os.path.exists(self.sent_news_file):
                print("⚠️ 뉴스 기록 파일 없음")
                return []
            
            with open(self.sent_news_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # 7일 전 날짜 계산
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            # 7일 이내 뉴스만 필터링
            weekly_news = [
                news for news in history.get('sent_news', [])
                if news.get('sent_at', '') > seven_days_ago.isoformat()
            ]
            
            print(f"📊 지난 7일간 전송된 뉴스: {len(weekly_news)}개")
            return weekly_news
            
        except Exception as e:
            print(f"⚠️ 뉴스 기록 로드 실패: {e}")
            return []
    
    def get_reddit_wsb_hot_tickers(self, limit: int = 100) -> Dict[str, int]:
        """Reddit r/wallstreetbets에서 핫한 티커 추출"""
        if not REDDIT_AVAILABLE:
            print("⚠️ Reddit 라이브러리 없음 - 스킵")
            return {}
        
        if not self.reddit_client_id or not self.reddit_client_secret:
            print("⚠️ Reddit API 키 없음 - 스킵")
            return {}
        
        try:
            print(f"\n🔍 Reddit r/wallstreetbets 분석 중...")
            
            reddit = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent='US Stock Bot v1.0'
            )
            
            ticker_counts = Counter()
            ticker_contexts = {}  # 티커별 대표 제목 저장
            
            # 공통 단어 필터 (티커 아닌 것들)
            common_words = {
                'TO', 'FOR', 'THE', 'AND', 'OR', 'BUT', 'NOT', 'ARE', 'WAS',
                'HAS', 'HAD', 'CAN', 'ALL', 'NEW', 'NOW', 'OUT', 'ANY', 'WHO',
                'HOW', 'WHY', 'GET', 'GOT', 'SEE', 'SAW', 'WAY', 'OUR', 'YOU',
                'YOUR', 'WILL', 'WOULD', 'COULD', 'SHOULD', 'MAY', 'MIGHT',
                'BEEN', 'BEING', 'HAVE', 'HIS', 'HER', 'ITS', 'THEIR', 'THERE',
                'WHAT', 'WHEN', 'WHERE', 'WHICH', 'THIS', 'THAT', 'THESE', 'THOSE',
                'FROM', 'WITH', 'INTO', 'OVER', 'AFTER', 'BEFORE', 'ABOUT',
                'AGAINST', 'BETWEEN', 'DURING', 'WITHOUT', 'THROUGH', 'THAN',
                'USA', 'CEO', 'IPO', 'ETF', 'WSB', 'YOLO', 'DD', 'TA', 'IMO'
            }
            
            # Hot 포스트 가져오기
            subreddit = reddit.subreddit('wallstreetbets')
            hot_posts = subreddit.hot(limit=limit)
            
            for post in hot_posts:
                # 티커 패턴: $TSLA 또는 TSLA (대문자 2-5글자)
                text = post.title + " " + post.selftext
                tickers = re.findall(r'\$?([A-Z]{2,5})\b', text)
                
                # 필터링
                valid_tickers = [
                    t for t in tickers 
                    if t not in common_words and t.isalpha()
                ]
                
                # 카운트 증가
                for ticker in valid_tickers:
                    ticker_counts[ticker] += 1
                    
                    # 대표 제목 저장 (upvote 높은 것)
                    if ticker not in ticker_contexts or post.score > ticker_contexts[ticker]['score']:
                        ticker_contexts[ticker] = {
                            'title': post.title,
                            'score': post.score,
                            'url': f"https://reddit.com{post.permalink}"
                        }
            
            # 상위 티커만 반환
            top_tickers = dict(ticker_counts.most_common(20))
            
            print(f"✅ Reddit 분석 완료: {len(top_tickers)}개 티커 발견")
            for ticker, count in list(top_tickers.items())[:5]:
                print(f"   {ticker}: {count}회 언급")
            
            return {
                'tickers': top_tickers,
                'contexts': ticker_contexts
            }
            
        except Exception as e:
            print(f"⚠️ Reddit 분석 실패: {e}")
            return {}
    
    def get_google_trends_data(self, tickers: List[str]) -> Dict[str, int]:
        """Google Trends에서 주식 티커 검색량 확인"""
        if not TRENDS_AVAILABLE:
            print("⚠️ Google Trends 라이브러리 없음 - 스킵")
            return {}
        
        if not tickers:
            return {}
        
        try:
            print(f"\n📊 Google Trends 분석 중... ({len(tickers)}개 티커)")
            
            # 한 번에 최대 5개씩만 조회 가능
            pytrends = TrendReq(hl='en-US', tz=360)
            trends_data = {}
            
            # 5개씩 묶어서 처리
            for i in range(0, len(tickers), 5):
                batch = tickers[i:i+5]
                
                try:
                    # 지난 7일간 트렌드
                    pytrends.build_payload(batch, timeframe='now 7-d')
                    interest = pytrends.interest_over_time()
                    
                    if not interest.empty:
                        # 각 티커의 평균 관심도 (0-100)
                        for ticker in batch:
                            if ticker in interest.columns:
                                avg_interest = int(interest[ticker].mean())
                                trends_data[ticker] = avg_interest
                    
                    # Rate limit 방지
                    import time
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"⚠️ {batch} 트렌드 조회 실패: {e}")
                    continue
            
            print(f"✅ Google Trends 분석 완료: {len(trends_data)}개 티커")
            return trends_data
            
        except Exception as e:
            print(f"⚠️ Google Trends 분석 실패: {e}")
            return {}
    
    def analyze_weekly_hot_news(self) -> List[Dict]:
        """주간 핫 뉴스 TOP 10 분석"""
        print(f"\n{'='*60}")
        print(f"🔥 주간 핫 뉴스 TOP 10 분석 시작")
        print(f"{'='*60}\n")
        
        # 1. 지난 7일 뉴스 기록 로드
        weekly_news = self._load_weekly_news_history()
        
        if not weekly_news:
            print("❌ 분석할 뉴스가 없습니다.")
            return []
        
        # 2. Reddit WSB 분석
        reddit_data = self.get_reddit_wsb_hot_tickers(limit=100)
        wsb_tickers = reddit_data.get('tickers', {}) if reddit_data else {}
        wsb_contexts = reddit_data.get('contexts', {}) if reddit_data else {}
        
        # 3. Google Trends 분석 (상위 20개 티커만)
        top_tickers = list(wsb_tickers.keys())[:20] if wsb_tickers else []
        trends_data = self.get_google_trends_data(top_tickers)
        
        # 4. GPT에게 종합 분석 요청
        print(f"\n🤖 GPT-4o-mini로 종합 분석 중...\n")
        
        # 뉴스 데이터 준비
        news_summary = "\n\n".join([
            f"[{idx+1}] {news.get('title', '')}\n요약: {news.get('summary', '')[:200]}\n발송: {news.get('sent_at', '')[:10]}"
            for idx, news in enumerate(weekly_news[:100])  # 최대 100개
        ])
        
        # Reddit 데이터 준비
        reddit_summary = ""
        if wsb_tickers:
            reddit_summary = "Reddit r/wallstreetbets 핫 티커:\n"
            for ticker, count in list(wsb_tickers.items())[:15]:
                context = wsb_contexts.get(ticker, {})
                trend = trends_data.get(ticker, 0)
                reddit_summary += f"- {ticker}: {count}회 언급"
                if trend > 0:
                    reddit_summary += f" | Google 검색: {trend}/100"
                if context:
                    reddit_summary += f"\n  대표글: {context.get('title', '')[:80]}"
                reddit_summary += "\n"
        
        # GPT 프롬프트
        prompt = f"""당신은 금융 뉴스 전문 애널리스트입니다.

지난 7일간의 미국 주식 뉴스와 소셜 데이터를 종합 분석하여 **주간 핫 이슈 TOP 10**을 선정해주세요.

**지난 7일간 전송된 뉴스** ({len(weekly_news)}개):
{news_summary}

**소셜 미디어 분석**:
{reddit_summary if reddit_summary else "소셜 데이터 없음"}

---

**선정 기준** (우선순위):
1. **반복 등장 주제**: 여러 날에 걸쳐 반복된 이슈 (예: 엔비디아가 월/수/금 등장)
2. **Reddit 화제성**: WSB에서 많이 언급된 종목/이슈
3. **Google 검색 트렌드**: 검색량이 높은 종목
4. **시장 영향도**: 지수, 섹터, 거시경제에 큰 영향
5. **투자자 관심도**: 실적, M&A, 규제 등 중요 이벤트

**제외 기준**:
- 일회성 소규모 뉴스
- 반복 없는 단발성 이슈
- Reddit 밈/농담 성격

**응답 형식** (JSON만):
{{
  "weekly_hot_topics": [
    {{
      "rank": 1,
      "title": "주제/종목명 (한국어)",
      "summary": "이번 주 무슨 일이 있었는지 3-4문장 종합 요약 (한국어)",
      "frequency": "3일 등장" 또는 "Reddit 234회" 등,
      "heat_score": 95,
      "related_tickers": ["NVDA", "AMD"]
    }}
  ]
}}

**중요**: 
- 제목과 요약은 반드시 한국어로 작성
- TOP 10개만 선정
- heat_score는 종합 점수 (1-100)
- 점수 순으로 정렬

JSON만 출력하세요."""

        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o',  # GPT-4o 사용 (주간 분석)
                    'messages': [
                        {'role': 'system', 'content': '당신은 금융 뉴스 분석 전문가입니다. JSON 형식으로만 응답하세요.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 3000
                },
                timeout=120  # GPT-4o 타임아웃
            )
            
            if response.status_code != 200:
                print(f"❌ GPT 분석 실패: {response.status_code}")
                return []
            
            result = response.json()
            response_text = result['choices'][0]['message']['content']
            
            # JSON 추출
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            analysis = json.loads(response_text)
            hot_topics = analysis.get('weekly_hot_topics', [])
            
            print(f"✅ 주간 핫 뉴스 TOP {len(hot_topics)}개 선정 완료\n")
            
            # 결과 출력
            for topic in hot_topics[:5]:
                print(f"   {topic['rank']}. {topic['title']} (점수: {topic.get('heat_score', 0)})")
            
            return hot_topics
            
        except Exception as e:
            print(f"❌ GPT 분석 오류: {e}")
            return []


def main():
    """테스트용 메인 함수"""
    openai_api_key = os.getenv('OPENAI_API_KEY')
    sent_news_file = '/data/sent_news_history.json' if os.path.exists('/data') else 'sent_news_history.json'
    
    if not openai_api_key:
        print("❌ OPENAI_API_KEY 환경 변수가 필요합니다.")
        return
    
    analyzer = WeeklyHotNewsAnalyzer(openai_api_key, sent_news_file)
    hot_topics = analyzer.analyze_weekly_hot_news()
    
    if hot_topics:
        print("\n" + "="*60)
        print("🔥 주간 핫 뉴스 TOP 10")
        print("="*60 + "\n")
        
        for topic in hot_topics:
            print(f"{topic['rank']}. {topic['title']}")
            print(f"   {topic['summary']}")
            print(f"   빈도: {topic.get('frequency', 'N/A')} | 점수: {topic.get('heat_score', 0)}")
            if topic.get('related_tickers'):
                print(f"   관련: {', '.join(topic['related_tickers'])}")
            print()


if __name__ == "__main__":
    main()
