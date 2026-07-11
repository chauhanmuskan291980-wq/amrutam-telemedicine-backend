# Observability: Amrutam Telemedicine Backend

This document explains the observability setup for the Amrutam Telemedicine Backend.

Observability helps developers and operators understand the health, performance, and behavior of the backend system. It is important for production systems because it helps detect failures, monitor latency, debug issues, and maintain reliability.

The current observability setup includes:

* Health check endpoint
* Readiness endpoint
* Redis health endpoint
* Prometheus metrics endpoint
* Prometheus container in Docker Compose
* CI checks for reliability before deployment

---

## 1. Observability Goals

The main goals of observability are:

1. Verify whether the backend is running.
2. Verify whether the backend is ready to serve traffic.
3. Monitor API request count and latency.
4. Track error rates.
5. Monitor Redis availability.
6. Monitor service behavior using Prometheus.
7. Support debugging during development and demo.
8. Prepare the system for production monitoring.

---

## 2. Observability Architecture

```mermaid id="i0o6c7"
flowchart TD
    Client[Client / Swagger / Frontend] --> API[FastAPI Application]

    API --> Health[/health Endpoint]
    API --> Ready[/ready Endpoint]
    API --> RedisHealth[/health/redis Endpoint]
    API --> Metrics[/metrics Endpoint]

    Prometheus[Prometheus Server] --> Metrics

    Docker[Docker Compose] --> API
    Docker --> Redis[(Redis)]
    Docker --> Postgres[(PostgreSQL)]
    Docker --> Prometheus
```

Prometheus scrapes metrics from the FastAPI application using the `/metrics` endpoint.

---

## 3. Health Check Endpoint

Endpoint:

```http id="9p8tf9"
GET /health
```

Purpose:

The health endpoint confirms that the FastAPI application is running.

Example response:

```json id="jogvzz"
{
  "status": "healthy"
}
```

Usage:

```bash id="m8jy16"
curl http://127.0.0.1:8000/health
```

This endpoint is useful for:

* Local testing
* Docker health checks
* Load balancer health checks
* Uptime monitoring

---

## 4. Readiness Endpoint

Endpoint:

```http id="l1qgoo"
GET /ready
```

Purpose:

The readiness endpoint confirms whether the application is ready to serve requests.

Example response:

```json id="24wbi6"
{
  "status": "ready"
}
```

Usage:

```bash id="1pa43z"
curl http://127.0.0.1:8000/ready
```

Readiness checks are important in production because a container may be running but not ready to serve traffic yet.

---

## 5. Redis Health Endpoint

Endpoint:

```http id="o1c0e8"
GET /health/redis
```

Purpose:

This endpoint checks Redis availability.

If Redis is enabled and reachable, expected response:

```json id="7z3eaz"
{
  "status": "redis healthy"
}
```

If Redis is disabled for local development, expected response:

```json id="0xdt5n"
{
  "status": "redis disabled",
  "mode": "in-memory cache"
}
```

Usage:

```bash id="fbmacd"
curl http://127.0.0.1:8000/health/redis
```

Redis is used for:

* Doctor search caching
* Rate-limit counter storage in Docker/production mode

---

## 6. Prometheus Metrics Endpoint

Endpoint:

```http id="izt6nf"
GET /metrics
```

Purpose:

The `/metrics` endpoint exposes application metrics in Prometheus format.

Usage:

```bash id="nbns81"
curl http://127.0.0.1:8000/metrics
```

The metrics endpoint is generated using:

```text id="hwsquz"
prometheus-fastapi-instrumentator
```

Prometheus can use these metrics to monitor:

* Total HTTP requests
* Request duration
* Status codes
* Endpoint-level traffic
* Error rates

---

## 7. Prometheus Setup

Prometheus is included in Docker Compose.

Prometheus UI:

```text id="550beb"
http://127.0.0.1:9090
```

FastAPI metrics endpoint:

```text id="ie3f15"
http://127.0.0.1:8000/metrics
```

Prometheus config file:

```text id="l9vsef"
infra/prometheus.yml
```

Configuration:

```yaml id="2cehck"
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "amrutam-api"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["app:8000"]
```

This means Prometheus scrapes metrics from the FastAPI app container every 15 seconds.

---

## 8. Docker Compose Observability Setup

Docker Compose runs the following services:

