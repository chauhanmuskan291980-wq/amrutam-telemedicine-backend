from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import admin, auth, consultations, doctors, payments
from app.core.database import Base, engine

tags_metadata = [
    {
        "name": "Auth",
        "description": "User registration, login, and current user APIs",
    },
    {
        "name": "Doctors",
        "description": "Doctor search and availability management",
    },
    {
        "name": "Consultations",
        "description": "Booking, consultation lifecycle, and prescriptions",
    },
    {
        "name": "Payments",
        "description": "Mock payment workflow",
    },
    {
        "name": "Admin",
        "description": "Admin analytics and audit logs",
    },
]


app = FastAPI(
    title="Amrutam Telemedicine Backend",
    description="Production-grade backend for Amrutam telemedicine workflows",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Amrutam Telemedicine Backend is running"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.get("/ready", tags=["Health"])
def readiness_check():
    return {"status": "ready"}


app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(consultations.router)
app.include_router(payments.router)
app.include_router(admin.router)

Instrumentator().instrument(app).expose(app)