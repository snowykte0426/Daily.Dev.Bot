import requests
import json
from datetime import datetime
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordSender:
    def __init__(self):
        self.config = Config()
        self.webhook_url = self.config.DISCORD_WEBHOOK_URL

    def create_embed(self, post, index):
        description_text = ""

        if post.get('content'):
            description_text = post.get('content', '')[:2000]
        elif post.get('description'):
            description_text = post.get('description', '')[:2000]

        embed = {
            "title": f"🔥 [{index + 1}] {post.get('title', 'Unknown Title')[:256]}",
            "url": post.get('link', ''),
            "description": description_text,
            "color": 0x7289da,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Daily.dev Bot • 본문 번역됨" if post.get('content') else "Daily.dev Bot",
                "icon_url": "https://daily.dev/favicon.ico"
            }
        }

        fields = []

        if post.get('tags') and len(post['tags']) > 0:
            fields.append({
                "name": "🏷️ 태그",
                "value": " • ".join(post['tags'][:5]),
                "inline": True
            })

        if post.get('content') and post.get('description'):
            fields.append({
                "name": "📝 요약",
                "value": post.get('description', '')[:1024],
                "inline": False
            })

        if fields:
            embed["fields"] = fields

        return embed

    def send_daily_posts(self, posts):
        try:
            if not self.webhook_url:
                logger.error("Discord 웹훅 URL이 설정되지 않았습니다.")
                return False

            if not posts:
                logger.warning("전송할 게시글이 없습니다.")
                return False

            header_embed = {
                "title": "📰 오늘의 Daily.dev 인기 게시글",
                "description": f"**{datetime.now().strftime('%Y년 %m월 %d일')}** 기준 상위 {len(posts)}개 게시글을 가져왔습니다! 🚀",
                "color": 0x3498db,
                "timestamp": datetime.utcnow().isoformat(),
                "thumbnail": {
                    "url": "https://daily.dev/favicon.ico"
                }
            }

            header_payload = {
                "embeds": [header_embed],
                "username": "Daily.dev Bot",
                "avatar_url": "https://daily.dev/favicon.ico"
            }

            response = requests.post(
                self.webhook_url,
                data=json.dumps(header_payload),
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code != 204:
                logger.error(f"헤더 메시지 전송 실패: {response.status_code}")

            for i, post in enumerate(posts):
                embed = self.create_embed(post, i)

                payload = {
                    "embeds": [embed],
                    "username": "Daily.dev Bot",
                    "avatar_url": "https://daily.dev/favicon.ico"
                }

                response = requests.post(
                    self.webhook_url,
                    data=json.dumps(payload),
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 204:
                    logger.info(f"게시글 {i + 1}/{len(posts)} 전송 완료")
                else:
                    logger.error(f"게시글 {i + 1} 전송 실패: {response.status_code} - {response.text}")

                import time
                time.sleep(1)

            footer_embed = {
                "description": "---\n✅ **모든 게시글 전송 완료!**\n더 많은 개발 소식은 [Daily.dev](https://daily.dev)에서 확인하세요!",
                "color": 0x27ae60,
                "timestamp": datetime.utcnow().isoformat()
            }

            footer_payload = {
                "embeds": [footer_embed],
                "username": "Daily.dev Bot",
                "avatar_url": "https://daily.dev/favicon.ico"
            }

            requests.post(
                self.webhook_url,
                data=json.dumps(footer_payload),
                headers={'Content-Type': 'application/json'}
            )

            logger.info(f"총 {len(posts)}개 게시글 Discord 전송 완료")
            return True

        except Exception as e:
            logger.error(f"Discord 전송 실패: {str(e)}")
            return False

    def send_error_notification(self, error_message):
        try:
            embed = {
                "title": "❌ Daily.dev Bot 에러 발생",
                "description": f"```\n{error_message}\n```",
                "color": 0xe74c3c,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "Daily.dev Bot Error"
                }
            }

            payload = {
                "embeds": [embed],
                "username": "Daily.dev Bot",
                "avatar_url": "https://daily.dev/favicon.ico"
            }

            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )

            return response.status_code == 204

        except Exception as e:
            logger.error(f"에러 알림 전송 실패: {str(e)}")
            return False