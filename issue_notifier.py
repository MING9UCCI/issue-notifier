import requests
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
} if GITHUB_TOKEN else {}

# 감시할 외부 레포
REPOS = {
    "MING9UCCI/issue-notifier" : "Python"
    # "oss2025hnu/reposcore-py": "Python",
    # "oss2025hnu/reposcore-js": "JavaScript"
}

# 중복 알림 방지용
seen_issue_ids = set()

def send_to_discord(lang: str, issue: dict):
    message = (
        f"<{lang}> 이슈입니다.\n"
        f"작성자 : {issue['user']['login']}\n"
        f"이슈 제목 : {issue['title']}\n"
        f"{issue['html_url']}"
    )
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
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

def main():
    print(f"[START] GitHub 이슈 감시 시작: {datetime.now()}")
    while True:
        for repo, lang in REPOS.items():
            check_issues(repo, lang)
        time.sleep(60)  # 1분마다 감시

if __name__ == "__main__":
    main()
