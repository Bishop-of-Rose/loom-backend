from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str
    ORIGIN: str
    TEST_DATABASE_URL: str
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SESSION_SECRET: str

    @property
    def IS_DEV(self):
        return self.ENVIRONMENT == 'dev'

    @property
    def IS_PROD(self):
        return self.ENVIRONMENT == 'prod'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()