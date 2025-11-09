#!/usr/bin/env python3
"""
월간 핫 뉴스 분석기
지난 30일간의 뉴스 기록 → GPT-4o 분석 → 월간 TOP 10
매월 1일 한국시간 오전에 실행
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import requests


class MonthlyHotNewsAnalyzer:
    def __init__(self, openai_api_key: str, sent_news_file: str = '/data/sent_news_history.json'):
        self.openai_api_key = openai_api_key
        self.sent_news_file = sent_news_file
    
    def _load_monthly_news_history(self) -> List[Dict]:
        """지난 30일간 전송된 뉴스 기록 로드"""
        try:
            if not os.path.exists(self.sent_news_file):
                print("⚠️ 뉴스 기록 파일 없음")
                return []
            
            with open(self.sent_news_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # 30일 전 날짜 계산
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # 30일 이내 뉴스만 필터링
            monthly_news = [
                news for news in history.get('sent_news', [])
                if news.get('sent_at', '') > thirty_days_ago.isoformat()
            ]
            
            print(f"📊 지난 30일간 전송된 뉴스: {len(monthly_news)}개")
            return monthly_news
            
        except Exception as e:
            print(f"⚠️ 뉴스 기록 로드 실패: {e}")
            return []
    
    def analyze_monthly_hot_news(self) -> List[Dict]:
        """월간 핫 뉴스 TOP 10 분석 (GPT-4o 사용)"""
        print(f"\n{'='*60}")
        print(f"📅 월간 핫 뉴스 TOP 10 분석 시작 (GPT-4o)")
        print(f"{'='*60}\n")
        
        # 1. 지난 30일 뉴스 기록 로드
        monthly_news = self._load_monthly_news_history()
        
        if not monthly_news:
            print("❌ 분석할 뉴스가 없습니다.")
            return []
        
        if len(monthly_news) < 50:
            print(f"⚠️ 뉴스 개수가 적습니다 ({len(monthly_news)}개). 최소 50개 권장.")
        
        # 2. 뉴스 데이터 준비 (최대 300개)
        news_summary = "\n\n".join([
            f"[{idx+1}] {news.get('title', '')}\n요약: {news.get('summary', '')[:200]}\n날짜: {news.get('sent_at', '')[:10]}"
            for idx, news in enumerate(monthly_news[:300])
        ])
        
        # 3. GPT-4o 프롬프트
        current_month = datetime.now().strftime('%Y년 %m월')
        
        prompt = f"""당신은 월스트리트 저널 수준의 금융 애널리스트입니다.

지난 30일간 ({current_month}) 미국 주식 시장의 뉴스를 종합 분석하여 **월간 가장 중요했던 이슈 TOP 10**을 선정해주세요.

**지난 30일간 전송된 뉴스** ({len(monthly_news)}개):
{news_summary}

---

**선정 기준** (우선순위):
1. **시장 영향도**: S&P 500, 나스닥 등 주요 지수에 미친 영향
2. **지속성**: 한 달 내내 계속된 이슈 또는 여러 번 반복된 주제
3. **구조적 변화**: 산업, 정책, 기술의 근본적 변화
4. **투자자 관심도**: 실적, M&A, 규제 등 중대 사건
5. **거시경제**: 연준 정책, 인플레이션, 고용 등 매크로 이슈

**제외 기준**:
- 일회성 단기 이슈
- 소규모 기업의 단순 뉴스
- 중요도 낮은 밈/소문

**분석 관점**:
- 이번 달의 **가장 큰 흐름**은 무엇이었나?
- 어떤 종목/섹터가 **가장 주목**받았나?
- **투자 관점**에서 꼭 알아야 할 이슈는?
- 다음 달로 **이어질 가능성**이 높은 이슈는?

**응답 형식** (JSON만):
{{
  "monthly_summary": "이번 달 시장을 한 문장으로 요약 (한국어)",
  "market_mood": "낙관적/신중함/비관적 중 하나",
  "monthly_hot_topics": [
    {{
      "rank": 1,
      "title": "이슈 제목 (한국어)",
      "summary": "월간 관점에서 이 이슈가 왜 중요했는지, 무슨 일이 있었는지, 시장에 어떤 영향을 주었는지 4-5문장 상세 분석 (한국어)",
      "impact": "high/medium",
      "heat_score": 95,
      "related_tickers": ["NVDA", "AMD"],
      "outlook": "다음 달 전망 한 문장 (한국어)"
    }}
  ]
}}

**중요**: 
- 모든 텍스트는 반드시 한국어로 작성
- TOP 10개만 선정
- 월간 관점의 **심층 분석** 필수
- heat_score는 종합 점수 (1-100)
- 점수 순으로 정렬

JSON만 출력하세요."""

        try:
            print(f"🤖 GPT-4o로 월간 종합 분석 중... (최고 품질)\n")
            print(f"   분석 대상: {len(monthly_news)}개 뉴스")
            print(f"   예상 시간: 30-60초\n")
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o',  # GPT-4o 사용 (월간 분석)
                    'messages': [
                        {
                            'role': 'system', 
                            'content': '당신은 월스트리트 저널 수준의 금융 시장 전문 애널리스트입니다. 깊이 있는 분석과 통찰을 제공하세요. JSON 형식으로만 응답하세요.'
                        },
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.4,
                    'max_tokens': 4000  # 월간은 더 긴 분석
                },
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"❌ GPT-4o 분석 실패: {response.status_code}")
                print(f"   응답: {response.text}")
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
            
            monthly_summary = analysis.get('monthly_summary', '')
            market_mood = analysis.get('market_mood', '')
            hot_topics = analysis.get('monthly_hot_topics', [])
            
            print(f"✅ 월간 핫 뉴스 TOP {len(hot_topics)}개 선정 완료\n")
            print(f"📝 월간 요약: {monthly_summary}")
            print(f"📊 시장 분위기: {market_mood}\n")
            
            # 결과 출력
            for topic in hot_topics[:5]:
                print(f"   {topic['rank']}. {topic['title']} (점수: {topic.get('heat_score', 0)})")
            
            return {
                'monthly_summary': monthly_summary,
                'market_mood': market_mood,
                'hot_topics': hot_topics
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            print(f"   응답 내용: {response_text[:500]}")
            return []
        except Exception as e:
            print(f"❌ GPT-4o 분석 오류: {e}")
            return []


def main():
    """테스트용 메인 함수"""
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("❌ OPENAI_API_KEY 환경 변수가 필요합니다.")
        return
    
    analyzer = MonthlyHotNewsAnalyzer(openai_api_key)
    result = analyzer.analyze_monthly_hot_news()
    
    if result:
        print("\n" + "="*60)
        print(f"📅 {datetime.now().strftime('%Y년 %m월')} 월간 핫 뉴스 TOP 10")
        print("="*60 + "\n")
        
        print(f"📝 한 달 요약: {result['monthly_summary']}")
        print(f"📊 시장 분위기: {result['market_mood']}\n")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        for topic in result['hot_topics']:
            print(f"{topic['rank']}. {topic['title']}")
            print(f"   {topic['summary']}")
            print(f"   영향도: {topic.get('impact', 'N/A')} | 점수: {topic.get('heat_score', 0)}")
            if topic.get('related_tickers'):
                print(f"   관련: {', '.join(topic['related_tickers'])}")
            if topic.get('outlook'):
                print(f"   전망: {topic['outlook']}")
            print()


if __name__ == "__main__":
    main()
