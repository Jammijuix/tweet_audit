from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #api credentials loaded from  .env file
    gemini_api_key: str
    gemini_model : str = "gemini-3.5-flash"

    #default  file path
    archive_file_path: Path = Path("tweet_audit/data/tweets.js")
    #load configuration from the .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf_8",
        extra="ignore"
    )


settings = Settings()
    
