import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routers import exercises

load_dotenv()
# Leer ORIGINS como string y parsear una sola vez
origins_env = os.getenv("ORIGINS", "")
origins = [url.strip() for url in origins_env.split(",") if url.strip()]

app = FastAPI(
    title="GainzAPI",
    description="API de ejercicios de gimnasio para GAINZAPP",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
