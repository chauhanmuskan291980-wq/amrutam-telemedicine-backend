# Security Checklist: Amrutam Telemedicine Backend

This document lists the security controls implemented and recommended for the Amrutam Telemedicine Backend.

The backend handles sensitive healthcare-related workflows, so security is important across authentication, authorization, data validation, secrets, audit logging, rate limiting, infrastructure, and CI/CD.

---

## 1. Authentication Security

| Security Control                    | Status      | Notes                                            |
| ----------------------------------- | ----------- | ------------------------------------------------ |
| JWT-based authentication            | Implemented | Users receive access token after login           |
| Password hashing                    | Implemented | Passwords are hashed using bcrypt                |
| Plain-text password storage blocked | Implemented | Only password hashes are stored                  |
| Current user endpoint protected     | Implemented | Requires valid JWT token                         |
| Token expiry configured             | Implemented | Access token expiry is environment-configurable  |
| Strong password validation          | Implemented | Password validation is handled in request schema |
| MFA support                         | Planned     | MFA flag exists, full OTP/TOTP flow can be added |

---

## 2. Authorization and RBAC

The system uses role-based access control.

Supported roles:

```text id="pco8z3"
PATIENT
DOCTOR
ADMIN
```

| Security Control                       | Status      | Notes                                              |
| -------------------------------------- | ----------- | -------------------------------------------------- |
| Role-based access control              | Implemented | Uses dependency-based role checks                  |
| Patient-only booking                   | Implemented | Only patients can book consultations               |
| Doctor-only availability creation      | Implemented | Only doctors can create slots                      |
| Doctor-only prescription creation      | Implemented | Only assigned doctors can create prescriptions     |
| Admin-only analytics                   | Implemented | Admin access required                              |
| Admin-only audit logs                  | Implemented | Admin access required                              |
| Admin self-registration blocked        | Implemented | Public API does not allow admin signup             |
| Cross-user prescription access blocked | Implemented | Patients cannot view other patients’ prescriptions |

---

## 3. Input Validation

Input validation is handled using Pydantic schemas.

| Validation Area                  | Status      | Notes                                           |
| -------------------------------- | ----------- | ----------------------------------------------- |
| Email validation                 | Implemented | Uses email validation                           |
| Phone validation                 | Implemented | Validates Indian mobile number format           |
| Password validation              | Implemented | Enforces safer password input                   |
| Positive ID validation           | Implemented | IDs must be positive integers                   |
| Slot time validation             | Implemented | End time must be after start time               |
| Slot duration validation         | Implemented | Prevents invalid slot duration                  |
| Pagination validation            | Implemented | Limit and offset are validated                  |
| Prescription medicine validation | Implemented | Required medicine fields are checked            |
| Request body validation          | Implemented | Invalid request bodies return validation errors |

---

## 4. Rate Limiting

Rate limiting helps protect sensitive endpoints from abuse.

| Endpoint                   | Limit              | Status      |
| -------------------------- | ------------------ | ----------- |
| `POST /auth/register`      | 5 requests/minute  | Implemented |
| `POST /auth/login`         | 5 requests/minute  | Implemented |
| `POST /consultations/book` | 10 requests/minute | Implemented |

Rate limiting uses:

```text id="qd3xk2"
SlowAPI
Redis in Docker/production mode
Memory fallback in local/test mode
```

---

## 5. Booking Security

Booking is protected because it is a critical write operation.

| Security Control                   | Status                  | Notes                                             |
| ---------------------------------- | ----------------------- | ------------------------------------------------- |
| Idempotency key required           | Implemented             | Prevents duplicate booking writes                 |
| Slot availability checked          | Implemented             | Only available slots can be booked                |
| Double booking prevention          | Implemented             | Slot status changes after booking                 |
| Transaction-safe design            | Implemented/Recommended | Booking should remain inside short DB transaction |
| Conflict response for booked slots | Implemented             | Returns conflict when slot unavailable            |
| Audit log after booking            | Implemented             | Booking action is traceable                       |

---

## 6. Data Protection

