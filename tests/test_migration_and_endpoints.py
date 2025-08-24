import os
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'data' / 'exercises.db'
DATA = ROOT / 'data' / 'exercises.json'


def test_db_exists():
    assert DB.exists()


def test_db_has_rows():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM exercises')
    n = cur.fetchone()[0]
    conn.close()
    assert n > 0


def test_v1_readable():
    with open(DATA, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) >= 1
