import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Safety limits
    max_requests: int = 100_000
    max_concurrency: int = 500
    max_workers: int = 10
    max_duration_seconds: int = 3600

    # Default values
    default_workers: int = 1

    # Security
    api_token: str = ""
    allowed_target_hosts: str = "localhost,127.0.0.1,target-service,httpbin.org"

    class Config:
        env_prefix = "LOAD_TEST_"
        env_file = ".env"
        extra = "ignore"

    @property
    def allowed_hosts_list(self) -> List[str]:
        return [h.strip().lower() for h in self.allowed_target_hosts.split(",") if h.strip()]

    @property
    def auth_enabled(self) -> bool:
        return bool(self.api_token.strip())


settings = Settings()

# Allow both prefixed and unprefixed env vars for convenience
settings.api_token = os.getenv("API_TOKEN", settings.api_token)
settings.allowed_target_hosts = os.getenv("ALLOWED_TARGET_HOSTS", settings.allowed_target_hosts)
