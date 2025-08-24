import os
import logging
from pathlib import Path

# Configuración de logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log') if os.getenv('ENVIRONMENT') == 'development' else logging.StreamHandler()
        ]
    )

# Configuración de la aplicación
class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS: str = os.getenv("ADMIN_PASS", "password")
    ORIGINS: str = os.getenv("ORIGINS", "exp://127.0.0.1:19000")
    DATABASE_URL: str = str(Path(__file__).resolve().parent.parent / "data" / "exercises.db")
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "image/webp"]

settings = Settings()
