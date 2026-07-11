\# Architecture Document: Amrutam Telemedicine Backend



\## 1. Overview



The Amrutam Telemedicine Backend is a production-grade backend system designed to support online doctor discovery, doctor availability management, consultation booking, prescription management, payments, audit trails, and admin analytics.



The system is built using \*\*FastAPI\*\*, \*\*PostgreSQL\*\*, \*\*Redis\*\*, \*\*Docker\*\*, and \*\*Prometheus\*\*. It follows a modular backend architecture with clearly separated API routes, schemas, services, database models, security utilities, cache utilities, and infrastructure configuration.



The primary goals of the system are:



\* Support secure patient, doctor, and admin workflows.

\* Prevent double booking and duplicate write operations.

\* Provide fast read performance through caching and pagination.

\* Maintain audit logs for compliance-sensitive actions.

\* Expose metrics and health checks for observability.

\* Run consistently using Docker Compose.

\* Support CI/CD with automated tests, linting, security scanning, and Docker image publishing.



\---



\## 2. High-Level Architecture



```mermaid

flowchart TD

&#x20;   Client\[Client / Swagger / Frontend] --> API\[FastAPI Application]



&#x20;   API --> Auth\[Auth \& RBAC Layer]

&#x20;   API --> Validation\[Pydantic Validation Layer]

&#x20;   API --> Routes\[API Route Modules]



&#x20;   Routes --> DB\[(PostgreSQL)]

&#x20;   Routes --> Redis\[(Redis Cache / Rate Limit Store)]

&#x20;   Routes --> Audit\[Audit Log Utility]



&#x20;   API --> Metrics\[Prometheus Metrics Endpoint /metrics]

&#x20;   Prometheus\[Prometheus Server] --> Metrics



&#x20;   Docker\[Docker Compose] --> API

&#x20;   Docker --> DB

&#x20;   Docker --> Redis

&#x20;   Docker --> Prometheus



&#x20;   GitHub\[GitHub Actions CI/CD] --> Tests\[Pytest / Ruff / Bandit]

&#x20;   GitHub --> Registry\[GitHub Container Registry]

```



The backend is deployed as a containerized FastAPI service. PostgreSQL stores relational business data, Redis is used for caching and rate-limit counters, and Prometheus scrapes application metrics from the `/metrics` endpoint.



\---



\## 3. Main Components



\### 3.1 FastAPI Application



The FastAPI application exposes REST APIs for:



\* Authentication

\* Doctor search

\* Doctor availability

\* Consultation booking

\* Consultation lifecycle

\* Prescriptions

\* Payments

\* Admin analytics

\* Audit logs

\* Health checks

\* Metrics



FastAPI automatically generates OpenAPI documentation available at:



```text

/docs

/openapi.json

```



\### 3.2 PostgreSQL



PostgreSQL is the primary system of record. It stores:



\* Users

\* Profiles

\* Doctors

\* Availability slots

\* Consultations

\* Prescriptions

\* Payments

\* Audit logs

\* Idempotency keys



PostgreSQL was selected because the system requires relational consistency, transactional writes, joins, indexing, and strong integrity guarantees.



\### 3.3 Redis



Redis is used for:



1\. Doctor search result caching.

2\. Rate-limit counter storage in Docker/production mode.



For local development, Redis can be disabled and the system falls back to in-memory cache and memory-based rate limiting.



\### 3.4 Prometheus



Prometheus collects metrics from:



```text

/metrics

```



The Docker Compose setup exposes Prometheus at:



```text

http://127.0.0.1:9090

```



Prometheus helps monitor request counts, request latency, error rates, and service health.



\### 3.5 Docker Compose



Docker Compose runs the complete backend stack:



\* FastAPI API container

\* PostgreSQL container

\* Redis container

\* Prometheus container



This makes the system easy to run and review with one command:



```bash

docker compose up --build

```



\### 3.6 GitHub Actions CI/CD



The project includes two GitHub Actions workflows:



1\. \*\*CI Pipeline\*\*



&#x20;  \* Runs tests

&#x20;  \* Runs Ruff lint check

&#x20;  \* Runs Bandit security scan

