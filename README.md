# Amrutam Telemedicine Backend

Production-grade backend system for Amrutam’s telemedicine platform, built with **FastAPI**, **PostgreSQL**, **Redis**, **Docker**, **Prometheus**, and **GitHub Actions CI/CD**.

This backend focuses on scalability, reliability, security, observability, and maintainable service design. It implements core telemedicine workflows such as user authentication, role-based access control, doctor availability, consultation booking, prescriptions, payments, audit logs, admin analytics, rate limiting, idempotency, and monitoring.

---

## Project Links

* **Repository:** [amrutam-telemedicine-backend](https://github.com/chauhanmuskan291980-wq/amrutam-telemedicine-backend)
* **Docker Image:** [GitHub Container Registry Package](https://github.com/chauhanmuskan291980-wq/amrutam-telemedicine-backend/pkgs/container/amrutam-telemedicine-backend)
* **Docker Pull Command:**

```bash
docker pull ghcr.io/chauhanmuskan291980-wq/amrutam-telemedicine-backend:latest
```

---

## Tech Stack

| Area                     | Technology                 |
| ------------------------ | -------------------------- |
| Backend Framework        | FastAPI                    |
| Language                 | Python 3.10                |
| Database                 | PostgreSQL                 |
| ORM                      | SQLAlchemy                 |
| Cache / Rate Limit Store | Redis                      |
| Authentication           | JWT                        |
| Password Hashing         | Passlib + Bcrypt           |
| Validation               | Pydantic                   |
| API Documentation        | OpenAPI / Swagger          |
| Observability            | Prometheus metrics         |
| Containerization         | Docker, Docker Compose     |
| CI/CD                    | GitHub Actions             |
| Security Scan            | Bandit                     |
| Linting                  | Ruff                       |
| Testing                  | Pytest, FastAPI TestClient |

---

## Features Implemented

### User Lifecycle

* User registration
* User login
* JWT-based authentication
* Current user profile endpoint
* Role-based access control
* Supported roles:

  * `PATIENT`
  * `DOCTOR`
  * `ADMIN`

### Doctor Availability and Search

* Doctor registration
* Doctor profile creation
* Doctor availability slot creation
* Search doctors by specialization
* Filter doctors by rating
* Pagination using `limit` and `offset`
* Redis/in-memory caching for doctor search results
* Cache invalidation when doctor availability changes

### Booking Workflow

* Patient can book available doctor slots
* Booking uses `Idempotency-Key` header
* Prevents duplicate bookings
* Prevents double booking of the same slot
* Slot status changes after booking
* Consultation and payment records are created during booking

### Consultation Lifecycle

* Consultation booking
* Start consultation
* Complete consultation
* Cancel consultation
* Role-based access for patient and doctor

### Prescriptions

* Doctor can create prescription after consultation
* Patient can view own prescription
* Access control prevents other patients from viewing prescriptions
* Prescription medicine validation is included

### Payments

* Mock payment creation during booking
* Mock payment confirmation endpoint
* Payment status tracking

### Admin Analytics

* Total users
* Total doctors
* Total consultations
* Total prescriptions
* Total payments
* Admin-only access

### Compliance and Audit Logs

* Audit logs for sensitive workflows
* Tracks action, resource type, resource ID, user ID, IP address, and user agent
* Admin can view audit logs with pagination

### Security

* JWT authentication
* Bcrypt password hashing
* Role-based access control
* Input validation
* Rate limiting
* Secrets managed through environment variables
* Admin self-registration blocked
* Audit trails for compliance-sensitive actions
* Dependency/security scan through Bandit in CI

### Observability

* Health endpoint
* Readiness endpoint
* Redis health endpoint
* Prometheus `/metrics` endpoint
* Prometheus container included in Docker Compose

### Infrastructure

* Dockerfile
* Docker Compose setup
* PostgreSQL container
* Redis container
* FastAPI application container
* Prometheus container
* GitHub Actions CI pipeline
* GitHub Container Registry Docker image publishing workflow

---

## Project Structure

```text
amrutam-telemedicine-backend/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── admin.py
│   │       ├── auth.py
│   │       ├── consultations.py
│   │       ├── doctors.py
│   │       └── payments.py
│   │
│   ├── core/
│   │   ├── cache.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── rate_limiter.py
│   │   └── security.py
│   │
│   ├── models/
│   │   └── models.py
│   │
│   ├── schemas/
│   │   └── schemas.py
│   │
│   ├── utils/
│   │   └── audit.py
│   │
│   ├── main.py
│   └── seed_admin.py
│
├── docs/
│   └── openapi.json
│
├── infra/
│   └── prometheus.yml
│
├── tests/
│   ├── conftest.py
│   ├── test_core_flows.py
│   └── test_health.py
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── docker-publish.yml
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Core Data Model

The system uses the following core tables:

| Table                | Purpose                                                   |
| -------------------- | --------------------------------------------------------- |
| `users`              | Stores login, role, authentication, and account status    |
| `profiles`           | Stores user profile information                           |
| `doctors`            | Stores doctor specialization, fee, experience, and rating |
| `availability_slots` | Stores doctor available time slots                        |
| `consultations`      | Stores patient-doctor consultation lifecycle              |
| `prescriptions`      | Stores prescription data for consultations                |
| `payments`           | Stores payment status and amount                          |
| `audit_logs`         | Stores compliance and security audit trails               |
| `idempotency_keys`   | Prevents duplicate booking writes                         |

---

## API Modules

| Module        | Base Path                       | Description                                     |
| ------------- | ------------------------------- | ----------------------------------------------- |
| Auth          | `/auth`                         | Register, login, current user                   |
| Doctors       | `/doctors`                      | Search doctors, create availability, view slots |
| Consultations | `/consultations`                | Booking, lifecycle, prescriptions               |
| Payments      | `/payments`                     | Mock payment workflow                           |
| Admin         | `/admin`                        | Analytics and audit logs                        |
| Health        | `/health`, `/ready`, `/metrics` | Health, readiness, and monitoring               |

---

## Environment Variables

Create a `.env` file for local development.

```env
APP_NAME=Amrutam Telemedicine Backend
APP_ENV=development
APP_DEBUG=true

DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/amrutam_db

REDIS_ENABLED=false
REDIS_URL=redis://127.0.0.1:6379/0

RATE_LIMIT_ENABLED=true
RATE_LIMIT_STORAGE_URL=memory://

JWT_SECRET_KEY=change-this-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

For Docker Compose, environment variables are already provided inside `docker-compose.yml`.

---

## Local Setup Without Docker

### 1. Clone Repository

```bash
git clone https://github.com/chauhanmuskan291980-wq/amrutam-telemedicine-backend.git
cd amrutam-telemedicine-backend
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

Create PostgreSQL database:

```sql
CREATE DATABASE amrutam_db;
```

Update `.env` with your PostgreSQL credentials.

### 5. Run Application

```bash
uvicorn app.main:app --reload
```

Application will be available at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

---

## Docker Setup

This project includes Docker Compose for running:

* FastAPI app
* PostgreSQL
* Redis
* Prometheus

### Start All Services

```bash
docker compose up --build
```

### Stop Services

```bash
docker compose down
```

### Stop and Remove Database Volume

```bash
docker compose down -v
```

### Docker Services

| Service        | URL / Port                           | Purpose                    |
| -------------- | ------------------------------------ | -------------------------- |
| FastAPI API    | `http://127.0.0.1:8000`              | Backend API                |
| Swagger Docs   | `http://127.0.0.1:8000/docs`         | API testing                |
| OpenAPI Schema | `http://127.0.0.1:8000/openapi.json` | API schema                 |
| PostgreSQL     | `localhost:5433`                     | Database                   |
| Redis          | `localhost:6379`                     | Cache and rate-limit store |
| Prometheus     | `http://127.0.0.1:9090`              | Metrics dashboard          |

---

## Health Checks

```text
GET /
GET /health
GET /ready
GET /health/redis
GET /metrics
```

Example:

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{
  "status": "healthy"
}
```

---

## Prometheus Monitoring

The application exposes metrics at:

```text
http://127.0.0.1:8000/metrics
```

Prometheus UI runs at:

```text
http://127.0.0.1:9090
```

Prometheus scrapes metrics from the FastAPI app using:

```yaml
scrape_configs:
  - job_name: "amrutam-api"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["app:8000"]
```

To verify Prometheus:

1. Open `http://127.0.0.1:9090`
2. Go to **Status → Targets**
3. Confirm `amrutam-api` is `UP`

---

## Redis Usage

Redis is used for:

1. Doctor search caching
2. Rate-limit counter storage in Docker/production mode

Local development can run without Redis by using:

```env
REDIS_ENABLED=false
RATE_LIMIT_STORAGE_URL=memory://
```

Docker mode uses Redis:

```env
REDIS_ENABLED=true
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_STORAGE_URL=redis://redis:6379/1
```

---

## Rate Limiting

Sensitive endpoints are rate limited using SlowAPI.

Example limits:

| Endpoint                   | Limit              |
| -------------------------- | ------------------ |
| `POST /auth/register`      | 5 requests/minute  |
| `POST /auth/login`         | 5 requests/minute  |
| `POST /consultations/book` | 10 requests/minute |

When the limit is exceeded, the API returns:

```text
429 Too Many Requests
```

---

## Idempotency

Booking uses an `Idempotency-Key` header to prevent duplicate write operations.

Example:

```http
POST /consultations/book
Idempotency-Key: booking-001
Authorization: Bearer <token>
```

If the same request is retried with the same key, the existing booking response is returned instead of creating a duplicate consultation.

This protects the booking flow from:

* Network retries
* Double-clicks
* Client timeout retries
* Duplicate payment/booking attempts

---

## Testing

Run tests:

```bash
pytest -v
```

The test suite covers:

* Health check
* Readiness check
* Register/login/current user
* Admin self-registration block
* Role-based authorization
* Doctor availability
* Doctor search
* Booking idempotency
* Double booking prevention
* Consultation lifecycle
* Prescription access control
* Payment confirmation
* Admin analytics
* Audit logs

---

## Code Quality and Security Checks

Run Ruff:

```bash
ruff check app tests
```

Run Bandit:

```bash
bandit -r app -x app/seed_admin.py
```

---

## CI Pipeline

GitHub Actions CI is configured in:

```text
.github/workflows/ci.yml
```

CI runs on:

* Push to `main`
* Pull request to `main`

CI steps:

1. Checkout repository
2. Set up Python 3.10
3. Start PostgreSQL service
4. Install dependencies
5. Run tests
6. Run Ruff lint check
7. Run Bandit security scan

CI status should show a green check mark in GitHub Actions.

---

## Docker Publish Pipeline

Docker image publishing is configured in:

```text
.github/workflows/docker-publish.yml
```

This workflow:

1. Runs on push to `main`
2. Builds the Docker image
3. Logs in to GitHub Container Registry
4. Pushes the image to GHCR

Published image:

```bash
docker pull ghcr.io/chauhanmuskan291980-wq/amrutam-telemedicine-backend:latest
```

---

## OpenAPI Schema

FastAPI automatically generates OpenAPI schema at:

```text
http://127.0.0.1:8000/openapi.json
```

To export it:

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/openapi.json -OutFile docs/openapi.json
```

---

## Demo Admin User

The project includes a seed script:

```bash
python -m app.seed_admin
```

Demo admin credentials:

```text
Email: admin@example.com
Password: Password123
```

Important: These are demo credentials only. Change them before any real deployment.

---

## Security Design

Security features include:

* JWT authentication
* Bcrypt password hashing
* RBAC for patient, doctor, and admin roles
* Admin self-registration prevention
* Pydantic input validation
* Rate limiting on sensitive APIs
* Audit logs for compliance-sensitive events
* Environment-based secrets
* Dependency scanning through CI
* Security scan through Bandit

Planned/Documented production security improvements:

* MFA using OTP/TOTP
* HTTPS/TLS enforcement
* Key rotation policy
* Encrypted backups
* Fine-grained audit review workflow
* Centralized secret manager
* WAF/API gateway in front of application

---

## Scalability Design

The system is designed to support high consultation volume through:

* Stateless FastAPI application containers
* Horizontal scaling behind a load balancer
* PostgreSQL as primary relational database
* Redis for caching and rate limiting
* Indexing frequently queried fields
* Idempotent write APIs
* Concurrency control for booking
* Pagination on list APIs
* Prometheus-based monitoring
* Dockerized deployment

Target requirements:

| Requirement              | Strategy                                                  |
| ------------------------ | --------------------------------------------------------- |
| 100k daily consultations | Horizontal app scaling, DB indexing, Redis cache          |
| p95 reads < 200ms        | Redis cache, pagination, indexed queries                  |
| p95 writes < 500ms       | Optimized transactions, idempotency, short DB locks       |
| 99.95% availability      | Containerized deployment, health checks, restart policies |
| Secure access            | JWT, RBAC, rate limiting, audit logs                      |

---

## Reliability Design

Reliability strategies:

* Health and readiness endpoints
* Docker restart policies
* Database health checks
* Redis health checks
* Idempotent booking writes
* Audit logs for sensitive actions
* Prometheus metrics
* CI pipeline to prevent broken code from merging

Planned production reliability improvements:

* Blue/green deployment
* Database read replicas
* Automated backups
* Disaster recovery runbooks
* Centralized logs
* Distributed tracing
* Async job queue for notifications

---

## Current Limitations

This project is assignment/demo focused. Some production features are documented but not fully implemented.

Current limitations:

* MFA is designed but not fully implemented
* Payment gateway is mocked
* Alembic migration setup is available as a dependency but schema currently uses SQLAlchemy table creation
* Background jobs are not yet using Celery/RQ
* Full distributed tracing is planned but not fully implemented
* HTTPS/TLS termination should be handled by a reverse proxy or cloud load balancer in production

---

## Useful Commands

Run app locally:

```bash
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest -v
```

Run Docker:

```bash
docker compose up --build
```

Stop Docker:

```bash
docker compose down
```

Check running containers:

```bash
docker ps
```

Run lint:

```bash
ruff check app tests
```

Run security scan:

```bash
bandit -r app -x app/seed_admin.py
```

Export OpenAPI:

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/openapi.json -OutFile docs/openapi.json
```

Pull published Docker image:

```bash
docker pull ghcr.io/chauhanmuskan291980-wq/amrutam-telemedicine-backend:latest
```

---

## Evaluation Checklist

| Requirement                   | Status                          |
| ----------------------------- | ------------------------------- |
| Git repo with code and infra  | Done                            |
| README with setup             | Done                            |
| OpenAPI schema                | Done                            |
| Architecture doc              | In `docs/architecture.md`       |
| Tests and CI pipeline         | Done                            |
| Observability setup           | Done                            |
| Security checklist            | In `docs/security-checklist.md` |
| Threat model                  | In `docs/threat-model.md`       |
| PostgreSQL database           | Done                            |
| Redis optional cache          | Done                            |
| Docker deployment             | Done                            |
| Idempotency for writes        | Done                            |
| Rate limiting                 | Done                            |
| Input validation              | Done                            |
| Audit logs                    | Done                            |
| Admin analytics               | Done                            |
| Prometheus metrics            | Done                            |
| Docker image publish pipeline | Done                            |

---

## Author

**Muskan Chauhan**

Backend-focused Software Engineer and Applied AI learner with experience in FastAPI, Node.js, PostgreSQL, Docker, CI/CD, and production-grade backend systems.

---

## License

This project is created as part of the Amrutam backend engineering assignment.
