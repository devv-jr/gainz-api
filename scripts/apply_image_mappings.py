#!/usr/bin/env python3
"""
Aplica `data/images_best_match.csv` a los JSON de ejercicios: añade o actualiza
la propiedad `images` con [{'url': '/static/images/..'}] en el ejercicio correspondiente.

Modifica in-place los ficheros referenciados en la columna match_source.
"""
import csv
import json
from pathlib import Path

CSV = Path('data/images_best_match.csv')

if not CSV.exists():
    print('CSV not found:', CSV)
    raise SystemExit(1)

updates = {}
with CSV.open(encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        image = row['image'].strip()
        src = row['match_source'].strip()
        mid = row['match_id'].strip()
        if not src or not mid:
            continue
        try:
            mid_i = int(mid)
        except Exception:
            continue
        updates.setdefault(src, []).append((mid_i, image))

# Apply updates per source file
for src, entries in updates.items():
    path = Path(src)
    if not path.exists():
        print('Source JSON not found:', src)
        continue
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        print('Failed to read JSON', src, e)
        continue
    if not isinstance(data, list):
        print('Source JSON is not a list, skipping:', src)
        continue
    id_map = {item.get('id'): item for item in data if isinstance(item, dict) and 'id' in item}
    changed = False
    for mid, image in entries:
        item = id_map.get(mid)
        if not item:
            # try to find by slug or name
            for it in data:
                if not isinstance(it, dict):
                    continue
                if it.get('id') == mid:
                    item = it; break
            if not item:
                print(f'ID {mid} not found in {src}')
                continue
        # ensure images list exists
        images = item.get('images')
        if not images:
            item['images'] = [{'url': image}]
            changed = True
        else:
            # check if url already present
            urls = [im.get('url') for im in images if isinstance(im, dict) and 'url' in im]
            if image not in urls:
                images.append({'url': image})
                changed = True
    if changed:
        # backup
        bak = path.with_suffix(path.suffix + '.bak')
        bak.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Updated', src, 'backup at', bak)
    else:
        print('No changes for', src)

print('Done')
