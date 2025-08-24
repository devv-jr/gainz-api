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
    return name.lower().replace(' ', '-').replace("\u00f3", "o").replace("\u00e1", "a").replace("\u00e9", "e").replace("\u00ed", "i").replace("\u00fa", "u")

def migrate_exercises():
    """Main migration function"""
    try:
        logger.info("Starting exercise migration...")
        logger.info(f"Environment: {'Production' if settings.is_production else 'Development'}")
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        
        # Initialize database tables
        init_database()
        
        # Check if already migrated
        current_count = get_exercise_count()
        if current_count > 0:
            logger.info(f"Database already contains {current_count} exercises. Skipping migration.")
            return
        
        # Load exercises from JSON
        data_file = Path(__file__).parent.parent / "data" / "exercises.json"
        if not data_file.exists():
            logger.error(f"JSON file not found: {data_file}")
            return
        
        with open(data_file, 'r', encoding='utf-8') as f:
            raw_exercises = json.load(f)
        
        logger.info(f"Found {len(raw_exercises)} exercises in JSON file")
        
        # Migrate exercises
        migrated_count = 0
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for item in raw_exercises:
                try:
                    # Convert v1 format to v2 format
                    steps = []
                    if item.get('instructions'):
                        steps = [{"order": 1, "instruction": item['instructions']}]
                    
                    if settings.is_production:
                        # PostgreSQL insert
                        cursor.execute("""
                            INSERT INTO exercises (slug, name, summary, description, primary_muscle, 
                                                 secondary_muscles, equipment, difficulty, steps, tips, 
                                                 images, video_url, tags, variations, estimated, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            slugify(item.get('name', '')),
                            item.get('name'),
                            (item.get('instructions') or '')[:120],
                            item.get('instructions'),
                            item.get('muscle'),
                            json.dumps([]),  # secondary_muscles
                            json.dumps([item.get('equipment')] if item.get('equipment') else []),
                            item.get('difficulty'),
                            json.dumps(steps),
                            json.dumps([]),  # tips
                            json.dumps([]),  # images
                            None,  # video_url
                            json.dumps([]),  # tags
                            json.dumps([]),  # variations
                            None,  # estimated
                            datetime.utcnow()
                        ))
                    else:
                        # SQLite insert
                        cursor.execute("""
                            INSERT INTO exercises (slug, name, summary, description, primary_muscle, 
                                                 secondary_muscles, equipment, difficulty, steps, tips, 
                                                 images, video_url, tags, variations, estimated, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            slugify(item.get('name', '')),
                            item.get('name'),
                            (item.get('instructions') or '')[:120],
                            item.get('instructions'),
                            item.get('muscle'),
                            json.dumps([]),  # secondary_muscles
                            json.dumps([item.get('equipment')] if item.get('equipment') else []),
                            item.get('difficulty'),
                            json.dumps(steps),
                            json.dumps([]),  # tips
                            json.dumps([]),  # images
                            None,  # video_url
                            json.dumps([]),  # tags
                            json.dumps([]),  # variations
                            None,  # estimated
                            datetime.utcnow().isoformat()
                        ))
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error migrating exercise '{item.get('name', 'Unknown')}': {e}")
                    continue
            
            conn.commit()
        
        final_count = get_exercise_count()
        logger.info(f"Migration completed successfully!")
        logger.info(f"Exercises migrated: {migrated_count}/{len(raw_exercises)}")
        logger.info(f"Total exercises in database: {final_count}")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_exercises()
