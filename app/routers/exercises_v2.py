from fastapi import APIRouter, HTTPException, Query, Depends, Header
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from datetime import datetime
from app.auth import verify_token
from app.database import get_db_connection, init_database, get_exercise_count
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "exercises.json"

# Initialize database on module import
try:
    init_database()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

# Extended model for v2
class ImageItem(BaseModel):
    url: HttpUrl
    type: Optional[str] = "step"
    width: Optional[int] = None
    height: Optional[int] = None

class StepItem(BaseModel):
    order: int
    title: Optional[str] = None
    instruction: str
    duration_sec: Optional[int] = None

class EstimatedSetsReps(BaseModel):
    sets: Optional[int] = None
    reps: Optional[str] = None
    weight_kg: Optional[float] = None
    rest_sec: Optional[int] = None

class ExerciseV2(BaseModel):
    id: Optional[int] = None
    slug: str = Field(..., description="URL-friendly version of the name")
    name: str
    summary: Optional[str] = None
    description: Optional[str]
    primary_muscle: Optional[str]
    secondary_muscles: List[str] = []
    equipment: List[str] = []
    difficulty: Optional[str]
    steps: List[StepItem] = []
    tips: List[str] = []
    images: List[ImageItem] = []
    video_url: Optional[HttpUrl] = None
    tags: List[str] = []
    variations: List[Dict[str, Any]] = []
    estimated: Optional[EstimatedSetsReps] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


