#!/usr/bin/env python3
"""
해외주식 뉴스 자동 전송 스케줄러
- 오전 7시 (한국시간): 미국 장 마감 후 뉴스
- 오후 10시 30분 (한국시간): 미국 장 시작 전후 뉴스

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

# 환경 변수 로드
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HEADER_IMAGE_URL = os.getenv('HEADER_IMAGE_URL')

def send_morning_news():
    """오전 7시 (KST) - 미국 장 마감 후 뉴스"""
    print(f"\n{'='*60}")
    print(f"☀️ 오전 7시 미국주식 모닝브리프 전송 시작")
    print(f"   시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
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

def send_evening_news():
    """오후 10시 30분 (KST) - 미국 장 시작 전후 뉴스"""
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
        sys.exit(1)
    
    print("🤖 해외주식 뉴스 봇 스케줄러 시작")
    print(f"⏰ 예정된 전송 시간 (한국시간 기준):")
    print(f"   - 오전 7시: 미국 장 마감 후 뉴스")
    print(f"     (미국 동부: 섬머타임 시 오후 6시 / 동절기 시 오후 5시)")
    print(f"   - 오후 10시 30분: 미국 장 시작 전후 뉴스")
    print(f"     (미국 동부: 섬머타임 시 오전 9시 30분 / 동절기 시 오전 8시 30분)")
    print(f"\n현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # 스케줄 등록 - 한국시간 기준
    schedule.every().day.at("07:00").do(send_morning_news)
    schedule.every().day.at("22:30").do(send_evening_news)
    
    print("✅ 스케줄 등록 완료. 대기 중...\n")
    
    # 무한 루프로 스케줄 실행
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 스케줄러 종료")
        sys.exit(0)
