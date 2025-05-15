from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    # MongoDB
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_DB: str
    MONGO_PARAMS: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @property
    def postgres_database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )
    
    @property
    def mongo_database_url(self) -> str:
        return (
            f"mongodb+srv://{self.MONGO_USER}:"
            f"{self.MONGO_PASSWORD}@"
            f"{self.MONGO_HOST}/"
            f"{self.MONGO_DB}?"
            f"{self.MONGO_PARAMS}"
    )

    class Config:
        # Read environment variables from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Initialize settings
settings = Settings()