&#x20;  \* Uses PostgreSQL service in CI



2\. \*\*Docker Publish Pipeline\*\*



&#x20;  \* Builds Docker image

&#x20;  \* Pushes image to GitHub Container Registry



\---



\## 4. Application Module Design



The codebase follows a modular structure:



```text

app/

├── api/routes/          API route handlers

├── core/                Config, database, security, cache, rate limiter

├── models/              SQLAlchemy database models

├── schemas/             Pydantic request/response schemas

├── utils/               Audit log utility

├── main.py              FastAPI app entry point

└── seed\_admin.py        Demo admin user seed script

```



\### 4.1 API Layer



The API layer is organized by business domain:



| File               | Responsibility                     |

| ------------------ | ---------------------------------- |

| `auth.py`          | Register, login, current user      |

| `doctors.py`       | Doctor search, availability, slots |

| `consultations.py` | Booking, lifecycle, prescriptions  |

| `payments.py`      | Mock payment flow                  |

| `admin.py`         | Admin analytics, audit logs        |



\### 4.2 Core Layer



| File              | Responsibility                    |

| ----------------- | --------------------------------- |

| `config.py`       | Environment-based configuration   |

| `database.py`     | SQLAlchemy engine, session, base  |

| `security.py`     | Password hashing and JWT          |

| `dependencies.py` | Current user and role dependency  |

| `cache.py`        | Redis/in-memory cache abstraction |

| `rate\_limiter.py` | SlowAPI rate limiter setup        |



\### 4.3 Schema Layer



Pydantic schemas validate incoming data before business logic runs. Validation includes:



\* Email validation

\* Password strength validation

\* Indian mobile number validation

\* Positive ID validation

\* Slot time validation

\* Slot duration validation

\* Prescription medicine validation

\* Pagination validation



\---



\## 5. Data Flow



\### 5.1 User Registration Flow



```mermaid

sequenceDiagram

&#x20;   participant Client

&#x20;   participant API

&#x20;   participant Validation

&#x20;   participant DB

&#x20;   participant Audit



&#x20;   Client->>API: POST /auth/register

&#x20;   API->>Validation: Validate email, password, phone, role

&#x20;   Validation-->>API: Valid payload

&#x20;   API->>DB: Check existing user

&#x20;   API->>DB: Create user and profile

&#x20;   API->>Audit: Write USER\_REGISTERED log

&#x20;   API-->>Client: User response

```



\### 5.2 Login Flow



```mermaid

sequenceDiagram

&#x20;   participant Client

&#x20;   participant API

&#x20;   participant DB

&#x20;   participant Security



&#x20;   Client->>API: POST /auth/login

&#x20;   API->>DB: Find user by email

&#x20;   API->>Security: Verify bcrypt password

&#x20;   Security-->>API: Password valid

&#x20;   API->>Security: Generate JWT

&#x20;   API-->>Client: Access token

```



\### 5.3 Doctor Search Flow



```mermaid

sequenceDiagram

&#x20;   participant Client

&#x20;   participant API

&#x20;   participant Cache

&#x20;   participant DB



&#x20;   Client->>API: GET /doctors?specialization=Ayurveda

&#x20;   API->>Cache: Check doctor\_search cache key



&#x20;   alt Cache hit

&#x20;       Cache-->>API: Cached doctor list

&#x20;       API-->>Client: Doctor list

&#x20;   else Cache miss

&#x20;       API->>DB: Query doctors with filters

&#x20;       DB-->>API: Doctor list

&#x20;       API->>Cache: Store result with TTL

&#x20;       API-->>Client: Doctor list

&#x20;   end

```



\---



\## 6. Booking Flow and Concurrency Handling



The booking workflow is one of the most critical flows in the system because it must prevent double booking.



\### 6.1 Booking Flow