| Security Control                 | Status      | Notes                                             |
| -------------------------------- | ----------- | ------------------------------------------------- |
| Passwords hashed                 | Implemented | Uses bcrypt                                       |
| Secrets loaded from environment  | Implemented | Uses environment variables                        |
| No production secret hardcoding  | Implemented | Docker and CI use env variables                   |
| Medical data access restricted   | Implemented | Role and ownership checks are used                |
| Audit logs for sensitive actions | Implemented | Helps compliance and traceability                 |
| Database backup encryption       | Recommended | Should be enabled in production                   |
| Data encryption at rest          | Recommended | Should be enabled using managed DB/cloud settings |
| Data encryption in transit       | Recommended | Use HTTPS/TLS in production                       |

---

## 7. Audit Logging

Audit logs are created for important workflows.

Examples:

```text id="c1bo18"
USER_REGISTERED
DOCTOR_SLOT_CREATED
CONSULTATION_BOOKED
CONSULTATION_STARTED
CONSULTATION_COMPLETED
PRESCRIPTION_CREATED
PAYMENT_CONFIRMED
```

Audit log fields:

```text id="3v3fqw"
user_id
action
resource_type
resource_id
ip_address
user_agent
created_at
```

| Security Control         | Status      | Notes                                            |
| ------------------------ | ----------- | ------------------------------------------------ |
| Audit log table          | Implemented | Stores sensitive actions                         |
| Admin audit log access   | Implemented | Admin-only endpoint                              |
| IP address captured      | Implemented | Used for investigation                           |
| User agent captured      | Implemented | Useful for security review                       |
| Append-only audit design | Recommended | Audit logs should not be modified after creation |

---

## 8. API Security

| Security Control                  | Status      | Notes                                     |
| --------------------------------- | ----------- | ----------------------------------------- |
| Protected routes require JWT      | Implemented | Uses auth dependency                      |
| Role-restricted endpoints         | Implemented | Uses RBAC dependency                      |
| Validation errors handled         | Implemented | FastAPI/Pydantic validation               |
| Rate limit errors handled         | Implemented | Returns 429 when exceeded                 |
| CORS configured                   | Implemented | Allows trusted frontend origin            |
| OpenAPI docs enabled              | Implemented | Useful for review/demo                    |
| Disable public docs in production | Recommended | Optional for stricter production security |
| API gateway/WAF                   | Recommended | Useful in cloud production                |

---

## 9. Infrastructure Security

The project uses Docker Compose for local/demo deployment.

| Security Control         | Status      | Notes                                            |
| ------------------------ | ----------- | ------------------------------------------------ |
| Dockerfile included      | Implemented | App is containerized                             |
| Docker Compose included  | Implemented | Runs API, PostgreSQL, Redis, Prometheus          |
| PostgreSQL health check  | Implemented | Ensures DB readiness                             |
| Redis health check       | Implemented | Ensures Redis readiness                          |
| App restart policy       | Implemented | Containers can restart automatically             |
| Prometheus metrics       | Implemented | Monitoring endpoint available                    |
| Non-root container user  | Recommended | Can be added for stricter production security    |
| Image vulnerability scan | Recommended | Can be added using Trivy or pip-audit            |
| HTTPS termination        | Recommended | Should be handled by load balancer/reverse proxy |

---

## 10. CI/CD Security

GitHub Actions is configured for automated checks.

| Security Control              | Status      | Notes                           |
| ----------------------------- | ----------- | ------------------------------- |
| Automated tests               | Implemented | Pytest runs in CI               |
| Lint check                    | Implemented | Ruff runs in CI                 |
| Security scan                 | Implemented | Bandit runs in CI               |
| PostgreSQL service in CI      | Implemented | Tests run with database service |
| Docker image publishing       | Implemented | Image pushed to GHCR            |
| Protected branch rules        | Recommended | Require CI green before merge   |
| Dependency vulnerability scan | Recommended | Add pip-audit or Safety         |
| Secret scanning               | Recommended | Use GitHub secret scanning      |

---

## 11. Secrets Management

Environment variables used:

```text id="9ewkq0"
DATABASE_URL
REDIS_URL
RATE_LIMIT_STORAGE_URL
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS
```

Checklist:

| Rule                                   | Status      |
| -------------------------------------- | ----------- |
| Do not commit `.env`                   | Implemented |
| Use `.env.example` for sample config   | Recommended |
| Use strong JWT secret in production    | Recommended |
| Rotate secrets periodically            | Recommended |
| Use cloud secret manager in production | Recommended |
| Never log secrets                      | Recommended |

