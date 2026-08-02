from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #Application settings
    app_name: str = "Afrab CFO"
    app_version: str = "0.1.0"
    environment: str = "development"
    
    #Server settings
    host: str = "127.0.0.1"
    port: int = 8000
    
    #Database settings
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()