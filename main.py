import sys
import argparse
import logging
from config import Config
from scheduler import DailyBotScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def validate_config():
    config = Config()
    errors = []

    if not config.DISCORD_WEBHOOK_URL:
        errors.append("DISCORD_WEBHOOK_URL이 설정되지 않았습니다.")

    if not config.DAILY_DEV_EMAIL:
        errors.append("DAILY_DEV_EMAIL이 설정되지 않았습니다.")

    if not config.DAILY_DEV_PASSWORD:
        errors.append("DAILY_DEV_PASSWORD가 설정되지 않았습니다.")

    if errors:
        logger.error("설정 오류:")
        for error in errors:
            logger.error(f"  - {error}")
        logger.error("\n.env 파일을 확인하고 필수 환경변수를 설정해주세요.")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Daily.dev Bot")
    parser.add_argument("--run-once", action="store_true", help="즉시 한 번 실행")
    parser.add_argument("--api", action="store_true", help="API 서버 시작")
    parser.add_argument("--validate", action="store_true", help="설정 검증")

    args = parser.parse_args()

    if args.validate:
        if validate_config():
            logger.info("모든 설정이 올바르게 구성되었습니다.")
        sys.exit(0)

    if not validate_config():
        sys.exit(1)

    logger.info("Daily.dev Bot 시작")
    logger.info("=" * 50)

    try:
        if args.api:
            logger.info("API 서버 모드로 시작")
            import uvicorn
            from web_api import app

            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_config={
                    "version": 1,
                    "formatters": {
                        "default": {
                            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        }
                    },
                    "handlers": {
                        "default": {
                            "formatter": "default",
                            "class": "logging.StreamHandler",
                            "stream": "ext://sys.stdout",
                        },
                    },
                    "root": {
                        "level": "INFO",
                        "handlers": ["default"],
                    },
                }
            )

        elif args.run_once:
            logger.info("즉시 실행 모드")
            scheduler = DailyBotScheduler()
            scheduler.run_once()

        else:
            logger.info("스케줄러 모드로 시작")
            scheduler = DailyBotScheduler()
            scheduler.start_scheduler()

    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()