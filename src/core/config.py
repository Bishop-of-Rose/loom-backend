from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ORIGIN: str
    TEST_DATABASE_URL: str
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()