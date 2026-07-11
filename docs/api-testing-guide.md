# API Testing Guide: Amrutam Telemedicine Backend

This guide explains how to test the Amrutam Telemedicine Backend using Swagger UI.

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

---

## 1. Start the Application

From the project folder:

```powershell
cd E:\amrutam-telemedicine-backend
docker compose up -d --build
```

Check containers:

```powershell
docker ps
```

Expected containers:

```text
amrutam_api
amrutam_postgres
amrutam_redis
amrutam_prometheus
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 2. Optional: Clear Database Before Testing

To clear all existing test data, open PostgreSQL shell:

```powershell
docker exec -it amrutam_postgres psql -U postgres -d amrutam_db
```

Run:

```sql
TRUNCATE TABLE
    audit_logs,
    idempotency_keys,
    payments,
    prescriptions,
    consultations,
    availability_slots,
    doctors,
    profiles,
    users
RESTART IDENTITY CASCADE;
```

Exit:

```sql
\q
```

Create demo admin again:

```powershell
docker exec -it amrutam_api python -m app.seed_admin
```

---

## 3. Test Health APIs

### 3.1 Root Endpoint

Endpoint:

```http
GET /
```

Expected response:

```json
{
  "message": "Amrutam Telemedicine Backend is running"
}
```

### 3.2 Health Check

Endpoint:

```http
GET /health
```

Expected response:

```json
{
  "status": "healthy"
}
```

### 3.3 Readiness Check

Endpoint:

```http
GET /ready
```

Expected response:

```json
{
  "status": "ready"
}
```

### 3.4 Redis Health

Endpoint:

```http
GET /health/redis
```

Expected response in Docker mode:

```json
{
  "status": "redis healthy"
}
```

---

## 4. Create Test Users

You need three types of users:

1. Patient
2. Doctor
3. Admin

Admin is created using the seed script.

---

## 5. Register Patient

Endpoint:

```http
POST /auth/register
```

Example request:

```json
{
  "email": "patient1@example.com",
  "phone": "9876543210",
  "password": "Password123",
  "role": "PATIENT",
  "full_name": "Test Patient"
}
```

Expected result:

```text
201 Created
```

Save the patient email and password.

---

## 6. Register Doctor

Endpoint:

```http
POST /auth/register
```

Example request:

```json
{
  "email": "doctor1@example.com",
  "phone": "9876543211",
  "password": "Password123",
  "role": "DOCTOR",
  "full_name": "Dr Test Doctor",
  "specialization": "Ayurveda",
  "experience_years": 5,
  "consultation_fee": 500
}
```

Expected result:

```text
201 Created
```

Save the doctor email and password.

---

## 7. Login and Get Access Tokens

Endpoint:

```http
POST /auth/login
```

### 7.1 Login as Patient

Request:

```json
{
  "email": "patient1@example.com",
  "password": "Password123"
}
```

Copy the returned access token.

### 7.2 Login as Doctor

Request:

```json
{
  "email": "doctor1@example.com",
  "password": "Password123"
}
```

Copy the returned access token.

### 7.3 Login as Admin

Admin user is created using seed script.

Credentials:

```text
Email: admin@example.com
Password: Password123
```

Request:

```json
{
  "email": "admin@example.com",
  "password": "Password123"
}
```

Copy the returned access token.

---

## 8. Authorize in Swagger

In Swagger UI:

1. Click **Authorize** button.
2. Paste token in this format:

```text
Bearer <your_access_token>
```

Example:

```text
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...
```

3. Click **Authorize**.
4. Click **Close**.

Use the correct token depending on the API you are testing:

| API Type              | Token Needed  |
| --------------------- | ------------- |
| Patient booking       | Patient token |
| Doctor availability   | Doctor token  |
| Prescription creation | Doctor token  |
| Admin analytics       | Admin token   |

---

## 9. Test Current User API

Endpoint:

```http
GET /auth/me
```

Use patient, doctor, or admin token.

Expected response should show current user details.

---

## 10. Create Doctor Availability

Use the **doctor token** in Swagger authorization.

Endpoint:

```http
POST /doctors/availability
```

Example request:

```json
{
  "start_time": "2026-07-12T10:00:00",
  "end_time": "2026-07-12T10:30:00"
}
```

Expected result:

```text
201 Created
```

Save the returned slot ID.

Example important values:

```text
doctor_id = 1
slot_id = 1
status = AVAILABLE
```

---

## 11. Search Doctors

Endpoint:

```http
GET /doctors
```

Example query parameters:

```text
specialization=Ayurveda
min_rating=0
limit=10
offset=0
```

Expected response:

```json
[
  {
    "id": 1,
    "specialization": "Ayurveda",
    "experience_years": 5,
    "consultation_fee": 500,
    "rating": 0
  }
]
```

This endpoint also tests Redis caching.

---

## 12. View Doctor Slots

Endpoint:

```http
GET /doctors/{doctor_id}/slots
```

Example:

```text
GET /doctors/1/slots
```

Expected response should show available slots.

Save:

```text
doctor_id
slot_id
```

---

## 13. Book Consultation

Use the **patient token** in Swagger authorization.

Endpoint:

```http
POST /consultations/book
```

Important: Add header:

```http
Idempotency-Key: booking-test-001
```

In Swagger, there should be a field for `Idempotency-Key` if it is defined as a header parameter.

Example request:

```json
{
  "doctor_id": 1,
  "slot_id": 1,
  "reason": "Fever and body pain"
}
```

Expected response:

```text
201 Created
```

Save:

```text
consultation_id
payment_id if returned
```

Expected consultation status:

```text
BOOKED
```

---

## 14. Test Idempotency

Send the same booking request again with the same header:

```http
Idempotency-Key: booking-test-001
```

Expected behavior:

```text
The backend should return the same previous booking response.
It should not create a duplicate consultation.
```

This proves duplicate booking retry protection.

---

## 15. Test Double Booking Prevention

Try booking the same slot again with a different idempotency key.

Header:

```http
Idempotency-Key: booking-test-002
```

Same body:

```json
{
  "doctor_id": 1,
  "slot_id": 1,
  "reason": "Trying same slot again"
}
```

Expected response:

```text
409 Conflict
```

Expected message:

```json
{
  "detail": "Slot is not available"
}
```

This proves double booking prevention.

---

## 16. Start Consultation

Use the **doctor token**.

Endpoint:

```http
POST /consultations/{consultation_id}/start
```

Example:

```text
POST /consultations/1/start
```

Expected status:

```text
ONGOING
```

---

## 17. Complete Consultation

Use the **doctor token**.

Endpoint:

```http
POST /consultations/{consultation_id}/complete
```

Example:

```text
POST /consultations/1/complete
```

Expected status:

```text
COMPLETED
```

---

## 18. Create Prescription

Use the **doctor token**.

Endpoint:

```http
POST /consultations/{consultation_id}/prescriptions
```

If your Swagger shows a different prescription endpoint, use the endpoint shown there.

Example request:

```json
{
  "medicines": [
    {
      "name": "Paracetamol",
      "dosage": "500mg",
      "frequency": "Twice a day",
      "duration": "3 days",
      "instructions": "After food"
    }
  ],
  "notes": "Drink warm water and take proper rest."
}
```

Expected response:

```text
201 Created
```

Save:

```text
prescription_id
```

---

## 19. View Prescription

Use the **patient token**.

Endpoint:

```http
GET /consultations/prescriptions/{prescription_id}
```

If your Swagger shows a different prescription GET endpoint, use the endpoint shown there.

Expected result:

```text
Patient can view own prescription.
```

Security test:

```text
Another patient should not be able to view this prescription.
```

---

## 20. Confirm Mock Payment

Use patient token or allowed role based on your Swagger endpoint.

Endpoint:

```http
POST /payments/{payment_id}/mock-confirm
```

Example:

```text
POST /payments/1/mock-confirm
```

Expected payment status:

```text
PAID
```

---

## 21. View Payment

Endpoint:

```http
GET /payments/{payment_id}
```

Expected response should show:

```text
status = PAID
```

---

## 22. Admin Analytics

Use the **admin token**.

Endpoint:

```http
GET /admin/analytics/summary
```

Expected response contains counts such as:

```json
{
  "total_users": 3,
  "total_doctors": 1,
  "total_consultations": 1,
  "total_prescriptions": 1,
  "total_payments": 1
}
```

---

## 23. Admin Audit Logs

Use the **admin token**.

Endpoint:

```http
GET /admin/audit-logs
```

Expected response should show audit events such as:

```text
USER_REGISTERED
DOCTOR_SLOT_CREATED
CONSULTATION_BOOKED
CONSULTATION_STARTED
CONSULTATION_COMPLETED
PRESCRIPTION_CREATED
PAYMENT_CONFIRMED
```

---

## 24. Test RBAC Security

### 24.1 Patient Tries to Create Doctor Availability

Use patient token.

Endpoint:

```http
POST /doctors/availability
```

Expected response:

```text
403 Forbidden
```

### 24.2 Doctor Tries to Access Admin Analytics

Use doctor token.

Endpoint:

```http
GET /admin/analytics/summary
```

Expected response:

```text
403 Forbidden
```

### 24.3 Public User Tries Protected API

Remove authorization token and call:

```http
GET /auth/me
```

Expected response:

```text
401 Unauthorized
```

---

## 25. Test Validation

Try invalid phone number during register:

```json
{
  "email": "invaliduser@example.com",
  "phone": "12345",
  "password": "Password123",
  "role": "PATIENT",
  "full_name": "Invalid User"
}
```

Expected response:

```text
422 Validation Error
```

Try invalid slot time:

```json
{
  "start_time": "2026-07-12T11:00:00",
  "end_time": "2026-07-12T10:30:00"
}
```

Expected response:

```text
422 Validation Error
```

---

## 26. Test Rate Limiting

Try calling login repeatedly more than the allowed limit.

Endpoint:

```http
POST /auth/login
```

Expected response after limit is exceeded:

```text
429 Too Many Requests
```

---

## 27. Test Metrics

Endpoint:

```http
GET /metrics
```

Open:

```text
http://127.0.0.1:8000/metrics
```

Expected result:

```text
Prometheus metrics text output
```

---

## 28. Test Prometheus

Open:

```text
http://127.0.0.1:9090
```

Go to:

```text
Status → Targets
```

Expected:

```text
amrutam-api = UP
```

Try query:

```promql
http_requests_total
```

or:

```promql
http_request_duration_seconds
```

Metric names may vary depending on the Prometheus instrumentator version.

---

## 29. Suggested Testing Order

Use this order for smooth testing:

```text
1. Start Docker Compose
2. Clear database if needed
3. Seed admin
4. Test /health
5. Register patient
6. Register doctor
7. Login patient
8. Login doctor
9. Login admin
10. Authorize doctor token
11. Create doctor availability
12. Search doctors
13. View doctor slots
14. Authorize patient token
15. Book consultation with Idempotency-Key
16. Repeat same booking with same Idempotency-Key
17. Try same slot with different Idempotency-Key
18. Authorize doctor token
19. Start consultation
20. Complete consultation
21. Create prescription
22. Authorize patient token
23. View prescription
24. Confirm payment
25. Authorize admin token
26. Check analytics
27. Check audit logs
28. Check /metrics
29. Check Prometheus UI
```

---

## 30. Final Testing Checklist

| Test                              | Expected Result  |
| --------------------------------- | ---------------- |
| `/health`                         | Healthy          |
| `/ready`                          | Ready            |
| `/health/redis`                   | Redis healthy    |
| Register patient                  | Success          |
| Register doctor                   | Success          |
| Login patient                     | Token received   |
| Login doctor                      | Token received   |
| Login admin                       | Token received   |
| Doctor creates availability       | Success          |
| Patient searches doctor           | Success          |
| Patient books slot                | Success          |
| Repeat booking with same key      | Same response    |
| Book same slot with different key | Conflict         |
| Doctor starts consultation        | Success          |
| Doctor completes consultation     | Success          |
| Doctor creates prescription       | Success          |
| Patient views own prescription    | Success          |
| Payment confirmation              | Success          |
| Admin analytics                   | Success          |
| Admin audit logs                  | Success          |
| Patient accessing admin API       | Forbidden        |
| Invalid input                     | Validation error |
| Rate limit                        | 429 after limit  |
| `/metrics`                        | Metrics shown    |
| Prometheus target                 | UP               |

---

## 31. Notes for Reviewer

The backend can be tested fully through Swagger UI.

The complete infrastructure runs using:

```bash
docker compose up --build
```

The application includes:

* FastAPI backend
* PostgreSQL database
* Redis cache/rate-limit store
* Prometheus monitoring
* JWT authentication
* Role-based access control
* Idempotent booking
* Audit logging
* CI/CD pipeline
* Docker image publishing