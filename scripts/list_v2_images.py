#!/usr/bin/env python3
"""Listado y verificación de imágenes referenciadas por archivos v2.

Genera un informe local de las rutas encontradas en JSON y si los ficheros existen
localmente bajo `static/images/`.

Opcional: se puede usar `--check-remote` para verificar con peticiones HTTP si las URLs
remotas devuelven 200.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse

DATA_FILES = [
    'data/examples_v2.json',
    'data/exercises_v2_with_images.json',
]

STATIC_ROOT = Path('static/images')


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_image_urls(obj):
    urls = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'images' and isinstance(v, list):
                for it in v:
                    if isinstance(it, dict) and 'url' in it:
                        urls.append(it['url'])
            else:
                urls.extend(extract_image_urls(v))
    elif isinstance(obj, list):
        for item in obj:
            urls.extend(extract_image_urls(item))
    return urls


def to_local_path(url):
    # If it's a full URL, strip the domain and leading slash
    parsed = urlparse(url)
    if parsed.scheme in ('http', 'https'):
        path = parsed.path
    else:
        path = url
    # remove leading slash
    path = path.lstrip('/')
    return Path(path)


def main(check_remote=False):
    found = []
    for f in DATA_FILES:
        if not os.path.exists(f):
            print(f"Warning: data file {f} no encontrado.")
            continue
        data = load_json(f)
        urls = extract_image_urls(data)
        for u in urls:
            local = to_local_path(u)
            exists = (Path(local).exists() and Path(local).is_file())
            # if the path is not under static/images, also try resolving relative
            if not exists and not str(local).startswith('static/'):
                alt = Path('static') / Path(local).name
                if alt.exists():
                    exists = True
                    local = alt
            found.append((f, u, str(local), exists))

    # print report
    print("Imagenes encontradas en JSON v2:\n")
    for src, url, local, exists in found:
        print(f"- {url} (from {src}) -> local: {local} -> {'OK' if exists else 'MISSING'})")

    if check_remote:
        try:
            import requests
        except Exception:
            print('\nPara check remoto requiere `requests`. Instalar con: pip install requests')
            return
        print('\nVerificando URLs remotas HTTP...')
        for src, url, local, exists in found:
            if url.startswith('http'):
                try:
                    r = requests.head(url, timeout=5)
                    ok = r.status_code == 200
                except Exception as e:
                    ok = False
                print(f"- {url} -> HTTP 200: {ok}")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check-remote', action='store_true')
    args = p.parse_args()
    main(check_remote=args.check_remote)