```mermaid

sequenceDiagram

&#x20;   participant Patient

&#x20;   participant API

&#x20;   participant DB

&#x20;   participant Audit



&#x20;   Patient->>API: POST /consultations/book with Idempotency-Key

&#x20;   API->>DB: Check idempotency key

&#x20;   alt Key already exists

&#x20;       DB-->>API: Existing response

&#x20;       API-->>Patient: Return existing booking

&#x20;   else New request

&#x20;       API->>DB: Lock/check availability slot

&#x20;       API->>DB: Mark slot as BOOKED

&#x20;       API->>DB: Create consultation

&#x20;       API->>DB: Create payment record

&#x20;       API->>DB: Store idempotency key

&#x20;       API->>Audit: Write CONSULTATION\_BOOKED log

&#x20;       API-->>Patient: Booking response

&#x20;   end

```



\### 6.2 Idempotency



The booking API requires an `Idempotency-Key` header. This prevents duplicate write operations caused by:



\* Client retries

\* Network timeout retries

\* Double-click submissions

\* Payment/booking retry attempts



If the same key is used again with the same request, the API returns the previously stored response instead of creating a duplicate consultation.



\### 6.3 Double Booking Prevention



Double booking is prevented by checking the slot status before creating a consultation. Once a slot is booked, its status changes from:



```text

AVAILABLE → BOOKED

```



If another request attempts to book the same slot, the API returns a conflict response.



In a production setup, this can be further strengthened using:



\* Row-level locking

\* Unique constraint on `consultations.slot\_id`

\* Short database transactions

\* Retry logic for transaction conflicts



\---



\## 7. Database Design



Core tables:



| Table                | Description                                                           |

| -------------------- | --------------------------------------------------------------------- |

| `users`              | Stores authentication data, role, active status, MFA flag             |

| `profiles`           | Stores full name and user profile information                         |

| `doctors`            | Stores doctor details such as specialization, experience, fee, rating |

| `availability\_slots` | Stores doctor time slots and slot status                              |

| `consultations`      | Stores patient-doctor consultation lifecycle                          |

| `prescriptions`      | Stores prescription medicines and notes                               |

| `payments`           | Stores consultation payment information                               |

| `audit\_logs`         | Stores compliance and security audit trails                           |

| `idempotency\_keys`   | Stores request keys and responses for safe retries                    |



\---



\## 8. Caching Strategy



Redis is used to cache doctor search results.



\### 8.1 Cache Key Format



```text

doctor\_search:specialization=<value>:min\_rating=<value>:limit=<value>:offset=<value>

```



\### 8.2 Cache TTL



Doctor search cache uses a short TTL, for example:



```text

60 seconds

```



This improves read latency without keeping stale data for too long.



\### 8.3 Cache Invalidation



When a doctor creates or updates availability, doctor search cache keys are invalidated using:



```text

doctor\_search:\*

```



\### 8.4 Local Fallback



When Redis is disabled, the system uses an in-memory cache for local development. This allows the backend to run even without Redis.



\---



\## 9. Rate Limiting Strategy



Rate limiting is applied to sensitive APIs to reduce abuse and brute-force attempts.



| Endpoint                   | Limit              |

| -------------------------- | ------------------ |

| `POST /auth/register`      | 5 requests/minute  |

| `POST /auth/login`         | 5 requests/minute  |

| `POST /consultations/book` | 10 requests/minute |



In Docker/production mode, rate-limit counters are stored in Redis.



In local/test mode, rate limiting can be disabled or stored in memory.



\---



\## 10. Security Architecture



Security features implemented:



\* JWT authentication

\* Bcrypt password hashing

\* Role-based access control

\* Admin self-registration blocked

\* Pydantic input validation

\* Rate limiting

\* Audit logs

\* Environment-based secrets

\* Bandit security scan in CI



\### 10.1 Role-Based Access Control



Supported roles:



| Role      | Access                                                                   |

| --------- | ------------------------------------------------------------------------ |

| `PATIENT` | Book consultations, view own consultations and prescriptions             |

| `DOCTOR`  | Create availability, manage assigned consultations, create prescriptions |

| `ADMIN`   | View analytics and audit logs                                            |



\### 10.2 Secrets Management



Secrets are loaded from environment variables:



\* `DATABASE\_URL`

\* `JWT\_SECRET\_KEY`

\* `REDIS\_URL`

\* `RATE\_LIMIT\_STORAGE\_URL`



