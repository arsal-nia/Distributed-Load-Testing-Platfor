# Architecture Decisions

This document records important architectural and technical decisions made during development.

The purpose is to document **why** decisions were made, not just what technologies are being used.

---

## ADR-001 — Use Docker Containers

### Decision

Use Docker containers to run the major components of the system.

### Reason

Docker allows us to:

* Run multiple workers independently.
* Easily create and remove worker instances.
* Isolate components.
* Reproduce the same environment.
* Demonstrate distributed behavior on a single physical machine.

### Alternative Considered

Virtual machines.

### Why Not

VMs require significantly more system resources and are not necessary for demonstrating the distributed architecture.

---

## ADR-002 — Do Not Require Virtual Machines

### Decision

VM-based deployment is out of scope.

### Reason

The project can demonstrate distributed architecture using independent Docker containers.

The goal is to understand distributed systems, not to add infrastructure that provides little educational value for this project.

---

## ADR-003 — Use FastAPI for the Backend

### Decision

Use Python + FastAPI for the backend.

### Reason

FastAPI provides:

* Simple HTTP API development
* Request validation
* Automatic API documentation
* Good asynchronous support
* Easy integration with Python-based workers
* Familiarity with the Python ecosystem

---

## ADR-004 — Use Redis for Task Distribution

### Decision

Use Redis as the initial coordination and task-distribution mechanism.

### Reason

The load-testing system needs a way to distribute work between the coordinator and multiple workers.

Redis provides a lightweight mechanism for:

* Queues
* Temporary state
* Fast communication
* Worker coordination

It also allows workers to remain relatively independent from the backend.

---

## ADR-005 — Use PostgreSQL for Persistent Data

### Decision

Use PostgreSQL for persistent application data.

### Reason

The system needs durable storage for information such as:

* Users
* Load-test configurations
* Jobs
* Job status
* Historical test information
* Test summaries

PostgreSQL is well suited for structured relational data.

---

## ADR-006 — Separate Redis and PostgreSQL Responsibilities

### Decision

Redis and PostgreSQL will have different responsibilities.

### Redis

Used primarily for:

* Temporary state
* Queues
* Coordination
* Fast transient communication

### PostgreSQL

Used primarily for:

* Persistent data
* Historical information
* Application records

### Reason

A queue/coordination system and a persistent relational database solve different problems. Keeping their responsibilities separate makes the architecture easier to reason about.

---

## ADR-007 — Use Independent Workers

### Decision

Load generation will be performed by independent worker processes/containers.

### Reason

The primary purpose of the project is to demonstrate distributed workload execution.

Independent workers allow us to demonstrate:

* Parallel execution
* Horizontal scaling
* Worker failure
* Work distribution
* Worker coordination

---

## ADR-008 — Use a Locally Controlled Test Target

### Decision

The initial load-test target will be a service running under our control.

### Reason

This allows safe experimentation without generating unauthorized traffic against external systems.

It also allows us to deliberately create different response behaviors for testing.

---

## ADR-009 — Use Prometheus and Grafana for Observability

### Decision

Use Prometheus for metrics collection and Grafana for visualization.

### Reason

The project needs to demonstrate observability rather than only produce raw test results.

This allows us to monitor:

* Request rates
* Latency
* Errors
* Worker activity
* System resource usage
* Component health

---

## ADR-010 — Do Not Force Microservices

### Decision

Microservices will not be introduced merely because the project is distributed.

### Reason

A distributed system does not automatically need to be a microservices system.

Services will only be separated when there is a meaningful architectural reason, such as:

* Independent scaling
* Independent deployment
* Fault isolation
* Clear responsibility boundaries

### Result

The architecture may eventually contain multiple services, but microservices are an **evolutionary option**, not a forced requirement.

---

## ADR-011 — Start With a Simple Architecture

### Decision

Build the system incrementally rather than implementing every component at once.

### Reason

Introducing too many technologies simultaneously makes it difficult to understand:

* Where failures originate
* How components communicate
* Why a component exists
* Which component is responsible for a problem

The system will therefore grow gradually.

---

## ADR-012 — Local-First Development

### Decision

The initial system will run entirely on the developer's machine using Docker.

### Reason

Local development:

* Avoids cloud costs
* Avoids unnecessary infrastructure
* Makes debugging easier
* Allows rapid experimentation
* Is sufficient for demonstrating distributed behavior

Cloud deployment is not required for the core project.

---

## ADR-013 — Horizontal Scaling Over Vertical Scaling

### Decision

The architecture will emphasize horizontal worker scaling.

### Reason

The load generator should be able to increase capacity by adding workers:

```text
2 workers
   ↓
4 workers
   ↓
8 workers
```

rather than relying only on making a single worker more powerful.

This is one of the central distributed-system concepts the project is intended to demonstrate.

---

## ADR-014 — Architecture Must Follow Actual Requirements

### Decision

Technology choices and architectural patterns will be introduced only when they solve an actual problem.

### Reason

The project is intended to teach system design, not simply demonstrate the use of popular technologies.

Therefore:

> **No technology will be added solely for the sake of saying that the project uses it.**

This applies particularly to microservices, Kubernetes, cloud infrastructure, and other advanced infrastructure.

---

## Decision Status

These decisions represent the current architectural baseline.

They may be changed later if implementation or experimentation reveals a better approach.

Any significant change should be documented here with the reason for the change.
