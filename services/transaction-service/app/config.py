from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@postgres-transaction:5432/transactiondb"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    USER_SERVICE_URL: str = "http://user-service:8001"

    class Config:
        env_file = ".env"

settings = Settings()
