from pydantic_settings import BaseSettings

class Config(BaseSettings):
    EMBEDDINGS_MODEL_NAME: str = "models/gemini-embedding-001"
    LLM_MODEL_NAME: str = "gemini-2.5-flash"
    GOOGLE_API_KEY: str = ""
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    WEAVIATE_URL: str = ""
    WEAVIATE_API_KEY: str = ""

    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }
