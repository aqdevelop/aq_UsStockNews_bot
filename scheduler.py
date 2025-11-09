#!/usr/bin/env python3
"""
해외주식 뉴스 자동 전송 스케줄러
- 평일: 오전 7시, 오후 10시 30분 (하루 2회)
- 토요일: 오전 7시만 (하루 1회)
- 일요일: 오전 7시 + 주간 핫 TOP 10 (특별판)

섬머타임 자동 반영:
- 섬머타임(3-11월): 한국 시간 - 13시간 = 미국 동부
- 동절기(11-3월): 한국 시간 - 14시간 = 미국 동부
"""

import schedule
import time
import os
import sys
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_summary_gpt import USStockNewsSummary
from weekly_hot_analyzer import WeeklyHotNewsAnalyzer
from monthly_hot_analyzer import MonthlyHotNewsAnalyzer

# 환경 변수 로드
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HEADER_IMAGE_URL = os.getenv('HEADER_IMAGE_URL')

def is_weekend():
    """주말(토요일, 일요일) 확인"""
    return datetime.now().weekday() >= 5  # 5=토요일, 6=일요일

def is_sunday():
    """일요일 확인"""
    return datetime.now().weekday() == 6

def is_first_of_month():
    """매월 1일 확인"""
    return datetime.now().day == 1