No production secrets should be hardcoded in source code.



\### 10.3 MFA



The data model includes an MFA flag. Full OTP/TOTP verification can be added as a production enhancement. The expected MFA flow is:



1\. User enables MFA.

2\. System generates OTP/TOTP secret.

3\. User verifies code.

4\. Login requires both password and MFA code.



\---



\## 11. Observability Architecture



The system exposes:



| Endpoint        | Purpose                  |

| --------------- | ------------------------ |

| `/health`       | Basic health check       |

| `/ready`        | Readiness check          |

| `/health/redis` | Redis/cache health check |

| `/metrics`      | Prometheus metrics       |



Prometheus scrapes metrics from the application container.



Useful metrics include:



\* HTTP request count

\* HTTP response status codes

\* HTTP request latency

\* Error rates

\* Endpoint-level traffic



Production extensions:



\* Grafana dashboards

\* Centralized JSON logs

\* Request ID middleware

\* Distributed tracing with OpenTelemetry

\* Alerting rules for high error rate and high latency



\---



\## 12. Scalability Strategy



The system is designed to support the target of \*\*100k daily consultations\*\*.



\### 12.1 Horizontal Scaling



The FastAPI application is stateless. Multiple app containers can run behind a load balancer.



\### 12.2 Database Scaling



PostgreSQL scaling strategies:



\* Proper indexing on frequently queried columns

\* Connection pooling

\* Read replicas for analytics/search-heavy workloads

\* Partitioning for large audit logs and consultation history

\* Regular vacuum/analyze maintenance



Suggested indexes:



\* `users.email`

\* `doctors.specialization`

\* `availability\_slots.doctor\_id`

\* `availability\_slots.status`

\* `consultations.patient\_id`

\* `consultations.doctor\_id`

\* `consultations.slot\_id`

\* `audit\_logs.created\_at`



\### 12.3 Cache Scaling



Redis reduces repeated database reads for doctor search and helps keep read latency low.



\### 12.4 Pagination



List APIs use pagination through `limit` and `offset`, preventing large unbounded reads.



\---



\## 13. Retry and Backoff Strategy



Retry should be used for transient failures only.



\### 13.1 Retry Use Cases



\* Temporary database connection failure

\* Temporary Redis connection failure

\* External notification service failure

\* Payment gateway timeout



\### 13.2 Backoff Policy



Recommended strategy:



```text

Initial delay: 200ms

Multiplier: 2x

Max retries: 3

Max delay: 2 seconds

Jitter: enabled

```



\### 13.3 Non-Retryable Cases



The system should not retry:



\* Validation errors

\* Authentication failures

\* Authorization failures

\* Duplicate booking conflicts

\* Invalid payment status



\---



\## 14. Transaction Management



The booking workflow should be handled inside a short database transaction.



Transaction responsibilities:



1\. Check idempotency key.

2\. Validate slot availability.

3\. Mark slot as booked.

4\. Create consultation.

5\. Create payment record.

6\. Save idempotency response.

7\. Commit transaction.



If any step fails, the transaction rolls back.



This prevents partial booking states.



\---



\## 15. Saga and Async Job Strategy



For current implementation, consultation booking and payment record creation happen in one backend flow.



For production expansion, a saga pattern can be used:



1\. Create booking intent.

2\. Reserve doctor slot.

3\. Create payment intent.

4\. Confirm payment.

5\. Confirm consultation.

6\. Send notification.

7\. Release slot if payment fails.



Async jobs can be used for:



\* Booking confirmation email/SMS

\* Prescription notification

\* Payment reconciliation

\* Audit export

\* Analytics aggregation



Potential tools:



\* Celery

\* RQ

\* Dramatiq

\* Kafka

\* RabbitMQ



\---



\## 16. Data Partitioning Strategy



For large-scale production usage, partitioning should be applied to high-growth tables.



Recommended partitioning:



| Table           | Partition Strategy                                         |

| --------------- | ---------------------------------------------------------- |

| `audit\_logs`    | Monthly partition by `created\_at`                          |

| `consultations` | Monthly partition by consultation date                     |

| `payments`      | Monthly partition by created date                          |

