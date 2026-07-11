import re
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.models import ConsultationStatus, PaymentStatus, SlotStatus, UserRole
from datetime import datetime, timezone



def make_utc_naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


class UserRegisterRequest(BaseModel):
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=2,max_length=255)
    role: UserRole = UserRole.PATIENT
    specialization: str | None = None
    experience_years: int | None = Field(default=0, ge=0, le=60)
    consultation_fee: Decimal | None = Field(default=0, ge=0, le=100000)

    @field_validator("password")
    @classmethod
    def validate_password(cls , value:str) -> str:
        if not re.search(r"[A-Za-z]",value):
            raise ValueError("Password must contain at least one letter")
        

        if not re.search(r"\d",value):
            raise ValueError("Password must contain at least one number")
        
        return value
    

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
     if value is None:
        return value

     if not re.fullmatch(r"^[6-9][0-9]{9}$", value):
        raise ValueError("Phone number must be a valid 10-digit Indian mobile number")

     return value
    

    @model_validator(mode="after")
    def validate_doctor_fields(self):
        if self.role == UserRole.DOCTOR:
            if not self.specialization:
             raise ValueError("Specialization is required for doctor registration")
            
            if len(self.specialization.strip())<2:
                raise ValueError("Specialization must be at least 2 characters")

        return self
    





class LoginRequest(BaseModel):
    email: EmailStr
    password: str =Field(min_length=8 , max_length=72)


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

    @model_validator(mode="after")
    def validate_slot_time(self):
        self.start_time = make_utc_naive(self.start_time)
        self.end_time = make_utc_naive(self.end_time)

        now = datetime.utcnow()

        if self.start_time <= now:
            raise ValueError("Start time must be in the future")

        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")

        duration_minutes = (self.end_time - self.start_time).total_seconds() / 60

        if duration_minutes < 15:
            raise ValueError("Availability slot must be at least 15 minutes")

        if duration_minutes > 120:
            raise ValueError("Availability slot cannot be more than 120 minutes")

        return self

class AvailabilityResponse(BaseModel):
    id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    status: SlotStatus

    model_config = {"from_attributes": True}


class BookingRequest(BaseModel):
    slot_id: int = Field(gt=0)
    reason: str | None = Field(default=None, max_length=500)


class ConsultationResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    slot_id: int
    status: ConsultationStatus
    reason: str | None

    model_config = {"from_attributes": True}



class PrescriptionCreateRequest(BaseModel):
    medicines: list[dict[str, Any]] = Field(min_length=1, max_length=20)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("medicines")
    @classmethod
    def validate_medicines(cls, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        required_fields = {"name", "dosage", "frequency", "duration"}

        for medicine in value:
            missing_fields = required_fields - set(medicine.keys())

            if missing_fields:
                raise ValueError(
                    f"Medicine is missing required fields: {', '.join(missing_fields)}"
                )

            for field in required_fields:
                if not str(medicine.get(field, "")).strip():
                    raise ValueError(f"Medicine field '{field}' cannot be empty")

        return value


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
    payment_id: int = Field(gt=0)
    status: PaymentStatus = PaymentStatus.PAID


class AdminAnalyticsResponse(BaseModel):
    total_users: int
    total_doctors: int
    total_consultations: int
    total_prescriptions: int
    total_payments: int