import os

class Settings:
    PROJECT_NAME: str = "Sleep Tracker API"
    PROJECT_DESCRIPTION: str = "API для отслеживания сна и управления режимом"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sleep_tracker.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "my_secret_key_for_sleep_tracker_app_12345")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
