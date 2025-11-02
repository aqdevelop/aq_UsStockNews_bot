#!/usr/bin/env python3
"""
텔레그램 Chat ID 확인 스크립트
"""

import requests
import sys

def get_chat_id(bot_token):
    """텔레그램 Chat ID 가져오기"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    print("🔍 Chat ID 확인 중...\n")
    print("📱 먼저 봇에게 아무 메시지나 보내주세요!\n")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 오류: {response.status_code}")
            print(f"   Bot Token이 올바른지 확인해주세요.")
            return
        
        data = response.json()
        
        if not data.get('result'):
            print("❌ 메시지가 없습니다.")
            print("   봇에게 아무 메시지나 보낸 후 다시 실행해주세요.")
            return
        
        # 가장 최근 메시지의 chat_id 추출
        chat_id = data['result'][-1]['message']['chat']['id']
        
        print("✅ Chat ID 확인 완료!\n")
        print(f"📋 당신의 Chat ID: {chat_id}\n")
        print("이 숫자를 TELEGRAM_CHAT_ID 환경변수로 사용하세요.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python get_chat_id.py <BOT_TOKEN>")
        print("\n예시:")
        print("python get_chat_id.py 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        sys.exit(1)
    
    bot_token = sys.argv[1]
    get_chat_id(bot_token)
