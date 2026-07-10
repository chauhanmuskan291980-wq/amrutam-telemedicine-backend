from fastapi import APIRouter, Depends , Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.models import AuditLog, Consultation, Doctor, Payment, Prescription, User, UserRole
from app.schemas.schemas import AdminAnalyticsResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/analytics/summary", response_model=AdminAnalyticsResponse)
def analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return AdminAnalyticsResponse(
        total_users=db.query(User).count(),
        total_doctors=db.query(Doctor).count(),
        total_consultations=db.query(Consultation).count(),
        total_prescriptions=db.query(Prescription).count(),
        total_payments=db.query(Payment).count(),
    )


@router.get("/audit-logs")
def get_audit_logs(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
