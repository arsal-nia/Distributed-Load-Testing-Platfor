# Project Structure

## 1. Purpose

This document defines the organization of the Distributed Load Testing Platform repository.

The structure is designed to keep each system component separated while keeping the project simple enough to understand and maintain.

---

# 2. Root Structure

```text
distributed-load-testing/
│
├── README.md
├── REQUIREMENTS.md
├── ARCHITECTURE.md
├── DECISIONS.md
├── API_SPEC.md
├── PROJECT_STRUCTURE.md
├── TASKS.md
├── AI_CONTEXT.md
│
├── backend/
├── worker/
├── frontend/
├── target-service/
├── metrics/
├── tests/
│
├── docker/
│
└── docker-compose.yml
```

---

# 3. Documentation

The documentation files remain at the repository root.

```text
README.md
REQUIREMENTS.md
ARCHITECTURE.md
DECISIONS.md
API_SPEC.md
PROJECT_STRUCTURE.md
TASKS.md
AI_CONTEXT.md
```

### README.md

Provides the overall project description.

### REQUIREMENTS.md

Defines what the system must and must not do.

### ARCHITECTURE.md

Defines system components and how they interact.

### DECISIONS.md

Records important architectural decisions and their reasoning.

### API_SPEC.md

Defines communication contracts between components.

### PROJECT_STRUCTURE.md

Defines where project files belong.

### TASKS.md

Tracks implementation progress and the current development task.

### AI_CONTEXT.md

Provides a concise source of truth for AI-assisted development.

---

# 4. Backend

```text
backend/
│
├── app/
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── schemas/
│   ├── database/
│   └── core/
│
├── tests/
│
├── requirements.txt
└── Dockerfile
```

The backend is responsible for the HTTP API and coordination logic.

### `api/`

API endpoints exposed to the frontend.

### `services/`

Application logic such as:

* Job management
* Test coordination
* Worker management

### `models/`

Database models.

### `schemas/`

Request and response validation models.

### `database/`

Database connection and persistence-related code.

### `core/`

Configuration and shared backend functionality.

---

# 5. Worker

```text
worker/
│
├── app/
│   ├── main.py
│   ├── executor.py
│   ├── client.py
│   ├── metrics.py
│   └── config.py
│
├── tests/
│
├── requirements.txt
└── Dockerfile
```

The worker is responsible for executing load-test workloads.

### `executor.py`

Controls the execution of assigned load-test work.

### `client.py`

Handles HTTP requests to the target service.

### `metrics.py`

Collects worker-level measurements.

### `config.py`

Contains worker configuration.

---

# 6. Frontend

```text
frontend/
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── hooks/
│   └── App.jsx
│
├── public/
├── package.json
└── Dockerfile
```

The frontend is responsible only for the user interface and communication with the backend API.

---

# 7. Target Service

```text
target-service/
│
├── app/
│   └── main.py
│
├── requirements.txt
└── Dockerfile
```

This is the controlled HTTP service used as the load-testing target.

It may eventually provide endpoints such as:

```text
/fast
/slow
/error
/cpu
/large-response
```

The target service exists so that load tests can be performed safely and repeatably.

---

# 8. Metrics

```text
metrics/
│
├── prometheus/
│   └── prometheus.yml
│
└── grafana/
    └── dashboards/
```

This directory contains configuration related to monitoring and visualization.

Prometheus collects metrics.

Grafana visualizes them.

---

# 9. Tests

```text
tests/
│
├── integration/
├── system/
└── load/
```

### `integration/`

Tests communication between components.

### `system/`

Tests complete system behavior.

### `load/`

Contains controlled experiments used to evaluate the load-testing platform itself.

---

# 10. Docker

```text
docker/
│
├── backend/
├── worker/
├── frontend/
└── target-service/
```

Dockerfiles may remain inside their respective component directories.

The `docker/` directory is reserved for shared Docker-related configuration that does not naturally belong to one component.

---

# 11. Docker Compose

The initial system will use:

```text
docker-compose.yml
```

to run the local environment.

Conceptually:

```text
docker-compose
      │
      ├── frontend
      ├── backend
      ├── redis
      ├── postgres
      ├── worker
      ├── target-service
      ├── prometheus
      └── grafana
```

Multiple worker containers can be created from the same worker image.

---

# 12. Separation Rules

### Rule 1 — Backend Does Not Generate Load

The backend coordinates tests but does not perform the actual load generation.

### Rule 2 — Workers Generate Load

Workers are responsible for sending requests to the target.

### Rule 3 — Frontend Does Not Contain Business Logic

The frontend communicates with backend APIs rather than directly accessing Redis or PostgreSQL.

### Rule 4 — Workers Do Not Directly Access PostgreSQL

Workers should communicate through the intended coordination/result mechanisms.

They should not directly manipulate application database records.

### Rule 5 — Target Service Is Independent

The target service should remain independent from the load generator.

This allows us to replace it later with another authorized target.

---

# 13. Dependency Direction

The intended dependency direction is:

```text
Frontend
    ↓
Backend
    ↓
Redis / PostgreSQL
    ↓
Workers
    ↓
Target Service
```

This is a conceptual dependency boundary rather than a strict requirement that every component communicate directly with the next component.

---

# 14. Naming Conventions

Use clear names that describe responsibility.

Examples:

```text
job_service.py
worker_manager.py
result_aggregator.py
load_executor.py
metrics_collector.py
```

Avoid vague names such as:

```text
helper.py
stuff.py
misc.py
new.py
test2.py
```

unless their purpose is genuinely temporary.

---

# 15. Structure Evolution

The repository structure may change as the system develops.

New directories or services should only be introduced when there is a clear reason.

The structure should support the architecture rather than dictate it.

---

# 16. Core Principle

> **Every directory and component should have a clear responsibility.**

If it is unclear where a piece of code belongs, the responsibility of that code should be clarified before creating another directory or service.
