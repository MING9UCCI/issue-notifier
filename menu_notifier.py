import requests
from datetime import datetime
import os
import schedule
from dotenv import load_dotenv
import urllib3

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
MENU_WEBHOOK_URL = os.getenv("DISCORD_MENU_WEBHOOK_URL")

def fetch_dormitory_menu():
    url = "https://my.hnu.kr/api/widget/internalWidget/selectSikdan"
    date = datetime.now().strftime("%Y%m%d")
    params = {
        "SIKDAN_DT": date,
        "SIKDANG_GB": "1"  # 생활관 식당
    }

    try:
        res = requests.get(url, params=params, timeout=10, verify=False)
        res.raise_for_status()
        data = res.json()

        lunch = None
        dinner = None

        for item in data:
            if item.get("SIKSA_GB") == "2":  # 점심
                lunch = item.get("MENU_NM", "메뉴 없음").strip().replace("\n", ", ")
            elif item.get("SIKSA_GB") == "3":  # 저녁
                dinner = item.get("MENU_NM", "메뉴 없음").strip().replace("\n", ", ")

        return lunch, dinner

    except Exception as e:
        print(f"[ERROR] 메뉴 가져오기 실패: {e}")
        return None, None

def send_menu_to_discord(meal_type, menu):
    if not menu:
        menu = "메뉴 정보 없음"

    emoji = "🍱" if meal_type == "lunch" else "🍽️"
    title = "점심 메뉴" if meal_type == "lunch" else "저녁 메뉴"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    embed = {
        "title": f"{emoji} 오늘의 {title}",
        "description": menu,
        "color": 0x5dade2,
        "footer": {"text": f"알림 시각: {now}"}
    }

    payload = {"embeds": [embed]}
    response = requests.post(MENU_WEBHOOK_URL, json=payload)

    if response.status_code != 204:
        print(f"[ERROR] 디스코드 전송 실패: {response.status_code} - {response.text}")
    else:
        print(f"[INFO] {title} 전송 성공!")

def schedule_menu_notifications():
    schedule.every().day.at("11:00").do(lambda: send_menu_to_discord("lunch", fetch_dormitory_menu()[0]))
    schedule.every().day.at("17:00").do(lambda: send_menu_to_discord("dinner", fetch_dormitory_menu()[1]))
