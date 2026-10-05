import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers.emergencies import router as emergencies_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SafetyU API",
    description="Emergency alert API for the SafetyU web app and ESP32 devices.",
    version="1.0.0",
)

origins_raw = os.getenv("CORS_ORIGINS", "*")
origins = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(emergencies_router)


@app.get("/")
def root():
    return {
        "name": "SafetyU API",
        "status": "online",
        "docs": "/docs",
        "emergencies": "/api/emergencies",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
