from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path

class Exercise(BaseModel):
    id: int
    name: str
    muscle: str
    equipment: str
    difficulty: str
    instructions: str

router = APIRouter()

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "exercises.json"

def load_exercises():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_exercises(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

exercises_db = load_exercises()

@router.get("/", response_model=List[Exercise])
def get_exercises(muscle: Optional[str] = None, equipment: Optional[str] = None, difficulty: Optional[str] = None):
    results = exercises_db
    if muscle:
        results = [e for e in results if e['muscle'].lower() == muscle.lower()]
    if equipment:
        results = [e for e in results if e['equipment'].lower() == equipment.lower()]
    if difficulty:
        results = [e for e in results if e['difficulty'].lower() == difficulty.lower()]
    return results

@router.get("/{exercise_id}", response_model=Exercise)
def get_exercise(exercise_id: int):
    for e in exercises_db:
        if e['id'] == exercise_id:
            return e
    raise HTTPException(status_code=404, detail="Exercise not found")

@router.post("/", response_model=Exercise, status_code=201)
def create_exercise(ex: Exercise):
    if any(e['id'] == ex.id for e in exercises_db):
        raise HTTPException(status_code=400, detail="ID already exists")
    exercises_db.append(ex.dict())
    save_exercises(exercises_db)
    return ex

@router.put("/{exercise_id}", response_model=Exercise)
def update_exercise(exercise_id: int, ex: Exercise):
    for idx, e in enumerate(exercises_db):
        if e['id'] == exercise_id:
            exercises_db[idx] = ex.dict()
            save_exercises(exercises_db)
            return ex
    raise HTTPException(status_code=404, detail="Exercise not found")

@router.delete("/{exercise_id}", status_code=204)
def delete_exercise(exercise_id: int):
    for idx, e in enumerate(exercises_db):
        if e['id'] == exercise_id:
            del exercises_db[idx]
            save_exercises(exercises_db)
            return
    raise HTTPException(status_code=404, detail="Exercise not found")
