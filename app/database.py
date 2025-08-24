import os
import sqlite3
import psycopg2
import psycopg2.extras  # ⭐ Agregamos esta importación
from contextlib import contextmanager
from sqlalchemy import create_engine, text
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

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    if settings.is_postgresql:
        # ⭐ Corrección: usar cursor_factory en la conexión
        conn = psycopg2.connect(settings.DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        conn = sqlite3.connect(settings.DATABASE_URL.replace("sqlite:///", ""))
        conn.row_factory = sqlite3.Row
    
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database tables"""
    try:
        with engine.connect() as conn:
            # Create exercises table
            if settings.is_postgresql:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS exercises (
                        id SERIAL PRIMARY KEY,
                        slug VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        summary TEXT,
                        description TEXT,
                        primary_muscle VARCHAR(100),
                        secondary_muscles JSONB DEFAULT '[]',
                        equipment JSONB DEFAULT '[]',
                        difficulty VARCHAR(50),
                        steps JSONB DEFAULT '[]',
                        tips JSONB DEFAULT '[]',
                        images JSONB DEFAULT '[]',
                        video_url VARCHAR(500),
                        tags JSONB DEFAULT '[]',
                        variations JSONB DEFAULT '[]',
                        estimated JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS exercises (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        slug TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        summary TEXT,
                        description TEXT,
                        primary_muscle TEXT,
                        secondary_muscles TEXT DEFAULT '[]',
                        equipment TEXT DEFAULT '[]',
                        difficulty TEXT,
                        steps TEXT DEFAULT '[]',
                        tips TEXT DEFAULT '[]',
                        images TEXT DEFAULT '[]',
                        video_url TEXT,
                        tags TEXT DEFAULT '[]',
                        variations TEXT DEFAULT '[]',
                        estimated TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def get_exercise_count():
    """Get total count of exercises in database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM exercises"))
            return result.fetchone().count
    except Exception as e:
        print(f"Error getting exercise count: {e}")
        return 0
