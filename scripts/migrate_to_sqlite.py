"""
Simple migration script: JSON -> SQLite (data/exercises.db)
Creates a table `exercises` with columns: id, name, slug, json_data
Run: python scripts/migrate_to_sqlite.py
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / 'data' / 'exercises.json'
DB_FILE = ROOT / 'data' / 'exercises.db'

print('Loading JSON from', DATA_FILE)
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

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

for item in data:
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
print('Migration finished. DB at', DB_FILE)
