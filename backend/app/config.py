from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    supabase_url: Optional[str] = None          # Optional に変更
    supabase_service_role_key: Optional[str] = None  # Optional に変更

    class Config:
        env_file = ".env"

settings = Settings()