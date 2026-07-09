from fastapi import Request
from sqlalchemy.orm import Session

from app.models.models import AuditLog


def create_audit_log(
    db: Session,
    request: Request,
    action: str,
    resource_type: str,
    user_id: int | None = None,
    resource_id: str | None = None,
) -> None:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(audit_log)
    