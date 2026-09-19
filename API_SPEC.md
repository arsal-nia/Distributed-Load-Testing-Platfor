# API Specification

## 1. Purpose

This document defines the communication interfaces of the Distributed Load Testing Platform.

The API specification establishes what information components send and receive without defining their internal implementation.

The specification may evolve as implementation reveals new requirements.

---

# 2. API Architecture

The initial communication model is:

```text
Frontend
    │
    │ HTTP/REST
    ▼
FastAPI Backend
    │
    ├── PostgreSQL
    │
    └── Redis
          │
          ▼
       Workers
```

The frontend communicates with the backend through REST APIs.

The backend uses Redis for task distribution and coordination.

Workers communicate with the coordination system to receive jobs and report their status/results.

---

# 3. Backend API

Base path:

```text
/api
```

---

## 3.1 Create Load Test

### Endpoint

```http
POST /api/tests
```

### Purpose

Create a new load-test configuration.

### Request

```json
{
  "target_url": "http://target:8000/fast",
  "requests": 10000,
  "concurrency": 100,
  "duration_seconds": 60,
  "workers": 3
}
```

### Response

```json
{
  "test_id": "test_123",
  "status": "CREATED"
}
```

---

# 4. Start Test

### Endpoint

```http
POST /api/tests/{test_id}/start
```

### Purpose

Start an existing load test.

### Response

```json
{
  "test_id": "test_123",
  "status": "RUNNING"
}
```

When started, the backend creates/distributes the required workload through the coordination system.

---

# 5. Stop Test

### Endpoint

```http
POST /api/tests/{test_id}/stop
```

### Purpose

Stop a running load test.

### Response

```json
{
  "test_id": "test_123",
  "status": "STOPPED"
}
```

---

# 6. Get Test Status

### Endpoint

```http
GET /api/tests/{test_id}
```

### Purpose

Retrieve the current state of a load test.

### Response

```json
{
  "test_id": "test_123",
  "status": "RUNNING",
  "workers": 3,
  "started_at": "2026-01-01T12:00:00Z"
}
```

---

# 7. Get Test Results

### Endpoint

```http
GET /api/tests/{test_id}/results
```

### Purpose

Retrieve aggregated results for a completed or running test.

### Example Response

```json
{
  "test_id": "test_123",
  "total_requests": 10000,
  "successful_requests": 9850,
  "failed_requests": 150,
  "requests_per_second": 166.7,
  "average_latency_ms": 42.5,
  "p50_latency_ms": 35.2,
  "p95_latency_ms": 81.4,
  "p99_latency_ms": 120.7,
  "error_rate": 0.015
}
```

---

# 8. List Tests

### Endpoint

```http
GET /api/tests
```

### Purpose

Retrieve previously created load tests.

### Example Response

```json
{
  "tests": [
    {
      "test_id": "test_123",
      "status": "COMPLETED"
    },
    {
      "test_id": "test_124",
      "status": "RUNNING"
    }
  ]
}
```

---

# 9. Worker Communication

Worker communication is intentionally separated from the public frontend API.

Workers need to:

* Receive work
* Report availability
* Report progress
* Report results
* Report failures

The initial implementation will use **Redis-based task distribution**.

The exact Redis data structures and message formats will be defined when the worker system is implemented.

---

# 10. Worker Job Format

A worker may receive a job conceptually similar to:

```json
{
  "job_id": "job_123",
  "test_id": "test_123",
  "target_url": "http://target:8000/fast",
  "requests": 3333,
  "concurrency": 34,
  "duration_seconds": 60
}
```

The coordinator is responsible for dividing the overall test workload among workers.

For example:

```text
Total requests: 10,000

Worker 1 → 3,333
Worker 2 → 3,333
Worker 3 → 3,334
```

The exact distribution algorithm will be decided during implementation.

---

# 11. Worker Result Format

A worker will return information conceptually similar to:

```json
{
  "job_id": "job_123",
  "worker_id": "worker_2",
  "total_requests": 3333,
  "successful_requests": 3280,
  "failed_requests": 53,
  "latencies": {
    "p50": 35.1,
    "p95": 82.4,
    "p99": 121.2
  }
}
```

The coordinator/backend will aggregate results from all workers.

---

# 12. Worker Health

Workers should periodically provide a health/heartbeat signal.

Conceptually:

```text
Worker
   │
   │ heartbeat
   ▼
Coordinator
```

If a worker stops reporting for an appropriate period, the coordinator can mark it as unavailable.

The exact heartbeat interval and failure timeout will be determined during implementation.

---

# 13. Error Responses

The API should use standard HTTP status codes.

Examples:

| Status | Meaning                      |
| ------ | ---------------------------- |
| 200    | Request successful           |
| 201    | Resource created             |
| 400    | Invalid request              |
| 404    | Resource not found           |
| 409    | Invalid state/conflict       |
| 422    | Validation failure           |
| 500    | Internal server error        |
| 503    | Required service unavailable |

Example:

```json
{
  "error": "Invalid test configuration",
  "message": "Concurrency must be greater than 0"
}
```

---

# 14. Test State Model

A test follows a controlled lifecycle:

```text
        ┌─────────┐
        │ CREATED │
        └────┬────┘
             │ start
             ▼
        ┌─────────┐
        │ RUNNING │
        └────┬────┘
          ┌──┴───┐
          │      │
       finish   stop
          │      │
          ▼      ▼
     COMPLETED  STOPPED

RUNNING ──────────────► FAILED
```

The backend shall prevent invalid state transitions.

For example:

```text
COMPLETED → RUNNING
```

should not normally be allowed.

---

# 15. API Design Principles

The API should follow these principles:

### Clear Responsibilities

Each endpoint should have one clear purpose.

### Validation

Invalid configurations should be rejected before work is distributed.

### Stateless HTTP API

The frontend API should avoid relying on server-side connection state.

Persistent state should be stored in the appropriate data store.

### Versioning

If the API eventually becomes externally consumed, versioning can be introduced, for example:

```text
/api/v1/tests
```

This is not required for the initial implementation.

---

# 16. Future API Extensions

Potential future endpoints include:

```text
GET  /api/workers
GET  /api/workers/{worker_id}
GET  /api/system/health
GET  /api/metrics
```

These will only be implemented if they become necessary.

---

# 17. Important Design Rule

The API specification defines **contracts**, not implementation details.

For example:

> The specification says that a worker must receive a job and return results.

It does not yet dictate exactly whether this will use:

* Redis Lists
* Redis Streams
* Pub/Sub
* Another messaging mechanism

Those implementation decisions will be documented separately when we reach that stage.