| `prescriptions` | Partition by consultation date or patient region if needed |



This improves query performance, archival, and backup management.



\---



\## 17. Backup and Disaster Recovery



\### 17.1 Backup Strategy



Recommended backups:



\* Daily full PostgreSQL backups

\* Point-in-time recovery using WAL archiving

\* Encrypted backup storage

\* Backup retention policy of 30–90 days

\* Regular restore testing



\### 17.2 Disaster Recovery Targets



| Metric | Target     |

| ------ | ---------- |

| RPO    | 15 minutes |

| RTO    | 1 hour     |



\### 17.3 Recovery Plan



1\. Detect outage using monitoring.

2\. Fail over to standby database if available.

3\. Restore latest backup if primary database is corrupted.

4\. Replay WAL logs for point-in-time recovery.

5\. Restart application containers.

6\. Verify `/health`, `/ready`, and critical workflows.

7\. Review audit logs and incident timeline.



\---



\## 18. Availability Strategy



The target availability is \*\*99.95%\*\*.



Recommended production setup:



\* Multiple FastAPI app replicas

\* Load balancer

\* PostgreSQL managed database with backup and failover

\* Redis managed service or Redis cluster

\* Health checks and readiness checks

\* Rolling/blue-green deployments

\* CI/CD pipeline with automated tests

\* Observability alerts



\---



\## 19. Deployment Architecture



Current Docker Compose deployment:



```mermaid

flowchart LR

&#x20;   User\[User / Reviewer] --> API\[FastAPI App :8000]

&#x20;   API --> Postgres\[(PostgreSQL :5432)]

&#x20;   API --> Redis\[(Redis :6379)]

&#x20;   Prometheus\[Prometheus :9090] --> API

```



Local exposed ports:



| Service    | Port                                 |

| ---------- | ------------------------------------ |

| FastAPI    | `8000`                               |

| PostgreSQL | `5433` on host, `5432` inside Docker |

| Redis      | `6379`                               |

| Prometheus | `9090`                               |



\---



\## 20. CI/CD Architecture



```mermaid

flowchart TD

&#x20;   Dev\[Developer Push] --> GitHub\[GitHub Actions]



&#x20;   GitHub --> CI\[CI Workflow]

&#x20;   CI --> Tests\[Run Pytest]

&#x20;   CI --> Lint\[Run Ruff]

&#x20;   CI --> Security\[Run Bandit]



&#x20;   GitHub --> DockerBuild\[Docker Publish Workflow]

&#x20;   DockerBuild --> Image\[Build Docker Image]

&#x20;   Image --> GHCR\[Push to GitHub Container Registry]

```



The CI pipeline protects code quality. The Docker publish pipeline creates a deployable image:



```text

ghcr.io/chauhanmuskan291980-wq/amrutam-telemedicine-backend:latest

```



\---



\## 21. Tradeoffs and Future Improvements



\### Current Tradeoffs



\* Payment gateway is mocked.

\* MFA is designed but not fully implemented.

\* Alembic is included but schema creation currently uses SQLAlchemy metadata.

\* Background jobs are planned but not fully implemented with Celery/RQ.

\* Docker Compose is used for assignment/demo deployment, while production should use Kubernetes or managed cloud services.



\### Future Improvements



\* Add Alembic migrations.

\* Add request ID middleware.

\* Add structured JSON logging.

\* Add OpenTelemetry tracing.

\* Add Grafana dashboard.

\* Add full MFA OTP/TOTP flow.

\* Add real payment gateway integration.

\* Add async notification worker.

\* Add database indexes and migration scripts.

\* Add blue-green deployment strategy.



\---



\## 22. Conclusion



The Amrutam Telemedicine Backend provides a strong production-oriented foundation for a telemedicine platform. It implements the required core workflows, including user lifecycle, doctor availability, booking, consultations, prescriptions, payments, audit logs, admin analytics, idempotent writes, validation, rate limiting, metrics, Docker deployment, and CI/CD.



The architecture is designed to scale horizontally, maintain data consistency during bookings, provide observability through Prometheus, and support secure role-based workflows for patients, doctors, and admins.



