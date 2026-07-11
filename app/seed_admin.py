from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.models import Profile, User, UserRole


db = SessionLocal()

email = "admin@example.com"

existing_admin = db.query(User).filter(User.email == email).first()

if existing_admin:
    print("Admin already exists")
else:
    admin_user = User(
        email=email,
        phone="9876543212",
        password_hash=hash_password("Password123"),
        role=UserRole.ADMIN,
        is_active=True,
    )

    db.add(admin_user)
    db.flush()

    profile = Profile(
        user_id=admin_user.id,
        full_name="System Admin",
    )

    db.add(profile)
    db.commit()

    print("Admin created successfully")

db.close()
