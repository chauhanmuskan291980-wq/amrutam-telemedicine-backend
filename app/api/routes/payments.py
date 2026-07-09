from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import Payment, User, UserRole
from app.schemas.schemas import MockPaymentConfirmRequest, PaymentResponse

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if current_user.role == UserRole.PATIENT and payment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return payment


@router.post("/mock-confirm", response_model=PaymentResponse)
def mock_confirm_payment(
    payload: MockPaymentConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = db.query(Payment).filter(Payment.id == payload.payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if current_user.role == UserRole.PATIENT and payment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    payment.status = payload.status

    db.commit()
    db.refresh(payment)

    return payment