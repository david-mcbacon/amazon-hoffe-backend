from typing import Any, Union

from pydantic import BaseSettings, PostgresDsn, RedisDsn, root_validator

from src.constants import Environment


class Config(BaseSettings):
    DATABASE_URL: PostgresDsn = "postgresql://user:password@localhost:5432/db"
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    SITE_DOMAIN: str = "myapp.com"

    ENVIRONMENT: Environment = Environment.LOCAL

    SENTRY_DSN: Union[str, None]

    CORS_ORIGINS: list[str] = ["*"]
    CORS_ORIGINS_REGEX: Union[str, None]
    CORS_HEADERS: list[str] = ["*"]

    APP_VERSION: str = "1"

    @root_validator(skip_on_failure=True)
    def validate_sentry_non_local(cls, data: dict[str, Any]) -> dict[str, Any]:
        if data["ENVIRONMENT"].is_deployed and not data["SENTRY_DSN"]:
            raise ValueError("Sentry is not set")

        return data


settings = Config()

app_configs: dict[str, Any] = {
    "title": "Amazon Hoffe Backend",
    "swagger_ui_parameters": {"displayRequestDuration": True},
}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs
