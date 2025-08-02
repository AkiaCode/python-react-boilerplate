import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")


class Settings:
    USE_BUNDLE_PROXY = os.getenv("USE_BUNDLE_PROXY", "false").lower() == "true"
    FRONTEND_BUNDLE_PROXY_URL = os.getenv("FRONTEND_BUNDLE_PROXY_URL")


settings = Settings()
