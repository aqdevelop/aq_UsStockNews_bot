#!/usr/bin/env python3
"""
텔레그램 이미지 File ID 확인 스크립트
봇에게 보낸 이미지의 file_id를 가져옵니다
"""

import requests
import sys
import json

def get_photo_file_id(bot_token):
    """텔레그램에 업로드된 사진의 file_id 가져오기"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    print("📸 이미지 File ID 확인 중...\n")
    print("📱 먼저 봇에게 이미지를 보내주세요!\n")
    print("⏳ 3초 대기...\n")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 오류: {response.status_code}")
            print(f"   Bot Token이 올바른지 확인해주세요.")
            return
        
        data = response.json()
        
        if not data.get('result'):
            print("❌ 메시지가 없습니다.")
            print("   봇에게 이미지를 보낸 후 다시 실행해주세요.")
            return
        
        # 최근 메시지들 역순으로 검색
        for update in reversed(data['result']):
            message = update.get('message', {})
            
            # 사진이 있는 메시지 찾기
            if 'photo' in message:
                # 가장 큰 사이즈의 사진 선택 (마지막 요소)
                photo = message['photo'][-1]
                file_id = photo['file_id']
                file_size = photo.get('file_size', 0)
                width = photo.get('width', 0)
                height = photo.get('height', 0)
                
                print("✅ 이미지 발견!\n")
                print(f"📋 File ID:")
                print(f"   {file_id}\n")
                print(f"📏 이미지 정보:")
                print(f"   크기: {width}x{height}")
                print(f"   용량: {file_size / 1024:.1f} KB\n")
                print("🔧 Railway 환경 변수 설정:")
                print(f"   HEADER_IMAGE_URL={file_id}\n")
                print("💡 이 File ID를 복사해서 HEADER_IMAGE_URL에 붙여넣으세요!")
                return
        
        print("❌ 이미지를 찾을 수 없습니다.")
        print("   봇에게 이미지를 보낸 후 다시 실행해주세요.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("=" * 60)
        print("📸 텔레그램 이미지 File ID 확인 도구")
        print("=" * 60)
        print("\n사용법:")
        print("  python get_image_file_id.py <BOT_TOKEN>\n")
        print("예시:")
        print("  python get_image_file_id.py 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n")
        print("=" * 60)
        sys.exit(1)
    
    bot_token = sys.argv[1]
    get_photo_file_id(bot_token)
