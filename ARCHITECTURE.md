# Architecture

## 1. Architecture Overview

The Distributed Load Testing Platform will use a:

> **Distributed, containerized, worker-based client-server architecture with horizontal scalability.**

The system will consist of multiple independent components that communicate over defined interfaces.

Docker containers will be used to run and isolate the components locally.

Virtual machines are **not required**.

---

# 2. High-Level Architecture

```text
                         ┌───────────────┐
                         │     User      │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │    Frontend   │
                         │    (React)    │
                         └───────┬───────┘
                                 │ HTTP
                                 ▼
                         ┌───────────────┐
                         │    Backend    │
                         │   (FastAPI)   │
                         └───────┬───────┘
                                 │
                         ┌───────┴────────┐
                         │                │
                         ▼                ▼
                  ┌─────────────┐  ┌─────────────┐
                  │    Redis    │  │ PostgreSQL  │
                  │ Queue/State │  │  Persistent │
                  └──────┬──────┘  │    Data     │
                         │         └─────────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Worker 1 │ │ Worker 2 │ │ Worker 3 │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             └────────────┼────────────┘
                          ▼
                    ┌───────────┐
                    │   Target  │
                    │  Service  │
                    └───────────┘

                    Metrics
                       │
                       ▼
                ┌─────────────┐
                │ Prometheus  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │   Grafana   │
                └─────────────┘
```

---

# 3. Main Components

## 3.1 Frontend

**Technology:** React

The frontend provides the user interface for interacting with the platform.

Responsibilities:

* Configure load tests
* Start and stop tests
* View job status
* View results
* Display performance metrics

The frontend does not execute load tests itself.

---

## 3.2 Backend / Coordinator

**Technology:** Python + FastAPI

The backend acts as the central coordination component.

Responsibilities:

* Receive requests from the frontend
* Validate load-test configurations
* Create jobs
* Manage job state
* Schedule work
* Communicate with Redis
* Track workers
* Store application data
* Provide APIs to the frontend

The backend does **not** generate the actual load.

---

## 3.3 Redis

Redis will initially be used for:

* Task/job distribution
* Temporary job state
* Worker coordination
* Communication between the coordinator and workers

Redis provides a mechanism for decoupling job creation from job execution.

Example:

```text
Backend
   │
   │ Add job
   ▼
 Redis Queue
   │
   ├──────► Worker 1
   ├──────► Worker 2
   └──────► Worker 3
```

---

## 3.4 Workers

Workers are independent processes running inside Docker containers.

Their primary responsibility is:

> **Execute assigned portions of a load-test job.**

A worker will:

1. Receive work.
2. Generate HTTP requests.
3. Measure responses.
4. Collect local statistics.
5. Report results.
6. Report its status.

Workers should remain as independent as possible so that additional workers can be added without modifying the core system.

---

## 3.5 PostgreSQL

PostgreSQL will provide persistent storage.

It may store:

* Users
* Load-test configurations
* Job information
* Job status
* Test summaries
* Historical results

Redis is intended for fast temporary coordination, while PostgreSQL is intended for persistent application data.

---

## 3.6 Metrics System

The platform will expose operational and load-testing metrics.

Prometheus will collect metrics from the system.

Grafana will provide visualization.

Example:

```text
Workers / Backend
       │
       │ Metrics
       ▼
  Prometheus
       │
       ▼
    Grafana
```

The exact division between application results and Prometheus metrics will be determined during implementation.

---

# 4. Test Target

The initial test target will be a **locally controlled HTTP service**.

This allows the platform to safely test different behaviors without generating unauthorized traffic.

The target service may eventually provide endpoints such as:

```text
/fast
/slow
/error
/cpu
/large-response
```

These endpoints will allow controlled experiments involving different response times, errors, and workloads.

---

# 5. Request Flow

A typical load-test request will follow this process:

```text
1. User
   ↓
2. Frontend
   ↓
3. FastAPI
   ↓
4. Validate configuration
   ↓
5. Create job
   ↓
6. Redis
   ↓
7. Workers receive work
   ↓
8. Workers generate requests
   ↓
9. Target service responds
   ↓
10. Workers collect results
   ↓
11. Results/metrics return to platform
   ↓
12. Backend stores/aggregates results
   ↓
13. Frontend displays results
```

---

# 6. Worker Scaling

Workers are designed to scale horizontally.

For example:

```text
              Coordinator
                   │
             ┌─────┴─────┐
             │   Redis   │
             └─────┬─────┘
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       Worker 1 Worker 2 Worker 3
```

If more capacity is required:

```text
          ┌────────┼────────┬────────┬────────┐
          ▼        ▼        ▼        ▼        ▼
       Worker 1 Worker 2 Worker 3 Worker 4 Worker 5
```

The coordinator does not need to become more powerful simply because more workers are added.

---

# 7. Containerization

Each major component will run in a Docker container where appropriate.

Example:

```text
Docker Environment

┌───────────────────────────────────────────┐
│                                           │
│  Frontend     Backend      Redis          │
│                                           │
│  PostgreSQL   Worker 1     Worker 2       │
│                                           │
│  Worker 3     Prometheus   Grafana        │
│                                           │
└───────────────────────────────────────────┘
```

Docker provides process isolation and allows multiple worker instances to be created from the same worker image.

---

# 8. Communication

The system will use different communication mechanisms for different purposes.

### Frontend → Backend

HTTP/REST APIs.

### Backend → Redis

Redis commands / queue operations.

### Redis → Workers

Job/task distribution.

### Workers → Backend / Metrics System

Results and metrics.

The exact communication mechanism for worker results will be decided during implementation based on the requirements.

---

# 9. Failure Model

The architecture assumes that individual components can fail.

Examples:

```text
Worker 2 crashes
      ↓
Coordinator detects failure
      ↓
Job continues or work is reassigned
```

Other possible failures include:

* Redis unavailable
* Database unavailable
* Worker disconnected
* Target service unavailable
* Network communication failure

Failure handling will be introduced incrementally rather than attempting to solve every failure scenario initially.

---

# 10. Microservices Policy

Microservices are **not a mandatory architectural requirement**.

The project will not create separate services merely to increase the number of components.

A component may become an independent service if there is a meaningful reason, such as:

* Independent scaling
* Independent deployment
* Clear separation of responsibility
* Fault isolation
* Different resource requirements

Therefore, the architecture may evolve toward microservices where appropriate, but the project remains fundamentally focused on **distributed-system design**.

---

# 11. Deployment Model

The initial deployment model is:

```text
Developer Machine
        │
        ▼
Docker
        │
        ├── Frontend
        ├── Backend
        ├── Redis
        ├── PostgreSQL
        ├── Workers
        ├── Prometheus
        └── Grafana
```

All components can initially run on the same physical machine while still behaving as separate distributed components.

The project does not require:

* Virtual machines
* Cloud infrastructure
* Multiple physical computers

---

# 12. Architectural Goals

The architecture should demonstrate:

* Distributed task execution
* Decoupling
* Horizontal scaling
* Worker coordination
* Concurrent processing
* Fault isolation
* Observability
* Containerization
* Networking
* Performance measurement

The architecture should remain as simple as possible while still providing meaningful distributed-system behavior.
