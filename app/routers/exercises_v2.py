from fastapi import APIRouter, HTTPException, Query, Depends, Header
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from datetime import datetime
import sqlite3
from app.auth import verify_token

DB_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "exercises.db"

router = APIRouter()

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "exercises.json"

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
    sets: Optional[int]
    reps_min: Optional[int]
    reps_max: Optional[int]
    rest_sec: Optional[int]

class ExerciseV2(BaseModel):
    id: int
    slug: str
    name: str
    summary: Optional[str]
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
    # fallback to DB if available
    if DB_FILE.exists():
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute('SELECT json_data FROM exercises')
        rows = cur.fetchall()
        conn.close()
        return [json.loads(r[0]) for r in rows]
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def slugify(name: str) -> str:
    return name.lower().replace(' ', '-').replace("\u00f3", "o").replace("\u00e1", "a").replace("\u00e9", "e").replace("\u00ed", "i").replace("\u00fa", "u")


def transform(old: dict) -> dict:
    # Minimal transform: map old fields into v2 structure
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


def require_auth(authorization: Optional[str] = Header(None)):
    # Expect Authorization: Bearer <token>
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    token = parts[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.post("/", response_model=ExerciseV2, status_code=201)
def create_exercise_v2(ex: ExerciseV2, auth=Depends(require_auth)):
    # insert into DB
    if not DB_FILE.exists():
        raise HTTPException(status_code=500, detail="DB not found; run migration")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO exercises (id, name, slug, primary_muscle, difficulty, json_data, created_at) VALUES (?,?,?,?,?,?,?)', (
        ex.id, ex.name, ex.slug, ex.primary_muscle, ex.difficulty, json.dumps(ex.dict(), ensure_ascii=False), ex.created_at or datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    return ex


@router.put("/{exercise_id}", response_model=ExerciseV2)
def update_exercise_v2(exercise_id: int, ex: ExerciseV2, auth=Depends(require_auth)):
    if not DB_FILE.exists():
        raise HTTPException(status_code=500, detail="DB not found; run migration")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id FROM exercises WHERE id=?', (exercise_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail='Not found')
    cur.execute('UPDATE exercises SET name=?, slug=?, primary_muscle=?, difficulty=?, json_data=?, created_at=? WHERE id=?', (
        ex.name, ex.slug, ex.primary_muscle, ex.difficulty, json.dumps(ex.dict(), ensure_ascii=False), ex.created_at or datetime.utcnow().isoformat(), exercise_id
    ))
    conn.commit()
    conn.close()
    return ex


@router.delete("/{exercise_id}", status_code=204)
def delete_exercise_v2(exercise_id: int, auth=Depends(require_auth)):
    if not DB_FILE.exists():
        raise HTTPException(status_code=500, detail="DB not found; run migration")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('DELETE FROM exercises WHERE id=?', (exercise_id,))
    conn.commit()
    conn.close()
    return


@router.post("/migrate", status_code=200)
def migrate_now(auth=Depends(require_auth)):
    # programmatic migration using the existing script logic
    if DB_FILE.exists():
        return {"status": "already_migrated"}
    # read JSON and write to DB
    raw = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY,
        name TEXT,
        slug TEXT,
        primary_muscle TEXT,
        difficulty TEXT,
        json_data TEXT,
        created_at TEXT
    )
    ''')
    from datetime import datetime
    for item in raw:
        slug = item.get('name','').lower().replace(' ', '-')
        cur.execute('INSERT OR REPLACE INTO exercises (id, name, slug, primary_muscle, difficulty, json_data, created_at) VALUES (?,?,?,?,?,?,?)', (
            item.get('id'),
            item.get('name'),
            slug,
            item.get('muscle'),
            item.get('difficulty'),
            json.dumps(item, ensure_ascii=False),
            datetime.utcnow().isoformat()
        ))
    conn.commit()
    conn.close()
    return {"status": "migrated", "count": len(raw)}
