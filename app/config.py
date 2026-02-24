import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    FOURBYFOUR_API_KEY = os.getenv("FOURBYFOUR_API_KEY", "")
    FOURBYFOUR_PROJECT_ID = os.getenv("FOURBYFOUR_PROJECT_ID", "")
    FOURBYFOUR_BASE_URL = os.getenv("FOURBYFOUR_BASE_URL", "https://api.fourbyfour.dev")
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))


config = Config()
