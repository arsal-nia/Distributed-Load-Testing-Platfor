# AI Context

## Project

**Distributed Load Testing Platform**

A distributed, containerized, worker-based load-testing platform designed to demonstrate distributed systems and system-design concepts.

---

## Primary Goal

Build a working system that can:

1. Accept load-test configurations.
2. Create and manage test jobs.
3. Distribute workload across multiple workers.
4. Generate HTTP traffic against an authorized target.
5. Collect and aggregate results.
6. Measure performance metrics.
7. Display results through a dashboard.
8. Scale workers horizontally.
9. Handle worker/component failures.
10. Demonstrate real distributed-system behavior.

---

## Current Architecture

```text
User
  ↓
React Frontend
  ↓
FastAPI Backend / Coordinator
  ↓
Redis
  ↓
Multiple Docker Workers
  ↓
Controlled Test Target

Metrics
  ↓
Prometheus
  ↓
Grafana
```

PostgreSQL provides persistent application storage.

---

## Architecture Classification

The project is primarily:

> **A distributed, containerized, worker-based client-server system with horizontal scalability.**

It is **not required to be a microservices architecture**.

Microservices may be introduced only when a genuine architectural reason exists.

---

## Technology Stack

* Python
* FastAPI
* React
* Redis
* PostgreSQL
* Docker
* Prometheus
* Grafana

The project is developed locally.

VMs and cloud infrastructure are not required.

---

## Important Architectural Decisions

### Docker Instead of VMs

Docker containers are used to simulate independent system components while keeping resource usage manageable.

### Redis

Used primarily for task distribution, coordination, and temporary state.

### PostgreSQL

Used for persistent application data.

### Workers

Workers perform the actual load generation.

The backend coordinates work but does not generate the load itself.

### Local Test Target

The initial target is a service under our control so that load testing can be performed safely.

### No Forced Microservices

Do not split the system into microservices merely to follow a pattern.

### Horizontal Scaling

The project should demonstrate scaling by adding worker instances.

---

## Development Philosophy

The project is being built incrementally.

Do not implement the entire system at once.

Each stage should:

1. Solve a specific problem.
2. Be implemented.
3. Be tested.
4. Be understood.
5. Be documented when necessary.

---

## Current Development Stage

**Planning / Documentation**

The next implementation stage is:

> **Stage 1 — Basic HTTP Load Generator**

---

## Development Roadmap

```text
1. Basic HTTP Load Generator
2. Test Target Service
3. FastAPI Backend
4. Job Management
5. Containerized Worker
6. Multiple Workers
7. Redis Coordination
8. PostgreSQL Persistence
9. Metrics
10. Dashboard
11. Horizontal Scaling
12. Autoscaling
13. Failure Handling
14. Networking & Security
15. Evaluation
```

---

## AI Rules

When assisting with this project:

### Rule 1 — Follow Existing Architecture

Do not redesign the architecture without a clear reason.

### Rule 2 — Follow the Current Stage

Do not implement future-stage functionality unless explicitly requested.

### Rule 3 — Explain Before Implementing

When introducing an important component or technology, explain:

* What it is.
* Why we need it.
* What problem it solves.
* How it fits into the architecture.

### Rule 4 — No Unnecessary Technologies

Do not introduce technologies simply because they are popular.

### Rule 5 — No Forced Microservices

Do not create microservices unless there is a genuine architectural justification.

### Rule 6 — Respect Documentation

The following documents are the project's source of truth:

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

### Rule 7 — Preserve Existing Work

Do not rewrite working components unnecessarily.

Prefer incremental changes.

### Rule 8 — Keep the Developer in Control

The developer should understand the purpose and behavior of every major component.

AI-generated code should not be treated as a black box.

---

## Safety

Load tests must only target:

* Locally controlled systems.
* Systems owned by the developer.
* Systems where explicit permission has been granted.

Do not introduce functionality that enables unrestricted public load generation.

---

## Final Principle

> **The goal is not to use as many technologies as possible. The goal is to understand and build a real distributed system.**
