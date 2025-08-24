#!/usr/bin/env python3
import json, csv, re
from pathlib import Path

PRIORITY_SOURCES = [
    'data/exercises_v2_with_images.json',
    'data/exercises_complete_from_images.json',
    'data/exercises_complete.json',
    'data/exercises.json'
]

def normalize(s):
    if not s: return ''
    s = s.lower()
    s = s.replace('_',' ').replace('-',' ')
    s = re.sub(r'[^a-z0-9ñáéíóúü ]+','',s)
    s = re.sub(r'\s+',' ',s).strip()
    return s

base = Path('data')
map_file = base / 'images_exercise_map.json'
if not map_file.exists():
    print('map file missing:', map_file)
    raise SystemExit(1)

map_data = json.loads(map_file.read_text(encoding='utf-8'))
clean_rows = []
clean_json = []

for item in map_data:
    img = item.get('image')
    fname = Path(img).stem
    fname_n = normalize(fname)
    matches = item.get('matches', [])
    best = None
    best_score = -1
    # prefer exact slug/name
    for m in matches:
        slug = normalize(m.get('slug') or '')
        name = normalize(m.get('name') or '')
        if slug and slug == fname_n:
            best = m; best_score = 999; break
        if name and name == fname_n:
            best = m; best_score = 998; break
    if not best:
        # compute overlap and pick highest; break ties by source priority
        for m in matches:
            slug = normalize(m.get('slug') or '')
            name = normalize(m.get('name') or '')
            words_fname = set(fname_n.split())
            words_name = set((slug + ' ' + name).split())
            score = len(words_fname & words_name)
            if score > best_score:
                best = m; best_score = score
            elif score == best_score and best is not None:
                # tie-break: prefer priority source
                try:
                    cur_prio = PRIORITY_SOURCES.index(m.get('source_file')) if m.get('source_file') in PRIORITY_SOURCES else len(PRIORITY_SOURCES)
                except ValueError:
                    cur_prio = len(PRIORITY_SOURCES)
                try:
                    best_prio = PRIORITY_SOURCES.index(best.get('source_file')) if best.get('source_file') in PRIORITY_SOURCES else len(PRIORITY_SOURCES)
                except Exception:
                    best_prio = len(PRIORITY_SOURCES)
                if cur_prio < best_prio:
                    best = m
    # if still none but there is at least one match, pick first
    if not best and matches:
        best = matches[0]
    # mark ambiguous if more than 1 match and best_score low (<1) and not exact
    ambiguous = False
    if len(matches) > 1 and best_score <= 0:
        ambiguous = True
    # produce clean row
    clean_rows.append({
        'image': img,
        'filename': fname,
        'match_source': best.get('source_file') if best else '',
        'match_id': best.get('id') if best else '',
        'match_slug': best.get('slug') if best else '',
        'match_name': best.get('name') if best else '',
        'ambiguous': ambiguous,
        'match_score': best_score
    })
    # augment original item with best_match
    new_item = {
        'image': img,
        'filename': fname,
        'best_match': best or None,
        'ambiguous': ambiguous,
    }
    clean_json.append(new_item)

# write CSV
csv_file = base / 'images_best_match_clean.csv'
with csv_file.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['image','filename','match_source','match_id','match_slug','match_name','ambiguous','match_score'])
    for r in clean_rows:
        w.writerow([r['image'], r['filename'], r['match_source'], r['match_id'], r['match_slug'], r['match_name'], r['ambiguous'], r['match_score']])

# write JSON
json_file = base / 'images_best_match_clean.json'
json_file.write_text(json.dumps(clean_json, ensure_ascii=False, indent=2), encoding='utf-8')

# update main map file to include best_match only
updated_map = []
for orig, clean in zip(map_data, clean_json):
    updated = orig.copy()
    updated['best_match'] = clean['best_match']
    updated['ambiguous'] = clean['ambiguous']
    # optionally reduce matches to only best
    updated['matches'] = [clean['best_match']] if clean['best_match'] else []
    updated_map.append(updated)

map_file.write_text(json.dumps(updated_map, ensure_ascii=False, indent=2), encoding='utf-8')
print('Wrote clean csv/json and updated', map_file)

# remove .gitkeep from images_list.json and images_list.txt
list_json = base / 'images_list.json'
list_txt = base / 'images_list.txt'
for p in [list_json, list_txt]:
    if p.exists():
        txt = p.read_text(encoding='utf-8')
        new = txt.replace('/static/images/piernas/.gitkeep\n','')
        new = new.replace('/static/images/piernas/.gitkeep','')
        p.write_text(new, encoding='utf-8')
        print('Cleaned .gitkeep from', p)

print('Done')
