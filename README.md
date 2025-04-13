# 오픈소스 프로젝트 이슈 알리미 🔔
GitHub 저장소에 새로운 이슈가 등록되면 디스코드 Webhook으로 알림을 보내는 Python 기반 감시 봇입니다.


## 사용 방법
```bash
pip install -r requirements.txt
```


## .env 파일 생성
```bash
.env
```


### → 안에 Webhook 주소와 GitHub 토큰을 채워주세요
예시
```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/yyy
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxx
```


## 실행
python issue_notifier.py