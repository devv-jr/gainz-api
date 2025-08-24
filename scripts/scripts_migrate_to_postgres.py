#!/usr/bin/env python3
"""
Migration script to populate PostgreSQL database with exercises from JSON file.
This script should be run in production to migrate data from the JSON file to PostgreSQL.
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_connection, init_database, get_exercise_count
from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def slugify(name: str) -> str:
    """Convert name to URL-friendly slug"""
    import re
    name = name.lower()
    name = re.sub(r'[áàäâ]', 'a', name)
    name = re.sub(r'[éèëê]', 'e', name)
    name = re.sub(r'[íìïî]', 'i', name)
    name = re.sub(r'[óòöô]', 'o', name)
    name = re.sub(r'[úùüû]', 'u', name)
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'[\s-]+', '-', name)
    return name.strip('-')

def migrate_exercises():
    """Main migration function"""
    try:
        logger.info("Starting exercise migration...")
        logger.info(f"Environment: {'Production' if settings.is_production else 'Development'}")
        
        # Initialize database tables
        init_database()
        
        # Check if already migrated
        current_count = get_exercise_count()
        if current_count > 50:  # Si ya tiene muchos ejercicios, no migrar
            logger.info(f"Database already contains {current_count} exercises. Skipping migration.")
            return
        
        # Try to load from complete JSON first, fallback to regular JSON
        data_files = [
            Path(__file__).parent.parent / "data" / "exercises_complete.json",
            Path(__file__).parent.parent / "data" / "exercises.json"
        ]
        
        raw_exercises = None
        for data_file in data_files:
            if data_file.exists():
                logger.info(f"Loading exercises from: {data_file}")
                with open(data_file, 'r', encoding='utf-8') as f:
                    raw_exercises = json.load(f)
                break
        
        if not raw_exercises:
            logger.error("No exercise data files found")
            return
        
        logger.info(f"Found {len(raw_exercises)} exercises to migrate")
        
        # Migrate exercises
        migrated_count = 0
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for item in raw_exercises:
                try:
                    # Convert data to v2 format
                    name = item.get('name', '')
                    slug = slugify(name)
                    
                    # Handle different field names between v1 and v2
                    primary_muscle = item.get('primary_muscle') or item.get('muscle', '')
                    equipment = item.get('equipment', [])
                    if isinstance(equipment, str):
                        equipment = [equipment]
                    
                    # Handle steps
                    steps = item.get('steps', [])
                    if not steps and item.get('instructions'):
                        steps = [{"order": 1, "instruction": item['instructions']}]
                    
                    if settings.is_production:
                        # PostgreSQL insert
                        cursor.execute("""
                            INSERT INTO exercises (slug, name, summary, description, primary_muscle, 
                                                 secondary_muscles, equipment, difficulty, steps, tips, 
                                                 images, video_url, tags, variations, estimated, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (slug) DO NOTHING
                        """, (
                            slug,
                            name,
                            item.get('summary') or (item.get('description') or item.get('instructions', ''))[:120],
                            item.get('description') or item.get('instructions'),
                            primary_muscle,
                            json.dumps(item.get('secondary_muscles', [])),
                            json.dumps(equipment),
                            item.get('difficulty'),
                            json.dumps(steps),
                            json.dumps(item.get('tips', [])),
                            json.dumps(item.get('images', [])),
                            item.get('video_url'),
                            json.dumps(item.get('tags', [])),
                            json.dumps(item.get('variations', [])),
                            json.dumps(item.get('estimated')) if item.get('estimated') else None,
                            datetime.utcnow()
                        ))
                    else:
                        # SQLite insert  
                        cursor.execute("""
                            INSERT OR IGNORE INTO exercises (slug, name, summary, description, primary_muscle, 
                                                           secondary_muscles, equipment, difficulty, steps, tips, 
                                                           images, video_url, tags, variations, estimated, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            slug, name,
                            item.get('summary') or (item.get('description') or item.get('instructions', ''))[:120],
                            item.get('description') or item.get('instructions'),
                            primary_muscle,
                            json.dumps(item.get('secondary_muscles', [])),
                            json.dumps(equipment),
                            item.get('difficulty'),
                            json.dumps(steps),
                            json.dumps(item.get('tips', [])),
                            json.dumps(item.get('images', [])),
                            item.get('video_url'),
                            json.dumps(item.get('tags', [])),
                            json.dumps(item.get('variations', [])),
                            json.dumps(item.get('estimated')) if item.get('estimated') else None,
                            datetime.utcnow().isoformat()
                        ))
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error migrating exercise {item.get('name', 'Unknown')}: {e}")
                    continue
            
            conn.commit()
        
        logger.info(f"Successfully migrated {migrated_count} exercises")
        final_count = get_exercise_count()
        logger.info(f"Database now contains {final_count} exercises")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_exercises()