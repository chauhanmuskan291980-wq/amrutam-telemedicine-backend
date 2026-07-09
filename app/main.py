from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Amrutam Telemedicine Backend",
    description="Production-grade backend for telemedicine workflows",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Amrutam Telemedicine Backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/ready")
def readiness_check():
    return {
        "status": "ready"
    }


Instrumentator().instrument(app).expose(app)