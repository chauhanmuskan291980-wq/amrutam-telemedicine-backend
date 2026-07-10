import random
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.main import app
from app.models.models import Payment, Profile, User, UserRole

client = TestClient(app)

Base.metadata.create_all(bind=engine)

PASSWORD = "Password123"


def unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}@example.com"


def unique_phone() -> str:
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(9))


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register_patient():
    email = unique_email("patient")

    payload = {
        "email": email,
        "phone": unique_phone(),
        "password": PASSWORD,
        "full_name": "Test Patient",
        "role": "PATIENT",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201, response.json()

    return email


def register_doctor(specialization: str = "Ayurveda"):
    email = unique_email("doctor")

    payload = {
        "email": email,
        "phone": unique_phone(),
        "password": PASSWORD,
        "full_name": "Dr. Test Doctor",
        "role": "DOCTOR",
        "specialization": specialization,
        "experience_years": 7,
        "consultation_fee": 500,
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201, response.json()

    return email


def login_user(email: str) -> str:
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": PASSWORD,
        },
    )

    assert response.status_code == 200, response.json()

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    return data["access_token"]


def create_admin_user():
    email = unique_email("admin")

    db = SessionLocal()

    admin = User(
        email=email,
        phone=unique_phone(),
        password_hash=hash_password(PASSWORD),
        role=UserRole.ADMIN,
        is_active=True,
    )

    db.add(admin)
    db.flush()

    profile = Profile(
        user_id=admin.id,
        full_name="System Admin",
    )

    db.add(profile)
    db.commit()
    db.close()

    return email


def create_doctor_slot(doctor_token: str):
    response = client.post(
        "/doctors/availability",
        json={
            "start_time": "2026-07-20T10:00:00",
            "end_time": "2026-07-20T10:30:00",
        },
        headers=auth_headers(doctor_token),
    )

    assert response.status_code == 201, response.json()

    return response.json()


def book_slot(patient_token: str, slot_id: int, key: str):
    response = client.post(
        "/consultations/book",
        json={
            "slot_id": slot_id,
            "reason": "Fever and body pain",
        },
        headers={
            **auth_headers(patient_token),
            "Idempotency-Key": key,
        },
    )

    return response


def get_payment_id_by_consultation(consultation_id: int) -> int:
    db = SessionLocal()

    payment = (
        db.query(Payment)
        .filter(Payment.consultation_id == consultation_id)
        .first()
    )

    db.close()

    assert payment is not None

    return payment.id


