#!/usr/bin/env python3
import json, csv, re
from pathlib import Path

def normalize(s):
    if not s: return ''
    s = s.lower()
    s = s.replace('_',' ').replace('-',' ')
    s = re.sub(r'[^a-z0-9ñáéíóúü ]+','',s)
    s = re.sub(r'\s+',' ',s).strip()
    return s

map_file = Path('data/images_exercise_map.json')
csv_file = Path('data/images_best_match.csv')
report_file = Path('data/images_ambiguity_report.json')

map_data = json.loads(map_file.read_text(encoding='utf-8')) if map_file.exists() else []
# load csv into dict by image
csv_map = {}
if csv_file.exists():
    import csv
    with csv_file.open(encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            csv_map[row['image']] = row

report = []
for item in map_data:
    img = item.get('image')
    fname = Path(img).stem
    fname_n = normalize(fname)
    matches = item.get('matches', [])
    num_matches = len(matches)
    # determine best from csv
    csvrow = csv_map.get(img)
    best_slug = (csvrow.get('match_slug') or '').strip() if csvrow else ''
    best_name = (csvrow.get('match_name') or '').strip() if csvrow else ''
    best_id = csvrow.get('match_id') if csvrow else None
    best_source = csvrow.get('match_source') if csvrow else None
    # compute overlap score for best
    best_norm = normalize(best_slug or best_name)
    score = 0
    if best_norm:
        score = len(set(fname_n.split()) & set(best_norm.split()))
    exact = (best_norm == fname_n)
    ambiguous = False
    reasons = []
    if num_matches > 1:
        reasons.append('multiple_matches')
    if score <= 1 and not exact:
        reasons.append('low_overlap')
    if reasons:
        ambiguous = True
    report.append({
        'image': img,
        'filename': fname,
        'num_matches': num_matches,
        'best_source': best_source,
        'best_id': best_id,
        'best_slug': best_slug,
        'best_name': best_name,
        'overlap_score': score,
        'exact_match': exact,
        'ambiguous': ambiguous,
        'reasons': reasons
    })

report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('Wrote', report_file)
# print summary counts
amb_count = sum(1 for r in report if r['ambiguous'])
print('Total images:', len(report), 'Ambiguous:', amb_count)
