import logging
import time

import schedule

from config import Config
from daily_scraper import DailyDevScraper
from discord_sender import DiscordSender
from translator import KoreanTranslator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DailyBotScheduler:
    def __init__(self):
        self.config = Config()
        self.scraper = DailyDevScraper()
        self.translator = KoreanTranslator()
        self.discord_sender = DiscordSender()

    def run_daily_job(self):
        logger.info("Daily.dev Bot 작업 시작")

        try:
            logger.info("게시글 크롤링 시작...")
            posts = self.scraper.scrape_posts(limit=self.config.POST_LIMIT)

            if not posts:
                error_msg = "게시글을 가져올 수 없습니다."
                logger.error(error_msg)
                self.discord_sender.send_error_notification(error_msg)
                return

            logger.info(f"{len(posts)}개 게시글 크롤링 완료")

            logger.info("게시글 번역 시작...")
            translated_posts = self.translator.translate_posts(posts)

            logger.info("Discord 전송 시작...")
            success = self.discord_sender.send_daily_posts(translated_posts)

            if success:
                logger.info("Daily.dev Bot 작업 완료!")
            else:
                error_msg = "Discord 전송 실패"
                logger.error(error_msg)
                self.discord_sender.send_error_notification(error_msg)

        except Exception as e:
            error_msg = f"Daily.dev Bot 작업 중 에러 발생: {str(e)}"
            logger.error(error_msg)
            self.discord_sender.send_error_notification(error_msg)

    def start_scheduler(self):
        logger.info(f"Daily.dev Bot 스케줄러 시작 - 매일 {self.config.SCHEDULE_TIME}에 실행")

        schedule.every().day.at(self.config.SCHEDULE_TIME).do(self.run_daily_job)

        next_run = schedule.next_run()
        logger.info(f"다음 실행 예정 시간: {next_run}")

        while True:
            schedule.run_pending()
            time.sleep(60)

    def run_once(self):
        logger.info("즉시 실행 모드")
        self.run_daily_job()


if __name__ == "__main__":
    scheduler = DailyBotScheduler()
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--run-once":
        scheduler.run_once()
    else:
        scheduler.start_scheduler()