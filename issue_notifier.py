import requests
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import threading

# .env 불러오기
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
} if GITHUB_TOKEN else {}

# 감시할 외부 레포
REPOS = {
    "MING9UCCI/issue-notifier": "Python"
    # "oss2025hnu/reposcore-py": "Python",
    # "oss2025hnu/reposcore-js": "JavaScript"
}

# 이미 감지한 이슈 추적
seen_issue_ids = set()

# 루프 종료 여부
running = True


def send_to_discord(lang: str, issue: dict):
    issue_title = issue.get("title", "제목 없음")
    issue_number = issue.get("number")
    issue_url = issue["html_url"]
    author = issue["user"]["login"]
    avatar_url = issue["user"]["avatar_url"]
    repo_name = issue["repository_url"].split("/")[-1]

    # 생성 시각 (KST)
    created_at = issue.get("created_at")
    if created_at:
        created_at_dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        kst_time = created_at_dt + timedelta(hours=9)
        created_at_str = kst_time.strftime("%Y-%m-%d %H:%M KST")
    else:
        created_at_str = "알 수 없음"

    # 알림 시각 (KST)
    sent_at_str = (datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S KST")

    # 라벨 목록
    labels = [label["name"] for label in issue.get("labels", [])]
    label_text = ", ".join(labels) if labels else "없음"

    # 본문 요약
    body = issue.get("body", "")
    body_preview = (body[:200] + "...") if body and len(body) > 200 else body or "내용 없음"

    embed = {
        "title": f"🛠️ 새 이슈 - {repo_name} #{issue_number}",
        "description": f"**{issue_title}**",
        "color": 0x00b0f4,
        "thumbnail": {
            "url": avatar_url
        },
        "fields": [
            {
                "name": "작성자",
                "value": author,
                "inline": True
            },
            {
                "name": "작성 시각",
                "value": created_at_str,
                "inline": True
            },
            {
                "name": "📎 라벨",
                "value": label_text,
                "inline": False
            },
            {
                "name": "📄 본문 요약",
                "value": body_preview,
                "inline": False
            },
            {
                "name": "🔗 링크",
                "value": f"[이슈 바로가기]({issue_url})",
                "inline": False
            }
        ],
        "footer": {
            "text": f"알림 시각: {sent_at_str}"
        }
    }

    payload = {
        "embeds": [embed]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"[ERROR] 디스코드 전송 실패: {response.status_code} - {response.text}")


def check_issues(repo: str, lang: str):
    url = f"https://api.github.com/repos/{repo}/issues"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        issues = response.json()
        for issue in issues:
            if "pull_request" in issue:
                continue
            if issue["id"] not in seen_issue_ids:
                seen_issue_ids.add(issue["id"])
                send_to_discord(lang, issue)
    else:
        print(f"[ERROR] {repo} 이슈 확인 실패: {response.status_code}")


def watcher_loop():
    global running
    print(f"[START] GitHub 이슈 감시 시작: {datetime.now()}")
    while running:
        for repo, lang in REPOS.items():
            check_issues(repo, lang)
        time.sleep(60)


def input_listener():
    global running
    while True:
        command = input().strip().lower()
        if command in ["quit", "exit"]:
            print("[STOP] 프로그램 종료 중...")
            running = False
            break


if __name__ == "__main__":
    watcher_thread = threading.Thread(target=watcher_loop)
    watcher_thread.start()
    input_listener()
    watcher_thread.join()
    print("[DONE] 종료 완료.")
