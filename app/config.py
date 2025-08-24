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
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS: str = os.getenv("ADMIN_PASS", "password")
    ORIGINS = os.getenv("ORIGINS", "").split(",")

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL") or str(
        Path(__file__).resolve().parent.parent / "data" / "exercises.db"
    )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production (PostgreSQL)"""
        return self.DATABASE_URL.startswith(('postgresql://', 'postgres://'))
    
    @property
    def is_development(self) -> bool:
        """Check if running in development (SQLite)"""
        return not self.is_production

    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "image/webp"]

settings = Settings()
