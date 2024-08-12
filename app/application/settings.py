from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    DEBUG_MOD: bool

    # Directories
    DIRECTORY_MEDIA: str
    DIRECTORY_TEMPLATES: str

    # Database urls
    DATABASE_URL_TEST: str
    # Local url use for run not in docker container
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file="settings_app.cfg", env_file_encoding="utf-8"
    )


settings = Settings()

if __name__ == "__main__":
    settings = Settings()
    print(settings.model_dump())
