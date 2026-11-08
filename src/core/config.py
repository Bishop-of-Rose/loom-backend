from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    FRONTEND_URL: str | list[str]
    TEST_DATABASE_URL: str
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SESSION_SECRET: str

    @model_validator(mode='after')
    def Parse_Comma_Separated(self):
        if isinstance(self.FRONTEND_URL, list):
            return self

        self.FRONTEND_URL = self.FRONTEND_URL.split(',')
        return self

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()