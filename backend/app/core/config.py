from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
#Pydantic Settings class will automatically load enviroment variables, .env file and validate the values.


class Settings(BaseSettings):
   
    DATABASE_URL: str = "sqlite+aiosqlite:///./payment_system.db"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    APP_NAME: str = "HSBC Payment System"
    VERSION: str = "1.0.0"
    
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def allowed_origins_list(self) -> List[str]:

        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    PAYMENT_PENDING_TO_PROCESSING_DELAY: int = 10    
    PAYMENT_PROCESSING_MIN_DELAY: int = 3
    PAYMENT_PROCESSING_MAX_DELAY: int = 6
    PAYMENT_SUCCESS_RATE: float = 0.5                
    
    model_config = SettingsConfigDict(
        env_file=".env",           # read from .env file
        env_file_encoding="utf-8", # encoding format
        case_sensitive=False       # environment variable name is not case-sensitive
    )


# Create global configuration instance (singleton pattern)
settings = Settings()


# Convenient function: get configuration instance
def get_settings() -> Settings:

    return settings