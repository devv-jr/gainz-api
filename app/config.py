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
    ORIGINS = os.getenv("ORIGINS", "exp://127.0.0.1:19000").split(",")

    # Configuración de base de datos mejorada
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Si no hay DATABASE_URL (desarrollo local), usar SQLite
    if not DATABASE_URL:
        DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parent.parent / 'data' / 'exercises.db'}"
    
    # Environment detection
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Detectar el tipo de base de datos
    @property
    def is_postgresql(self) -> bool:
        return self.DATABASE_URL.startswith(('postgresql://', 'postgres://'))
    
    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith('sqlite://')

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production" or self.DATABASE_URL.startswith(("postgresql://", "postgres://"))
    
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "image/webp"]

settings = Settings()