def test_auth_register_login_and_me():
    patient_email = register_patient()
    token = login_user(patient_email)

    response = client.get(
        "/auth/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200, response.json()

    data = response.json()

    assert data["email"] == patient_email
    assert data["role"] == "PATIENT"
    assert data["is_active"] is True


def test_admin_cannot_self_register():
    response = client.post(
        "/auth/register",
        json={
            "email": unique_email("admin_self"),
            "phone": unique_phone(),
            "password": PASSWORD,
            "full_name": "Bad Admin",
            "role": "ADMIN",
        },
    )

    assert response.status_code == 400, response.json()
    assert response.json()["detail"] == "Admin users cannot self-register"


def test_patient_cannot_create_doctor_availability():
    patient_email = register_patient()
    patient_token = login_user(patient_email)

    response = client.post(
        "/doctors/availability",
        json={
            "start_time": "2026-07-20T11:00:00",
            "end_time": "2026-07-20T11:30:00",
        },
        headers=auth_headers(patient_token),
    )

    assert response.status_code == 403, response.json()
    assert response.json()["detail"] == "You do not have permission to access this resource"


def test_doctor_can_create_availability_and_patient_can_view_slots():
    doctor_email = register_doctor("Ayurveda")
    doctor_token = login_user(doctor_email)

    slot = create_doctor_slot(doctor_token)

    assert slot["status"] == "AVAILABLE"
    assert "doctor_id" in slot

    patient_email = register_patient()
    patient_token = login_user(patient_email)

    response = client.get(
        f"/doctors/{slot['doctor_id']}/slots",
        headers=auth_headers(patient_token),
    )

    assert response.status_code == 200, response.json()

    slots = response.json()

    assert isinstance(slots, list)
    assert any(item["id"] == slot["id"] for item in slots)


def test_doctor_search_filter():
    specialization = f"Cardiology-{uuid4().hex[:6]}"

    register_doctor(specialization)

    response = client.get(
        f"/doctors?specialization={specialization}&min_rating=0&limit=20&offset=0"
    )

    assert response.status_code == 200, response.json()

    doctors = response.json()

    assert isinstance(doctors, list)
    assert len(doctors) >= 1
    assert doctors[0]["specialization"] == specialization


def test_booking_idempotency_and_double_booking():
    doctor_email = register_doctor("Ayurveda")
    doctor_token = login_user(doctor_email)
    slot = create_doctor_slot(doctor_token)

    patient_email = register_patient()
    patient_token = login_user(patient_email)

    idempotency_key = f"booking-{uuid4().hex}"

    first_response = book_slot(
        patient_token=patient_token,
        slot_id=slot["id"],
        key=idempotency_key,
    )

    assert first_response.status_code == 201, first_response.json()

    first_booking = first_response.json()

    assert first_booking["slot_id"] == slot["id"]
    assert first_booking["status"] == "BOOKED"

    second_response = book_slot(
        patient_token=patient_token,
        slot_id=slot["id"],
        key=idempotency_key,
    )

    assert second_response.status_code == 201, second_response.json()
    assert second_response.json()["id"] == first_booking["id"]

    double_booking_response = book_slot(
        patient_token=patient_token,
        slot_id=slot["id"],
        key=f"booking-{uuid4().hex}",
    )

    assert double_booking_response.status_code == 409, double_booking_response.json()
    assert double_booking_response.json()["detail"] == "Slot is already booked or unavailable"


def test_consultation_lifecycle_and_prescription_flow():
    doctor_email = register_doctor("Ayurveda")
    doctor_token = login_user(doctor_email)
    slot = create_doctor_slot(doctor_token)

    patient_email = register_patient()
    patient_token = login_user(patient_email)

    booking_response = book_slot(
        patient_token=patient_token,
        slot_id=slot["id"],
        key=f"booking-{uuid4().hex}",
    )

    assert booking_response.status_code == 201, booking_response.json()

    consultation = booking_response.json()
    consultation_id = consultation["id"]

    start_response = client.patch(
        f"/consultations/{consultation_id}/start",
        headers=auth_headers(doctor_token),
    )

    assert start_response.status_code == 200, start_response.json()
    assert start_response.json()["status"] == "ONGOING"

    complete_response = client.patch(
        f"/consultations/{consultation_id}/complete",
        headers=auth_headers(doctor_token),
    )

    assert complete_response.status_code == 200, complete_response.json()
    assert complete_response.json()["status"] == "COMPLETED"

    prescription_response = client.post(
        f"/consultations/{consultation_id}/prescription",
        json={
            "medicines": [
                {
                    "name": "Paracetamol",
                    "dosage": "500mg",
                    "frequency": "Twice a day",
                    "duration": "3 days",
                    "instructions": "After food",
                }
            ],
            "notes": "Drink warm water and take rest.",
        },
        headers=auth_headers(doctor_token),
    )

    assert prescription_response.status_code == 200, prescription_response.json()

    prescription = prescription_response.json()

    assert prescription["consultation_id"] == consultation_id
    assert prescription["notes"] == "Drink warm water and take rest."

    patient_prescription_response = client.get(
        f"/consultations/{consultation_id}/prescription",
        headers=auth_headers(patient_token),
    )

    assert patient_prescription_response.status_code == 200, patient_prescription_response.json()
    assert patient_prescription_response.json()["consultation_id"] == consultation_id


def test_patient_cannot_view_another_patients_prescription():
    doctor_email = register_doctor("Ayurveda")
    doctor_token = login_user(doctor_email)
    slot = create_doctor_slot(doctor_token)

    patient_email = register_patient()
    patient_token = login_user(patient_email)

    other_patient_email = register_patient()
    other_patient_token = login_user(other_patient_email)

    booking_response = book_slot(
        patient_token=patient_token,
        slot_id=slot["id"],
        key=f"booking-{uuid4().hex}",
    )

    assert booking_response.status_code == 201, booking_response.json()

    consultation_id = booking_response.json()["id"]

    prescription_response = client.post(
        f"/consultations/{consultation_id}/prescription",
        json={
            "medicines": [
                {
                    "name": "Medicine A",
                    "dosage": "1 tablet",
                    "frequency": "Once a day",
                    "duration": "2 days",
                    "instructions": "After food",
                }
            ],
            "notes": "Private prescription",
        },
        headers=auth_headers(doctor_token),
    )

    assert prescription_response.status_code == 200, prescription_response.json()

    response = client.get(
        f"/consultations/{consultation_id}/prescription",
        headers=auth_headers(other_patient_token),
    )

    assert response.status_code == 403, response.json()
    assert response.json()["detail"] == "Access denied"


def test_payment_mock_confirm():
    doctor_email = register_doctor("Ayurveda")
    doctor_token = login_user(doctor_email)
    slot = create_doctor_slot(doctor_token)

    patient_email = register_patient()
    patient_token = login_user(patient_email)

    booking_response = book_slot(
        patient_token=patient_token,
        slot_id=slot["id"],
        key=f"booking-{uuid4().hex}",
    )

    assert booking_response.status_code == 201, booking_response.json()

    consultation_id = booking_response.json()["id"]
    payment_id = get_payment_id_by_consultation(consultation_id)

    get_payment_response = client.get(
        f"/payments/{payment_id}",
        headers=auth_headers(patient_token),
    )

    assert get_payment_response.status_code == 200, get_payment_response.json()
    assert get_payment_response.json()["status"] == "PENDING"

    confirm_response = client.post(
        "/payments/mock-confirm",
        json={
            "payment_id": payment_id,
            "status": "PAID",
        },
        headers=auth_headers(patient_token),
    )

    assert confirm_response.status_code == 200, confirm_response.json()
    assert confirm_response.json()["status"] == "PAID"


def test_admin_analytics_and_audit_logs():
    admin_email = create_admin_user()
    admin_token = login_user(admin_email)

    summary_response = client.get(
        "/admin/analytics/summary",
        headers=auth_headers(admin_token),
    )

    assert summary_response.status_code == 200, summary_response.json()

    summary = summary_response.json()

    assert "total_users" in summary
    assert "total_doctors" in summary
    assert "total_consultations" in summary
    assert "total_prescriptions" in summary
    assert "total_payments" in summary

    logs_response = client.get(
        "/admin/audit-logs?limit=50&offset=0",
        headers=auth_headers(admin_token),
    )

    assert logs_response.status_code == 200, logs_response.json()
    assert isinstance(logs_response.json(), list)


def test_non_admin_cannot_access_admin_analytics():
    patient_email = register_patient()
    patient_token = login_user(patient_email)

    response = client.get(
        "/admin/analytics/summary",
        headers=auth_headers(patient_token),
    )

    assert response.status_code == 403, response.json()
    assert response.json()["detail"] == "You do not have permission to access this resource"