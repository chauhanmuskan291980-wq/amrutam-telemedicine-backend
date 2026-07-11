from fastapi import APIRouter, Depends, HTTPException, Request, status , Query
from sqlalchemy.orm import Session
from app.core.cache import delete_cache_pattern, get_cache, set_cache
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.models import AvailabilitySlot, Doctor, SlotStatus, User, UserRole
from app.schemas.schemas import (
    AvailabilityCreateRequest,
    AvailabilityResponse,
    DoctorResponse,
)
from app.utils.audit import create_audit_log

router = APIRouter(prefix="/doctors", tags=["Doctors"])



@router.get("", response_model=list[DoctorResponse])
def search_doctors(
    specialization: str | None = Query(default=None, max_length=100),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    cache_key = (
        f"doctor_search:"
        f"specialization={specialization}:"
        f"min_rating={min_rating}:"
        f"limit={limit}:"
        f"offset={offset}"
    )

    cached_result = get_cache(cache_key)

    if cached_result is not None:
        return cached_result

    query = db.query(Doctor)

    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))

    if min_rating is not None:
        query = query.filter(Doctor.rating >= min_rating)

    doctors = query.offset(offset).limit(limit).all()

    result = [
        {
            "id": doctor.id,
            "user_id": doctor.user_id,
            "specialization": doctor.specialization,
            "experience_years": doctor.experience_years,
            "consultation_fee": doctor.consultation_fee,
            "rating": doctor.rating,
            "is_verified": doctor.is_verified,
        }
        for doctor in doctors
    ]

    set_cache(cache_key, result, ttl_seconds=60)

    return result


@router.post("/availability", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
def create_availability(
    payload: AvailabilityCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DOCTOR)),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    if payload.end_time <= payload.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be greater than start time",
        )

    slot = AvailabilitySlot(
        doctor_id=doctor.id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=SlotStatus.AVAILABLE,
    )

    db.add(slot)
    db.flush()

    create_audit_log(
        db=db,
        request=request,
        action="DOCTOR_SLOT_CREATED",
        resource_type="AVAILABILITY_SLOT",
        user_id=current_user.id,
        resource_id=str(slot.id),
    )

    db.commit()
    db.refresh(slot)

    delete_cache_pattern("doctor_search:*")

    return slot


@router.get("/{doctor_id}/slots", response_model=list[AvailabilityResponse])
def get_doctor_slots(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(AvailabilitySlot)
        .filter(
            AvailabilitySlot.doctor_id == doctor_id,
            AvailabilitySlot.status == SlotStatus.AVAILABLE,
        )
        .order_by(AvailabilitySlot.start_time.asc())
        .all()
    )