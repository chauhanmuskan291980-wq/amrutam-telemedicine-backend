from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.models import Doctor, Profile, User, UserRole
from app.schemas.schemas import LoginRequest, TokenResponse, UserRegisterRequest, UserResponse
from app.utils.audit import create_audit_log

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == payload.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    if payload.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin users cannot self-register",
        )

    user = User(
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )

    db.add(user)
    db.flush()

    profile = Profile(
        user_id=user.id,
        full_name=payload.full_name,
    )
    db.add(profile)

    if payload.role == UserRole.DOCTOR:
        if not payload.specialization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specialization is required for doctor registration",
            )

        doctor = Doctor(
            user_id=user.id,
            specialization=payload.specialization,
            experience_years=payload.experience_years or 0,
            consultation_fee=payload.consultation_fee or 0,
        )
        db.add(doctor)

    create_audit_log(
        db=db,
        request=request,
        action="USER_REGISTERED",
        resource_type="USER",
        user_id=user.id,
        resource_id=str(user.id),
    )

    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(subject=str(user.id))

    create_audit_log(
        db=db,
        request=request,
        action="USER_LOGIN",
        resource_type="USER",
        user_id=user.id,
        resource_id=str(user.id),
    )
    db.commit()

    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