| Service      | Purpose                    | Port           |
| ------------ | -------------------------- | -------------- |
| `app`        | FastAPI backend            | `8000`         |
| `db`         | PostgreSQL database        | `5433` on host |
| `redis`      | Cache and rate-limit store | `6379`         |
| `prometheus` | Metrics monitoring         | `9090`         |

Start all services:

```bash id="c2lml4"
docker compose up --build
```

Start in background:

```bash id="k9a2ww"
docker compose up -d --build
```

Check running containers:

```bash id="qlvagv"
docker ps
```

Stop services:

```bash id="lnhcfz"
docker compose down
```

---

## 9. How to Verify Observability

After running Docker Compose, verify these URLs:

| URL                                  | Expected Result            |
| ------------------------------------ | -------------------------- |
| `http://127.0.0.1:8000/health`       | Backend health response    |
| `http://127.0.0.1:8000/ready`        | Backend readiness response |
| `http://127.0.0.1:8000/health/redis` | Redis health response      |
| `http://127.0.0.1:8000/metrics`      | Prometheus metrics text    |
| `http://127.0.0.1:9090`              | Prometheus UI              |

In Prometheus:

1. Open `http://127.0.0.1:9090`
2. Go to **Status**
3. Click **Targets**
4. Confirm `amrutam-api` is shown as `UP`

---

## 10. Important Metrics

Useful metrics for this backend include:

| Metric Area                | What It Shows                         |
| -------------------------- | ------------------------------------- |
| Request count              | Number of API requests                |
| Request latency            | How long APIs take to respond         |
| Status codes               | Number of 2xx, 4xx, and 5xx responses |
| Endpoint traffic           | Which endpoints are used most         |
| Error rate                 | How many requests are failing         |
| Request duration histogram | Latency distribution                  |

These metrics help understand system behavior during:

* API testing
* Demo
* Load testing
* Production monitoring
* Debugging incidents

---

## 11. Example Prometheus Queries

In Prometheus UI, example queries can include:

### Total HTTP Requests

```promql id="7auq9p"
http_requests_total
```

### Request Duration

```promql id="p0583o"
http_request_duration_seconds
```

### Request Count by Status Code

```promql id="s8juyx"
sum by (status) (http_requests_total)
```

### Request Count by Handler

```promql id="cx1p29"
sum by (handler) (http_requests_total)
```

### 95th Percentile Latency

