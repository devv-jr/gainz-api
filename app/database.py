import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Configuración específica según el tipo de base de datos
if settings.is_postgresql:
    # Configuración para PostgreSQL en producción
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Cambiar a True para debug
    )
else:
    # Configuración para SQLite en desarrollo
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Solo para SQLite
        echo=True  # Para ver las consultas SQL en desarrollo
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
