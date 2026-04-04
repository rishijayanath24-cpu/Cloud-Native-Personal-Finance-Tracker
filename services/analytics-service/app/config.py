from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    TRANSACTION_SERVICE_URL: str = "http://transaction-service:8002"
    BUDGET_SERVICE_URL: str = "http://budget-service:8003"
    REDIS_URL: str = "redis://redis:6379"
    CACHE_TTL_SECONDS: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
