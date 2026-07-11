from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes import admin as admin_routes
from app.api.routes import auth as auth_routes
from app.api.routes import consultations as consultation_routes
from app.api.routes import doctors as doctor_routes
from app.api.routes import payments as payment_routes
from app.core.database import Base, engine
from app.core.rate_limiter import limiter


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
    {
        "name": "Health",
        "description": "Health, readiness, Redis, and metrics checks",
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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/health/redis", tags=["Health"])
def redis_health_check():
    from app.core.cache import redis_client
    from app.core.config import settings

    if not settings.redis_enabled:
        return {
            "status": "redis disabled",
            "mode": "in-memory cache",
        }

    try:
        if redis_client:
            redis_client.ping()
            return {"status": "redis healthy"}

        return {"status": "redis unavailable"}

    except Exception as exc:
        return {
            "status": "redis unavailable",
            "error": str(exc),
        }


app.include_router(auth_routes.router)
app.include_router(doctor_routes.router)
app.include_router(consultation_routes.router)
app.include_router(payment_routes.router)
app.include_router(admin_routes.router)

Instrumentator().instrument(app).expose(app)