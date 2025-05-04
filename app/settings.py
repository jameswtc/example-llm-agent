from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    project_root: Path = Field(
        default=Path(__file__).resolve().parent.parent
    )  # Set project root dynamically

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


settings = AppSettings()
