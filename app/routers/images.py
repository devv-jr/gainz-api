from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import shutil

router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent.parent / "static" / "images"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename")
    dest = STATIC_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"url": f"/static/images/{file.filename}"}

@router.get("/static/{image_name}")
async def get_image(image_name: str):
    path = STATIC_DIR / image_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)
