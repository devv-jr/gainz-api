import os
import sqlite3
import psycopg2
from contextlib import contextmanager
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

@contextmanager 
def get_db_connection():
    """Get database connection based on environment"""
    if settings.is_production:
        # PostgreSQL connection
        conn = psycopg2.connect(settings.DATABASE_URL)
        try:
            yield conn
        finally:
            conn.close()
    else:
        # SQLite connection
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        try:
            yield conn
        finally:
            conn.close()

def init_database():
    """Initialize database and create tables"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if settings.is_production:
                # PostgreSQL table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS exercises (
                        id SERIAL PRIMARY KEY,
                        slug VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        summary TEXT,
                        description TEXT,
                        primary_muscle VARCHAR(100),
                        secondary_muscles JSONB DEFAULT '[]',
                        equipment JSONB DEFAULT '[]',
                        difficulty VARCHAR(20) DEFAULT 'intermediate',
                        steps JSONB DEFAULT '[]',
                        tips JSONB DEFAULT '[]',
                        images JSONB DEFAULT '[]',
                        video_url TEXT,
                        tags JSONB DEFAULT '[]',
                        variations JSONB DEFAULT '[]',
                        estimated JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
                # SQLite table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS exercises (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        slug TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        summary TEXT,
                        description TEXT,
                        primary_muscle TEXT,
                        secondary_muscles TEXT DEFAULT '[]',
                        equipment TEXT DEFAULT '[]',
                        difficulty TEXT DEFAULT 'intermediate',
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
                """)
                
            conn.commit()
            print(f"Database initialized successfully with {settings.DATABASE_URL}")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def get_exercise_count():
    """Get total number of exercises in database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM exercises")
            result = cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        print(f"Error getting exercise count: {e}")
        return 0
