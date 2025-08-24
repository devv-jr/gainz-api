from sqlalchemy import create_engine, text
from .database import Base, engine
from .config import settings
import logging

logger = logging.getLogger(__name__)

def create_tables():
    """Crear todas las tablas definidas en los modelos"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"Error creando tablas: {e}")
        raise

def init_database():
    """Inicializar la base de datos según el entorno"""
    logger.info(f"Inicializando base de datos: {settings.DATABASE_URL}")
    
    if settings.is_postgresql:
        logger.info("Configurando PostgreSQL para producción")
        # Aquí puedes agregar configuraciones específicas para PostgreSQL
        create_tables()
    
    elif settings.is_sqlite:
        logger.info("Configurando SQLite para desarrollo")
        # Crear directorio data si no existe
        import os
        from pathlib import Path
        data_dir = Path(__file__).resolve().parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        create_tables()
    
    logger.info("Base de datos inicializada correctamente")

if __name__ == "__main__":
    init_database()
