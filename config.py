# config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env 파일 로드 설정
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # DB 및 JWT
    database_url: str
    jwt_secret: str

    # AWS S3
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    aws_s3_bucket_name: str

    # TMap
    tmap_app_key: str


@lru_cache
def get_settings():
    """환경 설정을 캐싱해서 어디서든 import 가능"""
    return Settings()
