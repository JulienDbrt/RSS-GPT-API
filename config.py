from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Charge les variables depuis un fichier .env si présent
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    # Base de données
    DATABASE_URL: str = "sqlite:///./rssgpt.db"
    DB_ECHO: bool = False # Contrôle le echo de SQLAlchemy

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Logique de l'application
    SUMMARY_LANGUAGE: str = "fr"
    SUMMARY_LENGTH: int = 250
    KEYWORD_COUNT: int = 6

    # Sécurité
    API_KEY: str

    # Configuration Redis pour ARQ
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

settings = Settings()