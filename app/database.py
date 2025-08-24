"""
Database connection and SQLAlchemy setup for GainzAPI
Supports both PostgreSQL (production) and SQLite (development)
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from contextlib import contextmanager
from typing import Generator
import os
from pathlib import Path

from app.config import settings

# Base for SQLAlchemy models
Base = declarative_base()

# Database engine setup
def create_database_engine():
    """Create database engine based on DATABASE_URL"""
    database_url = settings.DATABASE_URL
    
    # Check if it's a PostgreSQL URL or SQLite file path
    if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
        # PostgreSQL connection
        engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
        )
    else:
        # SQLite connection (for development)
        if not database_url.startswith('sqlite:'):
            # Convert file path to SQLite URL
            database_url = f"sqlite:///{database_url}"
        
        engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False}  # Only for SQLite
        )
    
    return engine

# Create engine and session factory
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Exercise table definition - backward compatible with existing migration
exercises_table = Table(
    'exercises',
    Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('name', String(255), nullable=False),
    Column('slug', String(255), unique=True, index=True),
    Column('primary_muscle', String(100)),
    Column('difficulty', String(50)),
    # Legacy column for backward compatibility
    Column('json_data', Text),
    # New columns for v2 API
    Column('summary', Text),
    Column('description', Text),
    Column('secondary_muscles', Text),  # JSON string
    Column('equipment', Text),          # JSON string
    Column('steps', Text),              # JSON string
    Column('tips', Text),               # JSON string
    Column('images', Text),             # JSON string
    Column('video_url', String(500)),
    Column('tags', Text),               # JSON string
    Column('variations', Text),         # JSON string
    Column('estimated', Text),          # JSON string
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    try:
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise