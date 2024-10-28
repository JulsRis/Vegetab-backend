from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Food App"
    API_V1_STR: str = "/api/v1"
    SPOONACULAR_API_KEY: str = "YOUR_SPOONACULAR_API_KEY"  # Replace with actual API key
    GOOGLE_CLOUD_VISION_CREDENTIALS: str  # This will be set from an environment variable
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./food_app.db")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
