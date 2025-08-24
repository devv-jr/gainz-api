#!/usr/bin/env python3
import sqlite3
import json
from pathlib import Path

def export_exercises():
    # Conectar a la base de datos SQLite
    db_path = Path(__file__).parent.parent / "data" / "exercises.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exercises ORDER BY id")
    exercises = []
    
    for row in cursor.fetchall():
        exercise = dict(row)
        exercises.append(exercise)
    
    conn.close()
    
    # Guardar en JSON
    json_path = Path(__file__).parent.parent / "data" / "exercises_complete.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(exercises, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"Exported {len(exercises)} exercises to {json_path}")

if __name__ == "__main__":
    export_exercises()