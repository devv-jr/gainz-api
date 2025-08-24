#!/usr/bin/env python3
"""Mapea imágenes en data/images_list.json a ejercicios en los JSON de datos.
Genera `data/images_exercise_map.json` con el resultado.
"""
import json
import re
from pathlib import Path

DATA_FILES = [
    'data/examples_v2.json',
    'data/exercises_v2_with_images.json',
    'data/exercises.json',
    'data/exercises_complete.json',
    'data/exercises_complete_from_images.json',
]

IMAGES_LIST = 'data/images_list.json'
OUTPUT = 'data/images_exercise_map.json'


def load_json_safe(p):
    try:
        return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception:
        return []


def normalize(s):
    if not isinstance(s, str):
        return ''
    s = s.lower()
    s = s.replace('_', ' ')
    s = s.replace('-', ' ')
    s = re.sub(r"[^a-z0-9ñáéíóúü ]+", '', s)
    s = re.sub(r"\s+", ' ', s).strip()
    return s


# gather exercises
exercises = []
for f in DATA_FILES:
    items = load_json_safe(f)
    if not isinstance(items, list):
        continue
    for it in items:
        # try to extract id, slug, name
        eid = it.get('id') if isinstance(it, dict) else None
        slug = it.get('slug') if isinstance(it, dict) else None
        name = it.get('name') if isinstance(it, dict) else None
        # some v1 items use 'name' and not slug
        exercises.append({
            'source_file': f,
            'id': eid,
            'slug': slug,
            'name': name,
            'raw': it
        })

# load images
images = load_json_safe(IMAGES_LIST)
if not isinstance(images, list):
    images = []

report = []
for img in images:
    # img like '/static/images/abs/crunch.png'
    path = img
    fname = Path(path).stem  # 'crunch'
    fname_norm = normalize(fname)
    matches = []
    for ex in exercises:
        slug = ex.get('slug') or ''
        name = ex.get('name') or ''
        slug_norm = normalize(slug)
        name_norm = normalize(name)
        # matching rules
        matched = False
        if slug_norm and (fname_norm == slug_norm or fname_norm in slug_norm or slug_norm in fname_norm):
            matched = True
        if not matched and name_norm and (fname_norm == name_norm or fname_norm in name_norm or name_norm in fname_norm):
            matched = True
        # also check if filename contains key words from name (like 'crunch-oblicuo' vs 'Crunch oblicuo')
        if not matched:
            # compare words sets
            fname_words = set(fname_norm.split())
            name_words = set(name_norm.split())
            if fname_words and name_words and fname_words & name_words:
                # require at least one overlap
                matched = True
        if matched:
            matches.append({
                'source_file': ex['source_file'],
                'id': ex['id'],
                'slug': ex['slug'],
                'name': ex['name']
            })
    report.append({
        'image': img,
        'filename': fname,
        'matches': matches
    })

# write report
Path(OUTPUT).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

# print simple summary
matched = sum(1 for r in report if r['matches'])
print(f"Images processed: {len(report)}, matched: {matched}, unmatched: {len(report)-matched}")
print(f"Report written to {OUTPUT}")
