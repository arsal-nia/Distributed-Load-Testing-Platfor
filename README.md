# Distributed Load Testing Platform

## Overview

A distributed load testing platform designed to simulate concurrent HTTP traffic against an authorized target system and demonstrate real-world system design concepts.

The platform will allow users to create load tests, distribute the workload across multiple workers, collect performance metrics, and visualize the results through a dashboard.

The project is primarily focused on learning and implementing **distributed systems, scalability, concurrency, containerization, networking, fault tolerance, and observability**.

---

## Main Goals

* Build a working distributed load testing system.
* Understand how a coordinator distributes work across multiple workers.
* Run multiple workers using Docker containers.
* Measure latency, throughput, errors, and other performance metrics.
* Support horizontal scaling of workers.
* Handle worker failures and unavailable components.
* Monitor the system using metrics and dashboards.
* Apply proper networking and security practices.
* Understand system-design tradeoffs through actual implementation.

---

## Core Features

### 1. Load Testing

Users can configure a test such as:

* Target URL
* Number of requests
* Concurrency
* Test duration
* Number of workers

The system generates HTTP traffic against an authorized target.

### 2. Distributed Workers

The workload can be distributed across multiple independent worker containers.

```text
                ┌── Worker 1
                ├── Worker 2
Coordinator ────┼── Worker 3
                └── Worker N
```

### 3. Job Management

The backend will:

* Create load-test jobs
* Track job status
* Distribute work
* Start and stop tests
* Track worker activity

### 4. Metrics and Observability

The system will collect metrics such as:

* Requests per second
* Response time
* P50 / P95 / P99 latency
* Error rate
* HTTP status codes
* Successful requests
* Failed requests
* Worker utilization

### 5. Dashboard

A web interface will allow users to:

* Create tests
* Start/stop tests
* View test status
* View performance metrics
* Analyze test results

### 6. Horizontal Scaling

The system will eventually support increasing or decreasing the number of workers based on workload.

The goal is to demonstrate how a distributed system can scale by adding more worker instances rather than making one machine increasingly powerful.

### 7. Failure Handling

The system will be designed to handle situations such as:

* Worker failure
* Worker disconnection
* Job failure
* Redis unavailability
* Invalid test configuration

---

## Architecture

The initial architecture will be:

```text
                    ┌──────────────┐
                    │   Frontend   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    FastAPI   │
                    │   Backend    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Redis     │
                    │ Queue/State  │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌─────────┐  ┌─────────┐  ┌─────────┐
         │ Worker 1│  │ Worker 2│  │ Worker 3│
         └────┬────┘  └────┬────┘  └────┬────┘
              │            │            │
              └────────────┼────────────┘
                           ▼
                     Test Target
                           │
                           ▼
                     Metrics System
                           │
                           ▼
                    Dashboard/Grafana
```

The project is primarily a **distributed, containerized, worker-based system**.

Microservices will **not be forced into the architecture**. Services will only be separated when there is a genuine architectural reason to do so.

---

## Technology Stack

| Component                 | Technology                          |
| ------------------------- | ----------------------------------- |
| Backend                   | Python + FastAPI                    |
| Frontend                  | React                               |
| Task Queue / Coordination | Redis                               |
| Database                  | PostgreSQL                          |
| Workers                   | Python                              |
| Containerization          | Docker                              |
| Metrics                   | Prometheus                          |
| Visualization             | Grafana                             |
| Deployment                | Local Docker environment            |
| Autoscaling               | To be determined during development |

All core technologies are open-source and can be used locally.

---

## Safety

The load-testing system will only be used against:

* Systems owned by the developer
* Local test environments
* Systems where explicit permission to perform load testing has been given

The project will initially use a **locally controlled test target** to avoid accidentally generating traffic against external services.

---

## Development Philosophy

The project will be developed incrementally.

The system will not begin with unnecessary complexity. Components will be introduced when they solve an actual problem.

The project will prioritize understanding:

* Why each component exists
* How components communicate
* How data flows through the system
* What happens when components fail
* How the system scales
* What tradeoffs each architectural decision introduces

AI tools may be used during development, but the architecture, design decisions, and implementation should remain understandable to the developer.

---

## Development Roadmap

1. Basic HTTP load generator
2. Local test-target service
3. FastAPI backend
4. Job creation and management
5. Containerized worker
6. Multiple workers
7. Redis-based task distribution
8. Persistent job/test data with PostgreSQL
9. Metrics collection
10. Dashboard
11. Horizontal worker scaling
12. Autoscaling
13. Failure handling
14. Networking and security improvements
15. Performance testing and system evaluation

VM-based deployment is **not required** for this project.

---

## Project Status

**Current stage:** Planning and architecture design.

The project will be implemented incrementally, with each architectural component understood and documented before moving to the next major component.
