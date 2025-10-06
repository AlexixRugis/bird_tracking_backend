from pydantic_settings import BaseSettings, SettingsConfigDict

class _Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    APP_TCP_PORT: int = 9999
    ENABLE_TCP_SERVER: bool = False
    
    DATABASE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra='allow')

settings = _Settings()