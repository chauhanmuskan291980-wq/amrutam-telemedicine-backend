from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Amrutam Telemedicine Backend"
    app_env: str = "development"
    app_debug: bool = True

    database_url: str = "postgresql://postgres:postgres@localhost:5432/amrutam_db"
    redis_enabled: bool = False
    redis_url: str = "redis://127.0.0.1:6379/0"
     

    jwt_secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    rate_limit_storage_url: str = "memory://"
    rate_limit_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()