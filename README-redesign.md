Gainz API — Redesign branch changes

Resumen rápido:
- API versionada: `/v1/exercises` (legacy) y `/v2/exercises` (enriquecida).
- Persistencia v2: SQLite en `data/exercises.db`. Ejecuta `python scripts/migrate_to_sqlite.py` si no existe.
- Imágenes: subida a `/images/upload` y servidas desde `/static/images/` en desarrollo.
- Auth: JWT con `app/auth.py` (clave en código para desarrollo).

Cómo ejecutar localmente:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/migrate_to_sqlite.py
.venv/bin/uvicorn app.main:app --reload
```

Tests:
```bash
source .venv/bin/activate
pytest -q
```

Notas:
- Para producción no sirvas imágenes desde el servidor: usa S3 + CDN. Cambia SECRET_KEY.
