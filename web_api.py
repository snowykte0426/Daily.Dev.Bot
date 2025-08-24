from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
from daily_scraper import DailyDevScraper
from translator import KoreanTranslator
from discord_sender import DiscordSender
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Daily.dev Bot API",
    description="Daily.dev 게시글을 크롤링하고 한국어로 번역하여 Discord로 전송하는 API",
    version="1.0.0"
)

config = Config()


@app.get("/")
async def root():
    return {
        "message": "Daily.dev Bot API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/scrape")
async def scrape_posts(background_tasks: BackgroundTasks, limit: int = 10):
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(status_code=400, detail="limit은 1~50 사이의 값이어야 합니다.")
        background_tasks.add_task(run_scraping_task, limit)

        return {
            "message": f"상위 {limit}개 게시글 크롤링 작업이 시작되었습니다.",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"크롤링 요청 처리 중 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")


@app.get("/scrape-sync")
async def scrape_posts_sync(limit: int = 10):
    try:
        if limit < 1 or limit > 20:
            raise HTTPException(status_code=400, detail="limit은 1~20 사이의 값이어야 합니다.")

        scraper = DailyDevScraper()
        posts = scraper.scrape_posts(limit)

        if not posts:
            raise HTTPException(status_code=404, detail="게시글을 가져올 수 없습니다.")

        return {
            "message": f"{len(posts)}개 게시글 크롤링 완료",
            "count": len(posts),
            "posts": posts,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"동기 크롤링 중 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")


@app.post("/translate")
async def translate_text(text: str, target_lang: str = "ko"):
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="번역할 텍스트가 없습니다.")

        if target_lang != "ko":
            raise HTTPException(status_code=400, detail="현재 한국어 번역만 지원합니다.")

        translator = KoreanTranslator()
        translated_text = translator.translate_to_korean(text)

        return {
            "original": text,
            "translated": translated_text,
            "target_language": target_lang,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"번역 중 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"번역 실패: {str(e)}")


@app.get("/config")
async def get_config():
    return {
        "post_limit": config.POST_LIMIT,
        "schedule_time": config.SCHEDULE_TIME,
        "daily_dev_url": config.DAILY_DEV_URL,
        "webhook_configured": bool(config.DISCORD_WEBHOOK_URL),
        "timestamp": datetime.now().isoformat()
    }


async def run_scraping_task(limit: int):
    try:
        logger.info(f"백그라운드 크롤링 시작 (limit: {limit})")

        scraper = DailyDevScraper()
        posts = scraper.scrape_posts(limit)

        if not posts:
            logger.error("크롤링된 게시글이 없습니다.")
            return

        translator = KoreanTranslator()
        translated_posts = translator.translate_posts(posts)

        discord_sender = DiscordSender()
        success = discord_sender.send_daily_posts(translated_posts)

        if success:
            logger.info(f"백그라운드 크롤링 작업 완료: {len(translated_posts)}개 게시글")
        else:
            logger.error("Discord 전송 실패")

    except Exception as e:
        logger.error(f"백그라운드 크롤링 작업 중 에러: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)