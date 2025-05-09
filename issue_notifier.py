import requests
import os
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# .env 불러오기
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_ISSUE_WEBHOOK_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
} if GITHUB_TOKEN else {}

# 감시할 외부 레포
REPOS = {
    "MING9UCCI/issue-notifier": "Python",
    "oss2025hnu/reposcore-py": "Python",
    "oss2025hnu/reposcore-js": "JavaScript"
}

# 이미 감지한 이슈 추적
seen_issue_ids = set()

# 서버 실행 시 기준 시각 (UTC)
base_time = datetime.now(timezone.utc)

# 📄 로그 출력 함수
def log(message: str, level: str = "INFO"):
    now = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
    tag = {
        "INFO": "ℹ️",
        "NEW": "🆕",
        "ERROR": "❌",
        "START": "🚀"
    }.get(level.upper(), "🔹")
    print(f"[{now}] {tag} [{level.upper()}] {message}")


def send_to_discord(lang: str, issue: dict):
    issue_title = issue.get("title", "제목 없음")
    issue_number = issue.get("number")
    issue_url = issue["html_url"]
    author = issue["user"]["login"]
    avatar_url = issue["user"]["avatar_url"]
    repo_name = issue["repository_url"].split("/")[-1]

    created_at = issue.get("created_at")
    if created_at:
        created_at_dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        kst_time = created_at_dt + timedelta(hours=9)
        created_at_str = kst_time.strftime("%Y-%m-%d %H:%M KST")
    else:
        created_at_str = "알 수 없음"

    sent_at_str = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S KST")

    labels = [label["name"] for label in issue.get("labels", [])]
    label_text = ", ".join(labels) if labels else "없음"

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
        log(f"디스코드 전송 실패: {response.status_code} - {response.text}", "ERROR")


def check_github_issues():
    for repo, lang in REPOS.items():
        url = f"https://api.github.com/repos/{repo}/issues"
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            issues = response.json()
            for issue in issues:
                if "pull_request" in issue:
                    continue

                created_at = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if created_at <= base_time:
                    continue

                if issue["id"] not in seen_issue_ids:
                    seen_issue_ids.add(issue["id"])
                    log(f"{repo}에서 새 이슈 발견: #{issue['number']} - {issue['title']}", "NEW")
                    send_to_discord(lang, issue)
        else:
            log(f"{repo} 이슈 확인 실패: {response.status_code}", "ERROR")


def run_issue_watcher():
    log("GitHub 이슈 감시 시작", "START")
    while True:
        check_github_issues()
        time.sleep(60)  # 1분마다 확인


if __name__ == "__main__":
    log("Server (non-interactive) 모드 실행 중", "INFO")
    run_issue_watcher()
