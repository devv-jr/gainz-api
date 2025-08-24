import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routers import exercises
from app.routers import exercises_v2
from app.config import setup_logging, settings

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Leer ORIGINS como string y parsear una sola vez
origins_env = os.getenv("ORIGINS", "")
origins = [url.strip() for url in origins_env.split(",") if url.strip()]

app = FastAPI(
    title="GainzAPI",
    description="API de ejercicios de gimnasio para GAINZAPP",
    version="1.0.0"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejadores de errores globales
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP {exc.status_code} error: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()} - Path: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "status_code": 422}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)} - Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

app.include_router(exercises.router, prefix="/v1/exercises", tags=["Exercises v1"])
app.include_router(exercises_v2.router, prefix="/v2/exercises", tags=["Exercises v2"])

@app.get("/", tags=["Info"])
def root():
    return {"message": "GainzAPI: v1 and v2 available", "v1": "/v1/exercises/", "v2": "/v2/exercises/"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "GainzAPI"}

# Mount static directory for development image serving
app.mount("/static", StaticFiles(directory="static"), name="static")

# include image router
from app.routers import images
app.include_router(images.router, prefix="/images", tags=["Images"])
from app.routers import auth_router
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