def send_morning_news():
    """오전 7시 (KST) - 미국 장 마감 후 뉴스"""
    print(f"\n{'='*60}")
    print(f"☀️ 오전 7시 미국주식 모닝브리프 전송 시작")
    print(f"   시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
    
    if is_weekend():
        print(f"   📅 주말 특별판")
    else:
        print(f"   📅 평일")
    
    print(f"   내용: 미국 장 마감 후 주요 뉴스")
    print(f"{'='*60}\n")
    
    bot = USStockNewsSummary(
        telegram_token=TELEGRAM_TOKEN,
        telegram_chat_id=TELEGRAM_CHAT_ID,
        openai_api_key=OPENAI_API_KEY,
        news_priority='general'
    )
    
    # time_of_day='morning' 명시
    bot.run(hours=12, top_n=10, header_image_url=HEADER_IMAGE_URL, time_of_day='morning')
    print("✅ 모닝브리프 전송 완료\n")
    
    # 일요일이면 주간 핫 뉴스도 전송
    if is_sunday():
        print(f"📅 일요일 특별 - 주간 핫 뉴스 전송 시작\n")
        time.sleep(5)  # 일반 뉴스와 5초 간격
        send_weekly_hot_news()
    
    # 매월 1일이면 월간 핫 뉴스도 전송
    if is_first_of_month():
        print(f"📅 매월 1일 특별 - 월간 핫 뉴스 전송 시작\n")
        time.sleep(10)  # 주간 뉴스 후 10초 대기
        send_monthly_hot_news()

def send_evening_news():
    """오후 10시 30분 (KST) - 미국 장 시작 전후 뉴스 (평일만)"""
    
    # 주말이면 전송하지 않음
    if is_weekend():
        print(f"\n{'='*60}")
        print(f"🌙 오후 10시 30분 - 주말이므로 이브닝브리프 생략")
        print(f"   시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
        print(f"{'='*60}\n")
        return
    
    print(f"\n{'='*60}")
    print(f"🌙 오후 10시 30분 미국주식 이브닝브리프 전송 시작")
    print(f"   시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
    print(f"   내용: 미국 장 시작 전후 주요 뉴스")
    print(f"{'='*60}\n")
    
    bot = USStockNewsSummary(
        telegram_token=TELEGRAM_TOKEN,
        telegram_chat_id=TELEGRAM_CHAT_ID,
        openai_api_key=OPENAI_API_KEY,
        news_priority='general'
    )
    
    # time_of_day='evening' 명시
    bot.run(hours=12, top_n=10, header_image_url=HEADER_IMAGE_URL, time_of_day='evening')
    print("✅ 이브닝브리프 전송 완료\n")

def send_weekly_hot_news():
    """주간 핫 뉴스 TOP 10 (일요일 오전 7시 직후)"""
    print(f"\n{'='*60}")
    print(f"🔥 주간 핫 뉴스 TOP 10 전송 시작 (GPT-4o)")
    print(f"   시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
    print(f"{'='*60}\n")
    
    # 주간 핫 뉴스 분석
    analyzer = WeeklyHotNewsAnalyzer(OPENAI_API_KEY, '/data/sent_news_history.json')
    hot_topics = analyzer.analyze_weekly_hot_news()
    
    if not hot_topics:
        print("⚠️ 분석 실패 또는 핫 뉴스 없음\n")
        return
    
    # 텔레그램 메시지 포맷팅
    def escape_markdown(text: str) -> str:
        """MarkdownV2 특수문자 이스케이프"""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    today = datetime.now().strftime('%Y\\-%m\\-%d')
    
    message = f"""🔥 *주간 핫 뉴스 TOP 10*
_한 주간 가장 화제였던 이슈_

📅 {today}

━━━━━━━━━━━━━━━━━━━━

"""
    
    for topic in hot_topics:
        rank = topic['rank']
        title = escape_markdown(topic['title'])
        summary = escape_markdown(topic['summary'])
        frequency = escape_markdown(topic.get('frequency', ''))
        heat_score = topic.get('heat_score', 0)
        tickers = topic.get('related_tickers', [])
        
        message += f"""{rank}\\. *{title}*
>{summary}

"""
        
        # 추가 정보
        info_line = f"📊 {frequency}"
        if tickers:
            tickers_str = ', '.join(tickers[:3])  # 최대 3개만
            info_line += f" \\| 종목: {escape_markdown(tickers_str)}"
        message += f"_{info_line}_\n\n"
    
    # 푸터
    message += f"""━━━━━━━━━━━━━━━━━━━━
📌 Reddit WSB \\+ Google Trends \\+ GPT\\-4o 분석
🔄 지난 7일 뉴스 종합

해외주식 소식 자동 포워딩 문의👇
📧 contact@aqresearch\\.com"""
    
    # 텔레그램 전송
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'MarkdownV2',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ 주간 핫 뉴스 전송 완료\n")
        else:
            print(f"❌ 전송 실패: {response.text}\n")
    except Exception as e:
        print(f"❌ 전송 오류: {e}\n")

def send_monthly_hot_news():
    """월간 핫 뉴스 TOP 10 (매월 1일 오전 7시 직후)"""
    print(f"\n{'='*60}")
    print(f"📅 월간 핫 뉴스 TOP 10 전송 시작 (GPT-4o)")
    print(f"   시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
    print(f"{'='*60}\n")
    
    # 월간 핫 뉴스 분석
    analyzer = MonthlyHotNewsAnalyzer(OPENAI_API_KEY, '/data/sent_news_history.json')
    result = analyzer.analyze_monthly_hot_news()
    
    if not result or not result.get('hot_topics'):
        print("⚠️ 분석 실패 또는 핫 뉴스 없음\n")
        return
    
    # 텔레그램 메시지 포맷팅
    def escape_markdown(text: str) -> str:
        """MarkdownV2 특수문자 이스케이프"""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    current_month = datetime.now().strftime('%Y년 %m월')
    monthly_summary = result.get('monthly_summary', '')
    market_mood = result.get('market_mood', '')
    hot_topics = result.get('hot_topics', [])
    
    message = f"""📅 *{escape_markdown(current_month)} 월간 핫 뉴스 TOP 10*
_한 달간 가장 중요했던 이슈_

📝 {escape_markdown(monthly_summary)}
📊 시장 분위기: {escape_markdown(market_mood)}

━━━━━━━━━━━━━━━━━━━━

"""
    
    for topic in hot_topics:
        rank = topic['rank']
        title = escape_markdown(topic['title'])
        summary = escape_markdown(topic['summary'])
        impact = topic.get('impact', '')
        outlook = topic.get('outlook', '')
        tickers = topic.get('related_tickers', [])
        
        message += f"""{rank}\\. *{title}*
>{summary}

"""
        
        # 추가 정보
        info_parts = []
        if impact:
            impact_emoji = "🔴" if impact == "high" else "🟡"
            info_parts.append(f"{impact_emoji} {escape_markdown(impact.upper())}")
        if tickers:
            tickers_str = ', '.join(tickers[:3])
            info_parts.append(f"종목: {escape_markdown(tickers_str)}")
        
        if info_parts:
            message += f"_{' \\| '.join(info_parts)}_\n"
        
        if outlook:
            message += f"💡 _{escape_markdown(outlook)}_\n"
        
        message += "\n"
    
    # 푸터
    message += f"""━━━━━━━━━━━━━━━━━━━━
📌 GPT\\-4o 월간 심층 분석
🔄 지난 30일 뉴스 종합

해외주식 소식 자동 포워딩 문의👇
📧 contact@aqresearch\\.com"""
    
    # 텔레그램 전송
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # 메시지가 너무 길면 분할
    max_length = 4000
    if len(message) <= max_length:
        messages = [message]
    else:
        # 헤더와 푸터 분리
        header = message.split('━━━━━━━━━━━━━━━━━━━━\n\n')[0] + '━━━━━━━━━━━━━━━━━━━━\n\n'
        footer = '\n━━━━━━━━━━━━━━━━━━━━\n' + message.split('\n━━━━━━━━━━━━━━━━━━━━\n')[-1]
        
        # 뉴스 항목들
        topics_text = message.replace(header, '').replace(footer, '')
        topics_list = topics_text.split('\n\n')
        
        messages = []
        current = header
        for part in topics_list:
            if len(current) + len(part) + len(footer) < max_length:
                current += part + "\n\n"
            else:
                messages.append(current + footer)
                current = header + part + "\n\n"
        
        if current != header:
            messages.append(current + footer)
    
    # 전송
    for idx, msg in enumerate(messages):
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': msg,
            'parse_mode': 'MarkdownV2',
            'disable_web_page_preview': True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ 월간 핫 뉴스 {idx+1}/{len(messages)} 전송 완료")
            else:
                print(f"❌ 전송 실패: {response.text}")
        except Exception as e:
            print(f"❌ 전송 오류: {e}")
        
        # 여러 메시지 전송 시 간격
        if idx < len(messages) - 1:
            time.sleep(2)
    
    print()

def main():
    """스케줄러 메인"""
    
    # 환경 변수 확인
    if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, OPENAI_API_KEY]):
        print("❌ 오류: 필요한 환경 변수가 설정되지 않았습니다.")
        print("\n다음 환경 변수를 설정해주세요:")
        print("  - TELEGRAM_BOT_TOKEN")
        print("  - TELEGRAM_CHAT_ID")
        print("  - OPENAI_API_KEY")
        print("  - HEADER_IMAGE_URL (선택사항)")
        print("  - REDDIT_CLIENT_ID (선택사항, 주간 핫 뉴스용)")
        print("  - REDDIT_CLIENT_SECRET (선택사항, 주간 핫 뉴스용)")
        sys.exit(1)
    
    print("🤖 해외주식 뉴스 봇 스케줄러 시작")
    print(f"⏰ 예정된 전송 시간 (한국시간 기준):")
    print(f"   📅 평일:")
    print(f"      - 오전 7시: 미국 장 마감 후 뉴스")
    print(f"        (미국 동부: 섬머타임 시 오후 6시 / 동절기 시 오후 5시)")
    print(f"      - 오후 10시 30분: 미국 장 시작 전후 뉴스")
    print(f"        (미국 동부: 섬머타임 시 오전 9시 30분 / 동절기 시 오전 8시 30분)")
    print(f"   📅 토요일:")
    print(f"      - 오전 7시만: 주말 뉴스 요약")
    print(f"   📅 일요일:")
    print(f"      - 오전 7시: 주말 뉴스 요약")
    print(f"      - 오전 7시 직후: 🔥 주간 핫 TOP 10 (GPT-4o)")
    print(f"   📅 매월 1일:")
    print(f"      - 오전 7시: 일반 뉴스")
    print(f"      - 오전 7시 직후: 🔥 주간 핫 TOP 10 (GPT-4o) [일요일인 경우]")
    print(f"      - 오전 7시 직후: 📅 월간 핫 TOP 10 (GPT-4o)")
    print(f"\n현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
    print(f"오늘: {['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'][datetime.now().weekday()]}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # Reddit 설정 확인
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
    if reddit_id and reddit_secret:
        print("✅ Reddit API 설정됨 - WSB 분석 활성화")
    else:
        print("⚠️ Reddit API 미설정 - WSB 분석 비활성화 (선택사항)")
    print()
    
    # 스케줄 등록 - 한국시간 기준
    # 매일 오전 7시 (평일+주말, 일요일은 주간 핫 뉴스도 추가)
    schedule.every().day.at("07:00").do(send_morning_news)
    
    # 매일 오후 10시 30분 (함수 내부에서 주말 체크)
    schedule.every().day.at("22:30").do(send_evening_news)
    
    print("✅ 스케줄 등록 완료. 대기 중...\n")
    
    # 무한 루프로 스케줄 실행
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    import requests  # 여기서 import
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 스케줄러 종료")
        sys.exit(0)
