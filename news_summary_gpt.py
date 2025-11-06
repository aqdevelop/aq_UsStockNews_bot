#!/usr/bin/env python3
"""
해외주식 뉴스 12시간 요약본 생성 (GPT-4o-mini 버전)
중요한 뉴스 10개를 한 글로 모아서 텔레그램에 전송
"""

import feedparser
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os
import sys

# Railway 로깅을 위한 버퍼링 비활성화
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

class USStockNewsSummary:
    def __init__(self, telegram_token: str, telegram_chat_id: str, openai_api_key: str, news_priority: str = 'general'):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.openai_api_key = openai_api_key
        self.news_priority = news_priority  # 'general', 'tech', 'macro' 등
        
        # 전송 기록 파일 경로 - Railway Volume 사용
        volume_path = '/data/sent_news_history.json'
        local_path = 'sent_news_history.json'
        
        # /data 디렉토리가 있으면 Volume 사용, 없으면 로컬 사용
        if os.path.exists('/data'):
            self.sent_news_file = volume_path
            print("📁 Railway Volume 사용: /data/sent_news_history.json")
        else:
            self.sent_news_file = local_path
            print("📁 로컬 파일 사용: sent_news_history.json")
        
        # 해외주식 RSS 피드 소스
        self.rss_feeds = {
            # 종합 뉴스
            'MarketWatch': 'https://www.marketwatch.com/rss/topstories',
            'Reuters Business': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
            'Bloomberg Markets': 'https://feeds.bloomberg.com/markets/news.rss',
            'CNBC Top News': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
            'Investing.com': 'https://www.investing.com/rss/news.rss',
            
            # 기술주/스타트업
            'TechCrunch': 'https://techcrunch.com/feed/',
            'The Verge': 'https://www.theverge.com/rss/index.xml',
            
            # 거시경제
            'Financial Times': 'https://www.ft.com/?format=rss',
            'Wall Street Journal': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
            
            # 한국 해외주식 뉴스
            '연합인포맥스': 'https://news.einfomax.co.kr/news/rss.xml',
            '서울경제': 'https://www.sedaily.com/RSS/S01.xml',
            '한국경제': 'https://www.hankyung.com/feed/economy',
        }
    
    def _load_sent_news_history(self) -> Dict:
        """전송 기록 불러오기"""
        try:
            if os.path.exists(self.sent_news_file):
                with open(self.sent_news_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 전송 기록 로드 실패: {e}")
        return {'sent_news': []}
    
    def _save_sent_news_history(self, history: Dict):
        """전송 기록 저장"""
        try:
            with open(self.sent_news_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 전송 기록 저장 실패: {e}")
    
    def _clean_old_history(self, history: Dict, days: int = 7) -> Dict:
        """N일 이전 기록 삭제"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        cleaned = {
            'sent_news': [
                news 
                for news in history.get('sent_news', []) 
                if news.get('sent_at', '') > cutoff_str
            ]
        }
        
        removed_count = len(history.get('sent_news', [])) - len(cleaned['sent_news'])
        if removed_count > 0:
            print(f"🗑️ {removed_count}개의 오래된 기록 삭제 (7일 이상)")
        
        return cleaned
    
    def _check_duplicate_by_similarity(self, new_news_list: List[Dict], history: Dict) -> List[Dict]:
        """GPT를 사용하여 유사한 주제의 뉴스 필터링"""
        if not history.get('sent_news'):
            print("📝 전송 기록 없음 - 중복 체크 생략")
            return new_news_list
        
        # 최근 전송한 뉴스 정보 (제목 + 요약)
        past_news_summary = "\n\n".join([
            f"[과거 뉴스 {idx+1}] 제목: {news.get('title', '')}\n요약: {news.get('summary', '')[:200]}"
            for idx, news in enumerate(history['sent_news'][-30:])  # 최근 30개만
        ])
        
        # 새로운 뉴스 정보
        new_news_summary = "\n\n".join([
            f"[새 뉴스 {idx+1}] 제목: {news.get('title', '')}\n요약: {news.get('summary', '')[:200]}"
            for idx, news in enumerate(new_news_list[:50])  # 최대 50개
        ])
        
        prompt = f"""다음은 최근 7일 이내에 이미 전송된 뉴스들입니다:

{past_news_summary}

---

다음은 이번에 전송하려는 새로운 뉴스들입니다:

{new_news_summary}

---

**작업**: 새로운 뉴스 중에서 과거 뉴스와 **주제나 내용이 유사한 뉴스**를 찾아주세요.

**판단 기준**:
1. 같은 사건/이슈를 다루는 경우 (예: "테슬라 CEO 인터뷰" 관련 뉴스들)
2. 같은 기업/인물에 대한 동일한 소식 (예: 같은 실적, 같은 발표)
3. 같은 주가/지수에 대한 동일한 변동 뉴스
4. 단순히 키워드가 겹치는 것이 아니라, **핵심 내용이 중복**되는 경우만

**중요**: 
- 같은 기업/인물이 나와도 **다른 사건**이면 중복 아님
- 주가 뉴스는 **같은 날짜, 같은 가격대**만 중복
- 후속 보도나 새로운 진전이 있으면 중복 아님

**응답 형식** (JSON만):
{{
  "duplicate_news_numbers": [2, 5, 7]  // 중복인 새 뉴스 번호들 (없으면 빈 배열)
}}

JSON만 출력하세요."""

        try:
            print(f"🤖 GPT로 중복 주제 검사 중... (새 뉴스 {len(new_news_list[:50])}개 vs 과거 {len(history['sent_news'][-30:])}개)")
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': [
                        {'role': 'system', 'content': '당신은 뉴스 중복 검사 전문가입니다. JSON 형식으로만 응답하세요.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.2,
                    'max_tokens': 500
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"⚠️ GPT 중복 검사 실패: {response.status_code}")
                return new_news_list
            
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
            
            duplicate_check = json.loads(response_text)
            duplicate_numbers = duplicate_check.get('duplicate_news_numbers', [])
            
            if duplicate_numbers:
                print(f"🔄 유사 주제 발견: {len(duplicate_numbers)}개 뉴스 제거")
                # 중복 번호에 해당하지 않는 뉴스만 반환
                filtered = [
                    news for idx, news in enumerate(new_news_list[:50]) 
                    if (idx + 1) not in duplicate_numbers
                ]
                filtered.extend(new_news_list[50:])
                
                print(f"📊 중복 제거 후: {len(filtered)}개 뉴스")
                return filtered
            else:
                print(f"✅ 유사 주제 없음 - 모든 뉴스 유지")
                return new_news_list
            
        except Exception as e:
            print(f"⚠️ GPT 중복 검사 오류: {e}")
            return new_news_list
    
    def _mark_news_as_sent(self, news_list: List[Dict]):
        """뉴스를 전송됨으로 표시"""
        history = self._load_sent_news_history()
        history = self._clean_old_history(history)
        
        current_time = datetime.now().isoformat()
        
        for news in news_list:
            history['sent_news'].append({
                'title': news['title'],
                'link': news['link'],
                'summary': news['summary'],
                'sent_at': current_time
            })
        
        self._save_sent_news_history(history)
        print(f"✅ {len(news_list)}개 뉴스 전송 기록 저장")
    
    def fetch_rss_news(self, hours: int = 12) -> List[Dict]:
        """RSS 피드에서 뉴스 수집"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        all_news = []
        
        print(f"📰 뉴스 수집 시작 (최근 {hours}시간)")
        print(f"   기준 시간: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                print(f"🔍 {source_name} 수집 중...", end=" ")
                feed = feedparser.parse(feed_url)
                count = 0
                
                for entry in feed.entries[:30]:  # 최대 30개
                    try:
                        # 발행 시간 파싱
                        pub_date = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            pub_date = datetime(*entry.updated_parsed[:6])
                        
                        # 시간 필터
                        if pub_date and pub_date < cutoff_time:
                            continue
                        
                        # 제목과 링크 필수
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '').strip()
                        
                        if not title or not link:
                            continue
                        
                        # 요약문 (description 또는 summary)
                        summary = entry.get('summary', entry.get('description', ''))[:500]
                        
                        all_news.append({
                            'title': title,
                            'link': link,
                            'summary': summary,
                            'source': source_name,
                            'published': pub_date.isoformat() if pub_date else None
                        })
                        count += 1
                    
                    except Exception as e:
                        continue
                
                print(f"✅ {count}개")
            
            except Exception as e:
                print(f"❌ 실패: {e}")
        
        print(f"\n📊 총 수집: {len(all_news)}개 뉴스\n")
        
        # 중복 제거 (제목 기준)
        seen_titles = set()
        unique_news = []
        
        for news in all_news:
            title_lower = news['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_news.append(news)
        
        removed = len(all_news) - len(unique_news)
        if removed > 0:
            print(f"🔄 중복 제거: {removed}개 (제목 기준)")
        
        print(f"📊 최종 수집: {len(unique_news)}개 뉴스\n")
        
        # GPT 기반 유사 주제 필터링
        history = self._load_sent_news_history()
        filtered_news = self._check_duplicate_by_similarity(unique_news, history)
        
        return filtered_news
    
    def analyze_and_select_top_news(self, news_list: List[Dict], top_n: int = 10) -> List[Dict]:
        """GPT를 사용해 중요 뉴스 선별 및 요약"""
        if not news_list:
            return []
        
        # 뉴스 목록을 GPT에 전달할 형식으로 변환
        news_text = "\n\n".join([
            f"[뉴스 {idx+1}]\n제목: {news['title']}\n출처: {news['source']}\n링크: {news['link']}\n내용: {news['summary'][:300]}"
            for idx, news in enumerate(news_list[:100])  # 최대 100개
        ])
        
        prompt = f"""당신은 해외주식 투자자를 위한 뉴스 큐레이터입니다.

다음 뉴스들 중에서 **투자자에게 가장 중요한 {top_n}개**를 선별하고, 각 뉴스를 한국어로 2-3문장으로 요약해주세요.

**선별 기준** (우선순위):
1. 주요 기업의 실적, M&A, 신제품 발표
2. 연준(Fed) 금리, 경제지표, 거시경제 이슈
3. 규제 변화, 정책 발표
4. 주요 지수 급등락 및 시장 동향
5. 섹터별 중요 이슈 (기술, 금융, 에너지 등)

**제외 기준**:
- 단순 의견/분석 기사
- 소규모 기업 뉴스
- 중요도 낮은 루머성 기사

**뉴스 목록**:
{news_text}

**응답 형식** (JSON만):
{{
  "selected_news": [
    {{
      "news_number": 1,
      "title": "제목을 반드시 한국어로 번역",
      "summary": "2-3문장 한국어 요약",
      "importance_score": 95
    }}
  ]
}}

**중요**: 제목(title)은 반드시 한국어로 번역해서 작성하세요. 영문 제목 사용 금지.
중요도 순으로 정렬하여 JSON만 출력하세요."""

        try:
            print(f"🤖 GPT로 중요 뉴스 {top_n}개 선별 중...\n")
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': [
                        {'role': 'system', 'content': '당신은 금융 뉴스 전문 애널리스트입니다. JSON 형식으로만 응답하세요.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 2000
                },
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"❌ GPT 요청 실패: {response.status_code}")
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
            selected = analysis.get('selected_news', [])
            
            # 선별된 뉴스 매칭
            top_news = []
            for item in selected[:top_n]:
                news_idx = item['news_number'] - 1
                if 0 <= news_idx < len(news_list):
                    original_news = news_list[news_idx]
                    top_news.append({
                        'title': item['title'],
                        'summary': item['summary'],
                        'link': original_news['link'],
                        'source': original_news['source'],
                        'importance': item.get('importance_score', 0)
                    })
            
            print(f"✅ {len(top_news)}개 중요 뉴스 선별 완료\n")
            
            # 중요도순 정렬
            top_news.sort(key=lambda x: x.get('importance', 0), reverse=True)
            
            return top_news
        
        except Exception as e:
            print(f"❌ GPT 분석 오류: {e}")
            return []
    
    def format_summary_message(self, news_list: List[Dict], time_of_day: str = None) -> str:
        """텔레그램 메시지 포맷 (MarkdownV2)"""
        
        def escape_markdown(text: str) -> str:
            """MarkdownV2 특수문자 이스케이프"""
            special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in special_chars:
                text = text.replace(char, f'\\{char}')
            return text
        
        # 시간대 자동 판단
        if time_of_day is None:
            current_hour = datetime.now().hour
            time_of_day = 'morning' if current_hour < 12 else 'evening'
        
        # 헤더 설정
        if time_of_day == 'morning':
            header = "☀️ *미국주식 모닝브리프*"
            subheader = "미국 장 마감 후 주요 뉴스"
        else:
            header = "🌙 *미국주식 이브닝브리프*"
            subheader = "미국 장 시작 전후 주요 뉴스"
        
        today = datetime.now().strftime('%Y\\-%m\\-%d %H:%M KST')
        
        message = f"""{header}
_{subheader}_

📅 {today}

━━━━━━━━━━━━━━━━━━━━

"""
        
        # 뉴스 목록
        for idx, news in enumerate(news_list, 1):
            title = news['title']
            summary = news['summary']
            link = news['link']
            
            # 이스케이프 적용
            title_escaped = escape_markdown(title)
            summary_escaped = escape_markdown(summary)
            
            message += f"""{idx}\\. *{title_escaped}*
>{summary_escaped} [원문]({link})

"""
            
            # 마지막 뉴스가 아니면 빈 줄 추가
            if idx < len(news_list):
                message += "\n"
        
        # 푸터
        message += f"""━━━━━━━━━━━━━━━━━━━━
총 {len(news_list)}개 주요 뉴스

해외주식 & 매크로 소식 자동 포워딩 문의👇
📧 contact@aqresearch\\.com"""
        
        return message
    
    def send_telegram_message(self, message: str, photo_url: str = None):
        """텔레그램으로 메시지 전송 (이미지 포함 가능)"""
        
        # 1. 이미지가 있으면 이미지 + 텍스트를 한 메시지로 전송
        if photo_url:
            print(f"📸 헤더 이미지 + 뉴스 통합 전송 시도: {photo_url[:50]}...")
            
            photo_url_api = f"https://api.telegram.org/bot{self.telegram_token}/sendPhoto"
            
            max_caption_length = 1000
            
            if len(message) <= max_caption_length:
                # 짧으면 한 번에 전송
                if photo_url.startswith('http'):
                    photo_payload = {
                        'chat_id': self.telegram_chat_id,
                        'photo': photo_url,
                        'caption': message,
                        'parse_mode': 'MarkdownV2',
                        'disable_web_page_preview': True
                    }
                else:
                    photo_payload = {
                        'chat_id': self.telegram_chat_id,
                        'photo': photo_url,
                        'caption': message,
                        'parse_mode': 'MarkdownV2',
                        'disable_web_page_preview': True
                    }
                
                try:
                    response = requests.post(photo_url_api, json=photo_payload, timeout=30)
                    
                    if response.status_code == 200:
                        print("✅ 이미지 + 뉴스 통합 전송 성공")
                        return
                    else:
                        print(f"⚠️ 통합 전송 실패: {response.text}")
                        
                except Exception as e:
                    print(f"⚠️ 통합 전송 오류: {e}")
        
        # 2. 텍스트 메시지 전송
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
        if photo_url and len(message) <= 1000:
            return
        
        # 메시지가 너무 길면 분할 (4096자 제한)
        max_length = 4000
        
        if len(message) <= max_length:
            messages = [message]
        else:
            parts = message.split('\n\n')
            messages = []
            current = parts[0] + "\n\n"
            
            for part in parts[1:]:
                if len(current) + len(part) < max_length:
                    current += part + "\n\n"
                else:
                    messages.append(current)
                    current = part + "\n\n"
            
            if current:
                messages.append(current)
        
        for idx, msg in enumerate(messages):
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': msg,
                'parse_mode': 'MarkdownV2',
                'disable_web_page_preview': True
            }
            
            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    print(f"✅ 메시지 {idx+1}/{len(messages)} 전송 성공")
                else:
                    print(f"❌ 전송 실패: {response.text}")
            except Exception as e:
                print(f"❌ 전송 오류: {e}")
    
    def run(self, hours: int = 12, top_n: int = 10, header_image_url: str = None, time_of_day: str = None):
        """실행
        
        Args:
            hours: 수집할 뉴스 시간 범위
            top_n: 선별할 뉴스 개수
            header_image_url: 헤더 이미지 URL
            time_of_day: 'morning', 'evening', None (자동)
        """
        print(f"\n{'='*50}")
        print(f"🚀 해외주식 뉴스 {hours}시간 요약 시작 (GPT-4o-mini)")
        print(f"{'='*50}\n")
        
        # 1. 뉴스 수집
        news_list = self.fetch_rss_news(hours=hours)
        
        if not news_list:
            print("❌ 수집된 뉴스가 없습니다.")
            return
        
        # 2. 중요 뉴스 선별
        top_news = self.analyze_and_select_top_news(news_list, top_n=top_n)
        
        if not top_news:
            print("❌ 선별된 뉴스가 없습니다.")
            return
        
        # 3. 요약 메시지 생성
        summary = self.format_summary_message(top_news, time_of_day=time_of_day)
        
        # 4. 텔레그램 전송
        print("📤 텔레그램 전송 중...\n")
        self.send_telegram_message(summary, photo_url=header_image_url)
        
        # 5. 전송된 뉴스 기록
        self._mark_news_as_sent(top_news)
        
        print(f"\n{'='*50}")
        print(f"✅ 완료: {len(top_news)}개 뉴스 요약 전송")
        print(f"{'='*50}\n")

def main():
    """메인 실행 함수"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    header_image_url = os.getenv('HEADER_IMAGE_URL')
    
    if not all([telegram_token, telegram_chat_id, openai_api_key]):
        print("❌ 오류: 필요한 환경 변수가 설정되지 않았습니다.")
        print("\n다음 환경 변수를 설정해주세요:")
        print("  - TELEGRAM_BOT_TOKEN")
        print("  - TELEGRAM_CHAT_ID")
        print("  - OPENAI_API_KEY")
        print("  - HEADER_IMAGE_URL (선택사항)")
        return
    
    bot = USStockNewsSummary(
        telegram_token=telegram_token,
        telegram_chat_id=telegram_chat_id,
        openai_api_key=openai_api_key
    )
    
    # 12시간, 상위 10개 뉴스
    bot.run(hours=12, top_n=10, header_image_url=header_image_url)

if __name__ == "__main__":
    main()