---

## 12. Database Security

| Security Control                    | Status                                     | Notes                                      |
| ----------------------------------- | ------------------------------------------ | ------------------------------------------ |
| SQLAlchemy ORM used                 | Implemented                                | Reduces raw SQL risk                       |
| Parameterized database operations   | Implemented                                | ORM helps prevent SQL injection            |
| Unique email constraint             | Recommended/Implemented depending on model | Prevents duplicate users                   |
| Unique consultation slot constraint | Recommended                                | Prevents double booking at DB level        |
| Indexes for query performance       | Recommended                                | Improves performance and reduces DB stress |
| Least-privilege DB user             | Recommended                                | Use limited DB credentials in production   |
| Backups enabled                     | Recommended                                | Required for production                    |
| PITR/WAL backups                    | Recommended                                | Needed for disaster recovery               |

---

## 13. Healthcare Data Security Considerations

The backend may process sensitive healthcare-related data such as:

* Patient profile details
* Consultation reason
* Prescription medicines
* Doctor-patient consultation history
* Payment records

Recommended production controls:

| Control            | Purpose                               |
| ------------------ | ------------------------------------- |
| HTTPS/TLS          | Protect data in transit               |
| Encryption at rest | Protect database and backups          |
| RBAC               | Restrict access by role               |
| Audit logging      | Track sensitive operations            |
| Data minimization  | Store only required data              |
| Retention policy   | Avoid keeping data longer than needed |
| Backup encryption  | Protect backup copies                 |
| Access reviews     | Regularly review admin access         |

---

## 14. Security Test Cases

The following security-related scenarios should be tested:

| Test Case                                     | Expected Result        |
| --------------------------------------------- | ---------------------- |
| Register patient with weak password           | Request rejected       |
| Register admin from public API                | Request rejected       |
| Login with wrong password                     | Request rejected       |
| Access protected route without token          | Request rejected       |
| Patient accesses another patient prescription | Request rejected       |
| Doctor creates availability                   | Allowed                |
| Patient creates doctor availability           | Rejected               |
| Non-admin accesses analytics                  | Rejected               |
| Duplicate booking with same idempotency key   | Same response returned |
| Booking already booked slot                   | Conflict response      |
| Exceed login rate limit                       | 429 response           |

---

## 15. Security Gaps and Future Improvements

Current project is assignment/demo focused. The following improvements are recommended before real production deployment:

1. Add full MFA using OTP/TOTP.
2. Add HTTPS/TLS through reverse proxy or load balancer.
3. Add Alembic migrations with explicit constraints.
4. Add unique DB constraint on `consultations.slot_id`.
5. Add non-root Docker user.
6. Add dependency vulnerability scanning with `pip-audit`.
7. Add container scanning with Trivy.
8. Add centralized logging.
9. Add OpenTelemetry tracing.
10. Add cloud secret manager.
11. Add encrypted database backups.
12. Add WAF/API gateway.
13. Add branch protection rules in GitHub.
14. Add audit log retention policy.
15. Add production-grade payment gateway security.

---

## 16. Final Security Status

| Area                             | Status                    |
| -------------------------------- | ------------------------- |
| Authentication                   | Implemented               |
| Authorization/RBAC               | Implemented               |
| Password hashing                 | Implemented               |
| Input validation                 | Implemented               |
| Rate limiting                    | Implemented               |
| Idempotency                      | Implemented               |
| Audit logging                    | Implemented               |
| Environment config               | Implemented               |
| Docker infrastructure            | Implemented               |
| CI checks                        | Implemented               |
| Security scan                    | Implemented               |
| MFA                              | Planned                   |
| HTTPS/TLS                        | Production recommendation |
| Encrypted backups                | Production recommendation |
| Container vulnerability scanning | Production recommendation |

---

## 17. Conclusion

The Amrutam Telemedicine Backend includes strong baseline security controls suitable for an assignment-level production backend design.

Implemented security features include JWT authentication, bcrypt password hashing, RBAC, input validation, rate limiting, idempotent booking, audit logging, environment-based configuration, Dockerized infrastructure, and CI security scanning.

For real production deployment, the next important improvements would be MFA, HTTPS/TLS, encrypted backups, database-level constraints, centralized logging, dependency vulnerability scanning, and cloud-based secret management.
