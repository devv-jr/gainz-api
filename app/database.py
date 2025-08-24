import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from contextlib import contextmanager
from app.config import settings
from pathlib import Path

logger = logging.getLogger(__name__)

# SQLite database file path
DB_FILE = Path(__file__).resolve().parent.parent / "data" / "exercises.db"

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Uses PostgreSQL in production, SQLite in development.
    """
    conn = None
    try:
        if settings.is_production:
            # PostgreSQL connection for production
            logger.info("Connecting to PostgreSQL database...")
            conn = psycopg2.connect(
                settings.DATABASE_URL,
                cursor_factory=RealDictCursor
            )
            logger.info("Successfully connected to PostgreSQL")
        else:
            # SQLite connection for development
            logger.info("Connecting to SQLite database...")
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
            logger.info("Successfully connected to SQLite")
        
        yield conn
        
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def init_database():
    """Initialize database tables if they don't exist"""
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
            """)
        
        conn.commit()
        logger.info("Database tables initialized successfully")

def get_exercise_count():
    """Get the total number of exercises in the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM exercises")
        result = cursor.fetchone()
        return result['count'] if result else 0
