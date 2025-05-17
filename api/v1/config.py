from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FIND MATE SERVICE API"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000
    DATABASE_URL: str = "mysql+pymysql://root:gh245hyt@localhost/findmate_db"

    class Config:
        env_file = ".env"

settings = Settings()