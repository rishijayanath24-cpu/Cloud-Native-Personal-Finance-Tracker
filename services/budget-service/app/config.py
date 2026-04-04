from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@postgres-budget:5432/budgetdb"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    TRANSACTION_SERVICE_URL: str = "http://transaction-service:8002"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8004"

    class Config:
        env_file = ".env"

settings = Settings()
