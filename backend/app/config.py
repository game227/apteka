from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://neo@localhost:5432/apteka_db"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 30

    telegram_bot_token: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    price_deviation_threshold: float = 0.20
    fuzzy_match_threshold: int = 80
    fuzzy_match_confirm_threshold: int = 60

    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