```promql id="schra4"
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

Note: Exact metric names may vary based on the instrumentator version and generated labels.

---

## 12. Logging Strategy

The current backend uses standard application logs through Uvicorn/FastAPI.

Current logging includes:

* Request logs
* Error logs
* Application startup logs
* Docker container logs

View app logs:

```bash id="o52dwh"
docker logs amrutam_api
```

Follow app logs live:

```bash id="tj444h"
docker logs -f amrutam_api
```

Recommended production logging improvements:

1. Structured JSON logs.
2. Request ID middleware.
3. Correlation ID across services.
4. Log levels: INFO, WARNING, ERROR.
5. Centralized log storage.
6. Sensitive data redaction.
7. Log retention policy.

Recommended tools:

* ELK Stack
* Grafana Loki
* AWS CloudWatch
* Google Cloud Logging
* Azure Monitor

---

## 13. Tracing Strategy

Distributed tracing is not fully implemented in the current assignment version.

Recommended future tracing setup:

| Tool          | Purpose                    |
| ------------- | -------------------------- |
| OpenTelemetry | Generate traces            |
| Jaeger        | Trace visualization        |
| Tempo         | Grafana-compatible tracing |
| Zipkin        | Distributed tracing UI     |

Tracing would help debug flows such as:

* Login request
* Doctor search
* Booking workflow
* Payment confirmation
* Prescription creation

Example booking trace:

```text id="umotm9"
POST /consultations/book
→ Validate JWT
→ Check idempotency key
→ Check slot availability
→ Create consultation
→ Create payment
→ Create audit log
→ Return response
```

---

## 14. Alerting Strategy

Alerting is recommended for production.

Important alerts:

| Alert                  | Condition                           |
| ---------------------- | ----------------------------------- |
| High error rate        | 5xx responses above threshold       |
| High latency           | p95 latency above target            |
| API down               | `/health` failing                   |
| Redis down             | `/health/redis` failing             |
| Database unavailable   | Readiness failure                   |
| High login failures    | Possible brute-force attack         |
| High booking conflicts | Possible abuse or concurrency issue |
| High memory/CPU        | Infrastructure overload             |

Recommended alert tools:

* Prometheus Alertmanager
* Grafana Alerts
* Cloud provider alerts

---

## 15. Reliability Targets

The assignment requirement includes:

| Target              | Requirement         |
| ------------------- | ------------------- |
| Read latency        | p95 less than 200ms |
| Write latency       | p95 less than 500ms |
| Availability        | 99.95%              |
| Daily consultations | 100k                |

Observability supports these targets by tracking:

* Request latency
* Error rate
* Uptime
* Traffic volume
* Endpoint performance
* Infrastructure health

---

## 16. Monitoring the Booking Flow

Booking is the most critical workflow.

Important booking observations:

| Signal                      | Why It Matters                  |
| --------------------------- | ------------------------------- |
| Booking request count       | Measures usage                  |
| Booking latency             | Shows user experience           |
| Booking 409 conflicts       | Detects double-booking attempts |
| Booking 401/403 errors      | Detects auth/role issues        |
| Booking 5xx errors          | Detects backend failures        |
| Payment creation failures   | Detects transaction issues      |
| Audit log creation failures | Detects compliance risk         |

Recommended production metrics:

```text id="5amoxf"
consultation_booking_total
consultation_booking_success_total
consultation_booking_conflict_total
consultation_booking_failure_total
payment_creation_total
audit_log_write_total
```

---

## 17. Monitoring Authentication

Authentication should be monitored carefully.

Important signals:

| Signal               | Why It Matters       |
| -------------------- | -------------------- |
| Login success count  | Normal usage         |
| Login failure count  | Possible brute force |
| Registration count   | Growth or spam       |
| 429 rate limit count | Abuse protection     |
| Invalid token count  | Suspicious activity  |

Recommended production alerts:

* Too many failed logins from same IP
* Sudden spike in registration attempts
* Repeated token validation failures

---

## 18. Monitoring Redis

Redis supports cache and rate limiting.

Important signals:

| Signal                | Why It Matters                |
| --------------------- | ----------------------------- |
| Redis health          | Cache/rate-limit availability |
| Cache hit rate        | Performance efficiency        |
| Cache miss rate       | DB load                       |
| Rate-limit key growth | Abuse or traffic spike        |
| Redis memory usage    | Capacity planning             |

If Redis fails, the backend can still run in fallback mode, but production should alert immediately.

---

## 19. Monitoring PostgreSQL

PostgreSQL is the primary system of record.

Recommended production signals:

| Signal           | Why It Matters                    |
| ---------------- | --------------------------------- |
| Connection count | Detect connection exhaustion      |
| Query latency    | Detect slow queries               |
| Lock waits       | Detect booking concurrency issues |
| Deadlocks        | Detect transaction problems       |
| Disk usage       | Prevent outage                    |
| Replication lag  | Read replica health               |
| Backup success   | Disaster recovery readiness       |

Recommended production tools:

* PostgreSQL exporter
* Managed database monitoring
* Slow query logs
* Query performance dashboard

---

## 20. Observability in CI/CD

CI/CD contributes to reliability before deployment.

Current CI checks:

| Check                   | Tool                      |
| ----------------------- | ------------------------- |
| Unit/API tests          | Pytest                    |
| Linting                 | Ruff                      |
| Security scan           | Bandit                    |
| PostgreSQL service test | GitHub Actions service    |
| Docker image publish    | GitHub Container Registry |

These checks reduce production risk by catching issues before code is deployed.

---

## 21. Future Improvements

Recommended future observability improvements:

1. Add structured JSON logging.
2. Add request ID middleware.
3. Add OpenTelemetry tracing.
4. Add Grafana dashboard.
5. Add Prometheus Alertmanager.
6. Add PostgreSQL exporter.
7. Add Redis exporter.
8. Add custom business metrics.
9. Add centralized log storage.
10. Add uptime monitoring.
11. Add SLO dashboards.
12. Add alert rules for p95 latency and 5xx errors.

---

## 22. Conclusion

The Amrutam Telemedicine Backend includes a solid baseline observability setup.

Implemented observability features include:

* `/health`
* `/ready`
* `/health/redis`
* `/metrics`
* Prometheus integration
* Docker Compose monitoring stack
* CI checks for test, lint, and security

This setup allows reviewers and developers to verify service health, inspect metrics, monitor API behavior, and understand the backend’s operational readiness.

For real production deployment, the next major improvements would be structured logging, request tracing, Grafana dashboards, alerting, PostgreSQL metrics, Redis metrics, and centralized log management.
