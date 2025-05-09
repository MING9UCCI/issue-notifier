# menu_notifier.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import schedule
import time
from dotenv import load_dotenv

load_dotenv()
MENU_WEBHOOK_URL = os.getenv("DISCORD_MENU_WEBHOOK_URL")

TARGET_URL = "https://my.hnu.kr/html/main/sso.html"

def fetch_menu(menu_type="lunch"):
    try:
        res = requests.get(TARGET_URL, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        menu_list = soup.select_one(f"ul.{menu_type}")
        if not menu_list:
            return None
        items = [li.text.strip() for li in menu_list.find_all("li") if li.text.strip() and li.text.strip() != "-"]
        return items
    except Exception as e:
        print(f"[ERROR] 메뉴 크롤링 실패: {e}")
        return None

def send_menu_to_discord(meal_type):
    items = fetch_menu(meal_type)
    if not items:
        return

    emoji = "🍱" if meal_type == "lunch" else "🍽️"
    title = "점심 메뉴" if meal_type == "lunch" else "저녁 메뉴"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    embed = {
        "title": f"{emoji} 오늘의 {title}",
        "description": "\n".join(f"- {item}" for item in items),
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
    schedule.every().day.at("11:00").do(lambda: send_menu_to_discord("lunch"))
    schedule.every().day.at("17:00").do(lambda: send_menu_to_discord("dinner"))