def load_exercises_raw():
    """Load exercises from database or fallback to JSON file"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if settings.is_production:
                # PostgreSQL query
                cursor.execute('SELECT * FROM exercises ORDER BY id')
            else:
                # SQLite query - try to get from exercises table first
                cursor.execute('SELECT * FROM exercises ORDER BY id')
            
            rows = cursor.fetchall()
            if rows:
                exercises = []
                for row in rows:
                    # Convert row to dict and handle JSON fields
                    exercise = dict(row)
                    
                    # Parse JSON fields for both PostgreSQL and SQLite
                    json_fields = ['secondary_muscles', 'equipment', 'steps', 'tips', 'images', 'tags', 'variations']
                    for field in json_fields:
                        if field in exercise and exercise[field]:
                            if isinstance(exercise[field], str):
                                try:
                                    exercise[field] = json.loads(exercise[field])
                                except json.JSONDecodeError:
                                    exercise[field] = []
                    
                    # Handle estimated field
                    if 'estimated' in exercise and exercise['estimated']:
                        if isinstance(exercise['estimated'], str):
                            try:
                                exercise['estimated'] = json.loads(exercise['estimated'])
                            except json.JSONDecodeError:
                                exercise['estimated'] = None
                    
                    exercises.append(exercise)
                
                logger.info(f"Loaded {len(exercises)} exercises from database")
                return exercises
            else:
                logger.warning("No exercises found in database, loading from JSON file")
                
    except Exception as e:
        logger.error(f"Error loading exercises from database: {e}")
        logger.info("Falling back to JSON file")
    
    # Fallback to JSON file
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} exercises from JSON file")
            return data
    except Exception as e:
        logger.error(f"Error loading exercises from JSON file: {e}")
        return []


def slugify(name: str) -> str:
    return name.lower().replace(' ', '-').replace("\u00f3", "o").replace("\u00e1", "a").replace("\u00e9", "e").replace("\u00ed", "i").replace("\u00fa", "u")


def transform(old):
    now = datetime.utcnow().isoformat()
    steps = []
    if old.get('instructions'):
        steps = [{"order": 1, "instruction": old['instructions']}]
    return {
        "id": old.get('id'),
        "slug": slugify(old.get('name', '')),
        "name": old.get('name'),
        "summary": (old.get('instructions') or '')[:120],
        "description": old.get('instructions'),
        "primary_muscle": old.get('muscle'),
        "secondary_muscles": [],
        "equipment": [old.get('equipment')] if old.get('equipment') else [],
        "difficulty": old.get('difficulty'),
        "steps": steps,
        "tips": [],
        "images": [],
        "video_url": None,
        "tags": [],
        "variations": [],
        "estimated": None,
        "created_at": now,
        "updated_at": now
    }


def require_auth(auth=Depends(verify_token)):
    if not auth:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return auth


@router.get("/", response_model=List[ExerciseV2])
def get_exercises_v2(query: Optional[str] = Query(None), muscle: Optional[str] = None, equipment: Optional[str] = None, page: int = 1, limit: int = 50):
    raw = load_exercises_raw()
    transformed = [transform(e) for e in raw]
    if query:
        q = query.lower()
        transformed = [e for e in transformed if q in (e['name'] or '').lower() or q in (e.get('description') or '').lower()]
    if muscle:
        transformed = [e for e in transformed if e.get('primary_muscle') and e['primary_muscle'].lower() == muscle.lower()]
    if equipment:
        transformed = [e for e in transformed if equipment.lower() in [x.lower() for x in e.get('equipment', [])]]
    start = (page - 1) * limit
    end = start + limit
    return transformed[start:end]

@router.get("/{exercise_id}", response_model=ExerciseV2)
def get_exercise_v2(exercise_id: int):
    raw = load_exercises_raw()
    for e in raw:
        if e.get('id') == exercise_id:
            return transform(e)
    raise HTTPException(status_code=404, detail="Exercise not found in v2")


@router.post("/", response_model=ExerciseV2)
def create_exercise_v2(ex: ExerciseV2, auth=Depends(require_auth)):
    # Insert into DB
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if settings.is_production:
                # PostgreSQL insert
                cursor.execute("""
                    INSERT INTO exercises (slug, name, summary, description, primary_muscle, 
                                         secondary_muscles, equipment, difficulty, steps, tips, 
                                         images, video_url, tags, variations, estimated, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    ex.slug, ex.name, ex.summary, ex.description, ex.primary_muscle,
                    json.dumps(ex.secondary_muscles), json.dumps(ex.equipment), ex.difficulty,
                    json.dumps([step.dict() for step in ex.steps]), json.dumps(ex.tips),
                    json.dumps([img.dict() for img in ex.images]), str(ex.video_url) if ex.video_url else None,
                    json.dumps(ex.tags), json.dumps(ex.variations), 
                    json.dumps(ex.estimated.dict()) if ex.estimated else None,
                    ex.created_at or datetime.utcnow()
                ))
                ex.id = cursor.fetchone()['id']
            else:
                # SQLite insert
                cursor.execute("""
                    INSERT INTO exercises (slug, name, summary, description, primary_muscle, 
                                         secondary_muscles, equipment, difficulty, steps, tips, 
                                         images, video_url, tags, variations, estimated, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ex.slug, ex.name, ex.summary, ex.description, ex.primary_muscle,
                    json.dumps(ex.secondary_muscles), json.dumps(ex.equipment), ex.difficulty,
                    json.dumps([step.dict() for step in ex.steps]), json.dumps(ex.tips),
                    json.dumps([img.dict() for img in ex.images]), str(ex.video_url) if ex.video_url else None,
                    json.dumps(ex.tags), json.dumps(ex.variations), 
                    json.dumps(ex.estimated.dict()) if ex.estimated else None,
                    (ex.created_at or datetime.utcnow()).isoformat()
                ))
                ex.id = cursor.lastrowid
            
            conn.commit()
            
    except Exception as e:
        logger.error(f"Error creating exercise: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating exercise: {str(e)}")
    
    return ex


@router.put("/{exercise_id}", response_model=ExerciseV2)
def update_exercise_v2(exercise_id: int, ex: ExerciseV2, auth=Depends(require_auth)):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exercise exists
            cursor.execute('SELECT id FROM exercises WHERE id = %s' if settings.is_production else 'SELECT id FROM exercises WHERE id = ?', (exercise_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail='Exercise not found')
            
            if settings.is_production:
                # PostgreSQL update
                cursor.execute("""
                    UPDATE exercises SET 
                        slug=%s, name=%s, summary=%s, description=%s, primary_muscle=%s,
                        secondary_muscles=%s, equipment=%s, difficulty=%s, steps=%s, tips=%s,
                        images=%s, video_url=%s, tags=%s, variations=%s, estimated=%s, updated_at=%s
                    WHERE id=%s
                """, (
                    ex.slug, ex.name, ex.summary, ex.description, ex.primary_muscle,
                    json.dumps(ex.secondary_muscles), json.dumps(ex.equipment), ex.difficulty,
                    json.dumps([step.dict() for step in ex.steps]), json.dumps(ex.tips),
                    json.dumps([img.dict() for img in ex.images]), str(ex.video_url) if ex.video_url else None,
                    json.dumps(ex.tags), json.dumps(ex.variations), 
                    json.dumps(ex.estimated.dict()) if ex.estimated else None,
                    datetime.utcnow(), exercise_id
                ))
            else:
                # SQLite update
                cursor.execute("""
                    UPDATE exercises SET 
                        slug=?, name=?, summary=?, description=?, primary_muscle=?,
                        secondary_muscles=?, equipment=?, difficulty=?, steps=?, tips=?,
                        images=?, video_url=?, tags=?, variations=?, estimated=?, updated_at=?
                    WHERE id=?
                """, (
                    ex.slug, ex.name, ex.summary, ex.description, ex.primary_muscle,
                    json.dumps(ex.secondary_muscles), json.dumps(ex.equipment), ex.difficulty,
                    json.dumps([step.dict() for step in ex.steps]), json.dumps(ex.tips),
                    json.dumps([img.dict() for img in ex.images]), str(ex.video_url) if ex.video_url else None,
                    json.dumps(ex.tags), json.dumps(ex.variations), 
                    json.dumps(ex.estimated.dict()) if ex.estimated else None,
                    datetime.utcnow().isoformat(), exercise_id
                ))
            
            conn.commit()
            ex.id = exercise_id
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating exercise: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating exercise: {str(e)}")
    
    return ex


@router.delete("/{exercise_id}", status_code=204)
def delete_exercise_v2(exercise_id: int, auth=Depends(require_auth)):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM exercises WHERE id = %s' if settings.is_production else 'DELETE FROM exercises WHERE id = ?', (exercise_id,))
            conn.commit()
            
    except Exception as e:
        logger.error(f"Error deleting exercise: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting exercise: {str(e)}")
    
    return


@router.post("/migrate", status_code=200)
def migrate_now(auth=Depends(require_auth)):
    """Migrate exercises from JSON file to database"""
    try:
        # Check current count
        current_count = get_exercise_count()
        if current_count > 0:
            return {"status": "already_migrated", "count": current_count}
        
        # Read JSON data
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            raw_exercises = json.load(f)
        
        logger.info(f"Migrating {len(raw_exercises)} exercises from JSON to database")
        
        # Insert exercises into database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for item in raw_exercises:
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
            
            conn.commit()
        
        final_count = get_exercise_count()
        logger.info(f"Migration completed successfully. Total exercises: {final_count}")
        return {"status": "migrated", "count": final_count}
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise HTTPException(status_code=500, detail=f"Migration error: {str(e)}")


@router.get("/stats")
def get_database_stats():
    """Get database statistics and health info"""
    try:
        total_count = get_exercise_count()
        
        # Get muscle group counts
        exercises = load_exercises_raw()
        muscle_counts = {}
        difficulty_counts = {}
        equipment_counts = {}
        
        for exercise in exercises:
            # Count by muscle group
            muscle = exercise.get('primary_muscle', 'Unknown')
            muscle_counts[muscle] = muscle_counts.get(muscle, 0) + 1
            
            # Count by difficulty
            diff = exercise.get('difficulty', 'Unknown')
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            
            # Count by equipment
            for equip in exercise.get('equipment', []):
                equipment_counts[equip] = equipment_counts.get(equip, 0) + 1
        
        return {
            "total_exercises": total_count,
            "database_type": "PostgreSQL" if settings.is_production else "SQLite",
            "environment": settings.ENVIRONMENT,
            "muscle_groups": muscle_counts,
            "difficulty_levels": difficulty_counts,
            "equipment_types": equipment_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")