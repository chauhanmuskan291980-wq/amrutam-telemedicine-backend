from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.models.models import ConsultationStatus, PaymentStatus, SlotStatus, UserRole


class UserRegisterRequest(BaseModel):
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8, max_length=72)
    full_name: str
    role: UserRole = UserRole.PATIENT
    specialization: str | None = None
    experience_years: int | None = 0
    consultation_fee: Decimal | None = 0


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    phone: str | None
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class DoctorResponse(BaseModel):
    id: int
    user_id: int
    specialization: str
    experience_years: int
    consultation_fee: Decimal
    rating: Decimal
    is_verified: bool

    model_config = {"from_attributes": True}


class AvailabilityCreateRequest(BaseModel):
    start_time: datetime
    end_time: datetime


class AvailabilityResponse(BaseModel):
    id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    status: SlotStatus

    model_config = {"from_attributes": True}


class BookingRequest(BaseModel):
    slot_id: int
    reason: str | None = None


class ConsultationResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    slot_id: int
    status: ConsultationStatus
    reason: str | None

    model_config = {"from_attributes": True}


class PrescriptionCreateRequest(BaseModel):
    medicines: list[dict[str, Any]]
    notes: str | None = None


class PrescriptionResponse(BaseModel):
    id: int
    consultation_id: int
    doctor_id: int
    patient_id: int
    medicines: list[dict[str, Any]]
    notes: str | None

    model_config = {"from_attributes": True}


class PaymentResponse(BaseModel):
    id: int
    consultation_id: int | None
    patient_id: int
    amount: Decimal
    status: PaymentStatus

    model_config = {"from_attributes": True}


class MockPaymentConfirmRequest(BaseModel):
    payment_id: int
    status: PaymentStatus = PaymentStatus.PAID


class AdminAnalyticsResponse(BaseModel):
    total_users: int
    total_doctors: int
    total_consultations: int
    total_prescriptions: int
    total_payments: int