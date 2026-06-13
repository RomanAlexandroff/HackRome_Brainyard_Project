from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .mock_data import fresh_dashboard
from .models import DashboardData, FieldEvent, FieldEventDraft, SensorReading, Study, StudyDraft
from .openai_service import openai_enabled
from .store import VineyardStore

app = FastAPI(
    title="Brainyard Backend",
    description="Hackathon MVP backend for AI-assisted vineyard monitoring and decision support.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = VineyardStore(fresh_dashboard())


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "brainyard-backend",
        "ai_enabled": openai_enabled(),
    }


@app.get("/api/dashboard", response_model=DashboardData)
def get_dashboard() -> DashboardData:
    return store.get_dashboard()


@app.get("/api/sensor/latest", response_model=Optional[SensorReading])
def get_latest_sensor_reading():
    return store.get_latest_sensor_reading()


@app.post("/api/sensor/readings", response_model=SensorReading)
def ingest_sensor_reading(reading: SensorReading) -> SensorReading:
    return store.ingest_sensor_reading(reading)


@app.post("/api/field-events", response_model=FieldEvent)
def create_field_event(draft: FieldEventDraft) -> FieldEvent:
    return store.create_field_event(draft)


@app.post("/api/studies", response_model=Study)
def create_study(draft: StudyDraft) -> Study:
    return store.create_study(draft)
