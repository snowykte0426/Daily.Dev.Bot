import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    DAILY_DEV_EMAIL = os.getenv("DAILY_DEV_EMAIL")
    DAILY_DEV_PASSWORD = os.getenv("DAILY_DEV_PASSWORD")
    CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")
    GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")

    SCHEDULE_TIME = "08:00"

    DAILY_DEV_URL = "https://app.daily.dev"
    POST_LIMIT = 10
    FETCH_CONTENT = os.getenv("FETCH_CONTENT", "true").lower() == "true"