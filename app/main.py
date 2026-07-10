from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import admin, auth, consultations, doctors, payments
from app.core.database import Base, engine
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.models import Profile, User, UserRole
from fastapi.middleware.cors import CORSMiddleware

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

 
Base.metadata.create_all(bind=engine)

db = SessionLocal()

email = "admin@example.com"

existing_admin = db.query(User).filter(User.email == email).first()

if existing_admin:
    print("Admin already exists")
else:
    admin = User(
        email=email,
        phone="9876543212",
        password_hash=hash_password("Password123"),
        role=UserRole.ADMIN,
        is_active=True,
    )

    db.add(admin)
    db.flush()

    profile = Profile(
        user_id=admin.id,
        full_name="System Admin",
    )

    db.add(profile)
    db.commit()

    print("Admin created successfully")

db.close()


app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(consultations.router)
app.include_router(payments.router)
app.include_router(admin.router)

Instrumentator().instrument(app).expose(app)