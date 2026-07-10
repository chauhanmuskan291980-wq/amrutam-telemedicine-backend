import hashlib
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.models import (
    AvailabilitySlot,
    Consultation,
    ConsultationStatus,
    Doctor,
    IdempotencyKey,
    Payment,
    Prescription,
    SlotStatus,
    User,
    UserRole,
)
from app.schemas.schemas import (
    BookingRequest,
    ConsultationResponse,
    PrescriptionCreateRequest,
    PrescriptionResponse,
)
from app.utils.audit import create_audit_log
from app.core.rate_limiter import limiter

router = APIRouter(prefix="/consultations", tags=["Consultations"])


@router.post("/book", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def book_consultation(
    payload: BookingRequest,
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PATIENT)),
):
    request_hash = hashlib.sha256(
        f"{current_user.id}:{payload.slot_id}:{payload.reason}".encode()
    ).hexdigest()

    existing_key = (
        db.query(IdempotencyKey)
        .filter(
            IdempotencyKey.key == idempotency_key,
            IdempotencyKey.user_id == current_user.id,
        )
        .first()
    )

    if existing_key:
        if existing_key.request_hash != request_hash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Idempotency key reused with different request body",
            )

        return existing_key.response_body

    try:
        slot = (
            db.query(AvailabilitySlot)
            .filter(AvailabilitySlot.id == payload.slot_id)
            .with_for_update()
            .first()
        )

        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found",
            )

        if slot.status != SlotStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slot is already booked or unavailable",
            )

        doctor = db.query(Doctor).filter(Doctor.id == slot.doctor_id).first()

        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found",
            )

        slot.status = SlotStatus.BOOKED
        slot.version += 1

        consultation = Consultation(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            slot_id=slot.id,
            status=ConsultationStatus.BOOKED,
            reason=payload.reason,
        )

        db.add(consultation)
        db.flush()

        payment = Payment(
            consultation_id=consultation.id,
            patient_id=current_user.id,
            amount=Decimal(doctor.consultation_fee or 0),
        )
        db.add(payment)

        response_body = {
            "id": consultation.id,
            "patient_id": consultation.patient_id,
            "doctor_id": consultation.doctor_id,
            "slot_id": consultation.slot_id,
            "status": consultation.status.value,
            "reason": consultation.reason,
        }

        idempotency_record = IdempotencyKey(
            key=idempotency_key,
            user_id=current_user.id,
            request_hash=request_hash,
            response_body=response_body,
        )
        db.add(idempotency_record)

        create_audit_log(
            db=db,
            request=request,
            action="CONSULTATION_BOOKED",
            resource_type="CONSULTATION",
            user_id=current_user.id,
            resource_id=str(consultation.id),
        )

        db.commit()
        db.refresh(consultation)

        return consultation

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot booking conflict. Please choose another slot.",
        )


@router.get("", response_model=list[ConsultationResponse])
def list_consultations(
    status_filter: ConsultationStatus | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Consultation)

    if current_user.role == UserRole.PATIENT:
        query = query.filter(Consultation.patient_id == current_user.id)

    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor:
            return []
        query = query.filter(Consultation.doctor_id == doctor.id)

    if status_filter:
        query = query.filter(Consultation.status == status_filter)

    return query.order_by(Consultation.created_at.desc()).all()


@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    allowed = False

    if current_user.role == UserRole.ADMIN:
        allowed = True

    if current_user.role == UserRole.PATIENT and consultation.patient_id == current_user.id:
        allowed = True

    if current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor and consultation.doctor_id == doctor.id:
            allowed = True

    if not allowed:
        raise HTTPException(status_code=403, detail="Access denied")

    return consultation


@router.patch("/{consultation_id}/start", response_model=ConsultationResponse)
def start_consultation(
    consultation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DOCTOR)),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()

    if not doctor or not consultation or consultation.doctor_id != doctor.id:
        raise HTTPException(status_code=404, detail="Consultation not found")

    if consultation.status != ConsultationStatus.BOOKED:
        raise HTTPException(status_code=400, detail="Only booked consultation can be started")

    consultation.status = ConsultationStatus.ONGOING

    create_audit_log(
        db=db,
        request=request,
        action="CONSULTATION_STARTED",
        resource_type="CONSULTATION",
        user_id=current_user.id,
        resource_id=str(consultation.id),
    )

    db.commit()
    db.refresh(consultation)
    return consultation


@router.patch("/{consultation_id}/complete", response_model=ConsultationResponse)
def complete_consultation(
    consultation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DOCTOR)),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()

    if not doctor or not consultation or consultation.doctor_id != doctor.id:
        raise HTTPException(status_code=404, detail="Consultation not found")

    if consultation.status != ConsultationStatus.ONGOING:
        raise HTTPException(status_code=400, detail="Only ongoing consultation can be completed")

    consultation.status = ConsultationStatus.COMPLETED

    create_audit_log(
        db=db,
        request=request,
        action="CONSULTATION_COMPLETED",
        resource_type="CONSULTATION",
        user_id=current_user.id,
        resource_id=str(consultation.id),
    )

    db.commit()
    db.refresh(consultation)
    return consultation


@router.patch("/{consultation_id}/cancel", response_model=ConsultationResponse)
def cancel_consultation(
    consultation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    if current_user.role == UserRole.PATIENT and consultation.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    consultation.status = ConsultationStatus.CANCELLED

    slot = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == consultation.slot_id).first()
    if slot:
        slot.status = SlotStatus.AVAILABLE

    create_audit_log(
        db=db,
        request=request,
        action="CONSULTATION_CANCELLED",
        resource_type="CONSULTATION",
        user_id=current_user.id,
        resource_id=str(consultation.id),
    )

    db.commit()
    db.refresh(consultation)

    return consultation


@router.post("/{consultation_id}/prescription", response_model=PrescriptionResponse)
def create_prescription(
    consultation_id: int,
    payload: PrescriptionCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DOCTOR)),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()

    if not doctor or not consultation or consultation.doctor_id != doctor.id:
        raise HTTPException(status_code=404, detail="Consultation not found")

    existing = (
        db.query(Prescription)
        .filter(Prescription.consultation_id == consultation_id)
        .first()
    )

    if existing:
        raise HTTPException(status_code=409, detail="Prescription already exists")

    prescription = Prescription(
        consultation_id=consultation.id,
        doctor_id=doctor.id,
        patient_id=consultation.patient_id,
        medicines=payload.medicines,
        notes=payload.notes,
    )

    db.add(prescription)
    db.flush()

    create_audit_log(
        db=db,
        request=request,
        action="PRESCRIPTION_CREATED",
        resource_type="PRESCRIPTION",
        user_id=current_user.id,
        resource_id=str(prescription.id),
    )

    db.commit()
    db.refresh(prescription)

    return prescription


@router.get("/{consultation_id}/prescription", response_model=PrescriptionResponse)
def get_prescription(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prescription = (
        db.query(Prescription)
        .filter(Prescription.consultation_id == consultation_id)
        .first()
    )

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    if current_user.role == UserRole.PATIENT and prescription.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or prescription.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Access denied")

    return prescription