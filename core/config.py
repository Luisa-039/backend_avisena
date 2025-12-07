from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# librería en Python que permite cargar variables de entorno
load_dotenv()
 
class Settings(BaseSettings):
    PROJECT_NAME: str = "AVISENA"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "Aplicación para gestionar granjas avicolas"

    # Configuración de la base de datos
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "")

    DATABASE_URL: str = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Configuración JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "XLgYz9lCctoQ3GuUuiiMW8diCiTq9dvv8gggsdyWsYG8K2kgPicfsm3g0bRS2JgFF3n9cxkXAHuR4roQQz2f7SS")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Configuración de Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "noreply@avisena.com")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://backend-avisena.onrender.com")

    class Config:
        env_file = ".env"

settings = Settings()

