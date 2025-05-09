import threading
import schedule
import time

from issue_notifier import run_issue_watcher
from menu_notifier import schedule_menu_notifications

def start_scheduler_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("🚀 알림 봇 실행 시작!")

    # GitHub 이슈 감시 스레드
    threading.Thread(target=run_issue_watcher, daemon=True).start()

    # 식단 알림 스케줄 등록
    schedule_menu_notifications()

    # 스케줄 루프 실행
    start_scheduler_loop()
