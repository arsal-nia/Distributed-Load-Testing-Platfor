# Requirements

## 1. Purpose

This document defines the functional and non-functional requirements of the Distributed Load Testing Platform.

The purpose is to establish a clear scope for the project and prevent unnecessary features or architectural complexity from being introduced during development.

---

# 2. Functional Requirements

## FR-01 — Create Load Test

The system shall allow a user to create a load test by specifying parameters such as:

* Target URL
* Number of requests
* Concurrency level
* Test duration
* Number of workers

---

## FR-02 — Validate Test Configuration

The backend shall validate load-test parameters before starting a test.

Invalid or unsafe configurations shall be rejected.

---

## FR-03 — Start Load Test

The system shall allow the user to start a configured load test.

The backend shall create a test job and distribute the required workload to available workers.

---

## FR-04 — Distributed Work Execution

Multiple worker instances shall be capable of executing portions of the same load-test job.

Workers shall operate independently from the coordinator.

---

## FR-05 — Worker Communication

Workers shall communicate with the coordination system to:

* Receive work
* Report status
* Report results
* Indicate failures

---

## FR-06 — Job Management

The backend shall maintain the state of load-test jobs.

A job shall have states such as:

```text
CREATED
RUNNING
COMPLETED
FAILED
STOPPED
```

---

## FR-07 — Stop Load Test

The user shall be able to stop a running load test.

The system shall communicate the stop request to the relevant workers.

---

## FR-08 — Collect Results

The system shall collect results from workers, including information such as:

* Total requests
* Successful requests
* Failed requests
* Response times
* HTTP status codes
* Worker-level results

---

## FR-09 — Calculate Performance Metrics

The system shall calculate or expose metrics including:

* Requests per second
* Error rate
* Average latency
* P50 latency
* P95 latency
* P99 latency
* HTTP status-code distribution

---

## FR-10 — Store Test Information

The system shall persist important information about load-test jobs and their results.

PostgreSQL will be used for persistent application data.

---

## FR-11 — Display Test Results

The frontend shall display the status and results of load tests in a readable dashboard.

---

## FR-12 — Multiple Worker Support

The system shall support running multiple worker containers simultaneously.

Adding additional workers shall allow the workload to be distributed across more execution instances.

---

## FR-13 — Worker Failure Detection

The system shall be capable of detecting when a worker becomes unavailable during a test.

The system should prevent the failure of one worker from unnecessarily crashing the entire platform.

---

## FR-14 — Metrics and Monitoring

The system shall expose system metrics that can be monitored using Prometheus and visualized using Grafana.

---

## FR-15 — Containerized Deployment

The major system components shall be runnable as Docker containers.

The initial deployment environment will be a local Docker environment.

---

# 3. Non-Functional Requirements

## NFR-01 — Scalability

The architecture shall support horizontal scaling of workers.

The system should be able to increase the number of worker instances without fundamentally changing the application architecture.

---

## NFR-02 — Reliability

Failure of an individual worker should be isolated as much as reasonably possible.

The coordinator should remain operational when an individual worker fails.

---

## NFR-03 — Performance

The system should be capable of generating a meaningful amount of concurrent HTTP traffic while maintaining reasonable resource usage on the development machine.

The project does not require production-scale traffic generation.

---

## NFR-04 — Maintainability

The codebase shall have clearly separated responsibilities.

Components should communicate through well-defined interfaces.

---

## NFR-05 — Observability

Important system behavior should be measurable through logs and metrics.

The system should make it possible to determine:

* What a component is doing
* Whether it is healthy
* Where failures occur
* How much work it is processing

---

## NFR-06 — Security

The system shall:

* Require appropriate authorization before executing tests.
* Apply limits to test configuration.
* Avoid exposing workers unnecessarily.
* Use controlled networking during development.
* Prevent accidental unrestricted load generation.

---

## NFR-07 — Resource Constraints

The system shall be designed to run on the developer's available hardware.

VMs are not required.

Docker containers shall be used to simulate multiple distributed components locally.

---

# 4. Out of Scope

The following are intentionally **not required** for the initial project.

### Cloud Infrastructure

No AWS, Azure, or Google Cloud deployment is required.

### Virtual Machines

VM-based deployment is out of scope.

### Production-Scale Load Testing

The project does not aim to compete with commercial load-testing infrastructure in request volume.

### Forced Microservices

The system will not be divided into microservices simply to satisfy an architectural pattern.

Services will only be separated when there is a genuine architectural reason.

### Advanced Authentication

A basic authentication/authorization mechanism may be implemented, but a complete enterprise identity system is out of scope.

### Mobile Application

No mobile application is planned.

### Multi-Region Deployment

Workers will initially operate within the local development environment.

---

# 5. Project Success Criteria

The project will be considered successful when:

1. A user can create a load test through the frontend.
2. The backend can create and manage the corresponding job.
3. The workload can be distributed across multiple Docker workers.
4. Workers can execute the test concurrently.
5. Workers can return results to the system.
6. The system can calculate meaningful performance metrics.
7. Results can be displayed through the dashboard.
8. Workers can be scaled horizontally.
9. Worker failure can be detected and handled.
10. The complete system can run locally using Docker.

---

# 6. Guiding Principle

> **Build only what contributes to demonstrating a real distributed load-testing system.**

Features and technologies should be introduced because they solve an actual problem in the system, not merely because they are popular technologies.
