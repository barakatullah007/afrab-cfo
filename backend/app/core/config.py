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

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    groq_api_key: str | None = None
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_timeout_seconds: int = 15

    # Financial Knowledge Engine (RAG) settings
    rag_enabled: bool = True
    rag_knowledge_dir: str = "data/knowledge"
    rag_index_dir: str = "data/knowledge/.index"
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 150
    rag_top_k: int = 5
    rag_embedding_model: str = "all-MiniLM-L6-v2"
    rag_cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
