from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ORIGIN: str = "client_origin"
    TEST_DATABASE_URL: str = "test_database_url"
    DATABASE_URL: str = "database_url"
    REDIS_URL: str = "redis_url"
    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "algorithm"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()