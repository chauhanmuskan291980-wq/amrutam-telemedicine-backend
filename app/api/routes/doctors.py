from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

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
    specialization: str | None = None,
    min_rating: float | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Doctor)

    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))

    if min_rating is not None:
        query = query.filter(Doctor.rating >= min_rating)

    return query.offset(offset).limit(limit).all()


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