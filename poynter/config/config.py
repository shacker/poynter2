import base64
import os
from pathlib import Path
from typing import List, Callable, Optional, Any

from goodconf import GoodConf, Field

# Make this the same as in main settings:
BASE_DIR: Path = Path(__file__).resolve().parent.parent


class AppConfig(GoodConf):
    """Configuration for template site. Pulls environment variables from
    the running instance and stores them as Django settings for use in code."""

    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    AWS_S3_REGION_NAME: str = Field(default="us-west-2")
    AWS_LOCATION: str = Field(default="", description="Var used by Django to prepend bucket prefix")
    PRIVATE_S3_BUCKET_PREFIX: str = Field(
        default="", description="Bucket prefix for this server instance"
    )
    AWS_SUBMITFILES_BUCKET_NAME: str = Field(
        default="", description="Connection to S3 bucket for media"
    )
    DEBUG: bool = Field(default=False, description="Toggle debugging.")
    EMAIL_BACKEND: str = Field(default="django.core.mail.backends.console.EmailBackend")
    ENVIRONMENT: str = Field(default="", description="Environment where application is deployed.")
    LOCAL_DEV: bool = Field(default=False, description="Enable local development tools")
    LOG_LEVEL: str = Field(default="INFO", description="Log level for application")
    DATABASE_URL: str = Field(
        default="postgres://localhost:5432/apppack_template", description="Database connection."
    )
    MEDIA_ROOT: str = Field(default=str(BASE_DIR / "media"))
    STATIC_ROOT: str = Field(default=str(BASE_DIR / "staticfiles"))
    PRIVATE_S3_BUCKET_NAME: str = Field(
        default="", description="Connection to S3 private bucket for media"
    )
    REDIS_ENABLED: bool = Field(default=False, description="If False, db caching will be used.")
    REDIS_URL: str = Field(default="redis://127.0.0.1:6379")
    REDIS_PREFIX: str = Field(default="poynter")
    SECRET_KEY: str = Field(
        default_factory=lambda: base64.b64encode(os.urandom(60)).decode(),
        description="Used for cryptographic signing. "
        "https://docs.djangoproject.com/en/2.0/ref/settings/#secret-key",
    )
    SENTRY_DSN: str = Field(default="")
    TEST_EMAIL_TO: str = Field(default="")

    class Config:
        default_files: List[str] = ["poynter/config/local.yml", "poynter/config/local.json"]


config: AppConfig = AppConfig()


def manage_py() -> None:
    """Entrypoint for manage.py"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poynter.config.settings")
    config.django_manage()


def generate_config() -> None:
    """Entrypoint for dumping out sample config"""
    print(config.generate_json(LOCAL_DEV=True, DEBUG=True, LOG_LEVEL="DEBUG"))
