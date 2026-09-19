# PROMPT.md
## Master AI Coding Control — Distributed Load Testing Platform

This file is the master operating procedure for AI-assisted development of this project.

## 1. Source of truth
Before doing any work, read the supplied project documents. Treat them as authoritative in this order:

1. `REQUIREMENTS.md` — what the system must/must not do.
2. `ARCHITECTURE.md` — component boundaries and system design.
3. `DECISIONS.md` — approved architectural decisions and rationale.
4. `API_SPEC.md` — API contracts.
5. `PROJECT_STRUCTURE.md` — where code belongs.
6. `TASKS.md` — current stage and scope.
7. `AI_CONTEXT.md` — compact project briefing.
8. `PROMPT.md` — these AI execution rules.
9. `CHANGELOG.md` — historical context; current documents override history.

If a document is missing, do not invent its contents. Tell me which document is missing.

## 2. Non-negotiable rules

- Work only on the explicitly requested stage/task.
- Do not implement future stages.
- Do not redesign the architecture silently.
- Do not add technologies, services, folders, files, frameworks, or patterns merely because they seem useful.
- Do not force microservices.
- Do not introduce VMs, Kubernetes, or cloud infrastructure unless explicitly approved.
- Docker is the intended local containerization mechanism.
- Preserve all working existing code.
- Follow `PROJECT_STRUCTURE.md` exactly.
- Frontend talks to FastAPI; it does not directly access Redis/PostgreSQL.
- Backend/coordinator orchestrates; it does not generate load.
- Workers generate load.
- Redis handles coordination/transient state.
- PostgreSQL handles durable application data.
- Target service is controlled and independently owned.
- Do not expose an unrestricted public load-testing service.
- Do not silently change API contracts.
- Do not silently change database responsibilities.
- Do not create duplicate implementations.
- Do not leave required supporting files implicit.

## 3. Required workflow

For every task:

### Phase A — Understand
Read all supplied reference files and inspect the existing code relevant to the task.

### Phase B — Plan
Before coding, state:
- current stage;
- exact objective;
- execution/data flow;
- files to create;
- files to modify;
- files that remain untouched;
- dependencies/configuration affected;
- why each affected file is needed;
- what is deliberately excluded because it belongs to another stage.

If the task conflicts with documentation, stop and explain the conflict.

### Phase C — Approval
Unless I explicitly say `IMPLEMENT NOW`, wait for my approval.

### Phase D — Implement
After approval:
- provide complete contents for every new file;
- provide complete revised contents for every modified file unless I request a diff;
- label every file with its exact repository path;
- include all required imports and supporting code;
- update dependency/config files when actually required;
- update Dockerfiles/Compose/configuration when actually required;
- include tests required by the stage;
- keep all paths/imports/service names consistent.

### Phase E — Verify
After code, provide:
- installation commands;
- environment variables;
- run commands;
- test commands;
- expected behavior;
- common failure points;
- exact files changed;
- structure audit;
- confirmation that no future-stage functionality was introduced.

### Phase F — Documentation
After a successful stage, identify required updates to:
- `TASKS.md`;
- `PROJECT_STRUCTURE.md`;
- `ARCHITECTURE.md`;
- `API_SPEC.md`;
- `DECISIONS.md`;
- `AI_CONTEXT.md`;
- `CHANGELOG.md`.

Only update documents whose contents genuinely changed.

## 4. Complete planned repository

```text
distributed-load-testing/
├── README.md
├── REQUIREMENTS.md
├── ARCHITECTURE.md
├── DECISIONS.md
├── API_SPEC.md
├── PROJECT_STRUCTURE.md
├── TASKS.md
├── AI_CONTEXT.md
├── PROMPT.md
├── CHANGELOG.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── database/
│   │   └── core/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── worker/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── target-service/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── metrics/
│   ├── prometheus/
│   └── grafana/
├── tests/
│   ├── integration/
│   ├── system/
│   └── load/
└── docker/
```

This is the planned final map. Do NOT create every file on day one. Create implementation files when their stage requires them.

## 5. Global code-completeness rule

When asked for implementation, consider the entire runnable surface, not only source code.

Potential affected artifacts include:
- Python;
- JSX/JavaScript;
- `requirements.txt`;
- `package.json`;
- Dockerfiles;
- `docker-compose.yml`;
- `.env.example`;
- YAML/JSON configuration;
- Prometheus configuration;
- Grafana dashboards/provisioning;
- database/migration files if approved;
- tests;
- documentation.

If a required supporting artifact is omitted, the implementation is incomplete.

However, never create an artifact simply to fill the tree. Only create what the current stage actually requires.

## 6. Conflict/change-control protocol

If implementation requires a structural or architectural change:

1. Identify the conflict.
2. Explain why the current design is insufficient.
3. Propose the smallest reasonable change.
4. Identify every MD file affected.
5. Wait for approval.
6. Update documentation.
7. Only then implement.

Never silently solve an architecture problem by inventing a new service or technology.

# 7. Stage prompts

## Stage 1 — Basic HTTP Load Generator

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `PROJECT_STRUCTURE.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 1: Basic HTTP Load Generator.

Build only a standalone Python load generator capable of:
- target URL input;
- request count;
- concurrency;
- HTTP execution;
- latency measurement;
- success/failure counting;
- basic aggregate statistics;
- meaningful terminal output.

Do not implement FastAPI coordination, Redis, PostgreSQL, Docker worker orchestration, React, Prometheus, Grafana, autoscaling, or distributed job management.

First give the design and exact files. Wait for approval unless IMPLEMENT NOW is stated.
```

## Stage 2 — Controlled Target Service

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `PROJECT_STRUCTURE.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 2: Controlled Target Service.

Create the independent local FastAPI service used for authorized testing. Implement only approved controlled endpoints such as /fast, /slow, and /error, plus any endpoint explicitly required by the current requirements.

Do not implement Redis, PostgreSQL, distributed workers, React, Prometheus, Grafana, autoscaling, or cloud deployment unless explicitly required for this stage's verification.

Explain endpoint behavior, files, dependencies, and interaction with Stage 1 before coding.
```

## Stage 3 — FastAPI Backend / Coordinator

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `API_SPEC.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 3: FastAPI Backend / Coordinator.

Implement the approved API and validation foundation from API_SPEC.md. The backend must coordinate tests but must not generate load.

Implement only the endpoints and test-management behavior required by this stage. Do not prematurely implement Redis worker distribution, frontend, Prometheus, Grafana, autoscaling, Kubernetes, or cloud deployment.

Do not alter API_SPEC.md silently. Explain API flow, schemas, services, affected files, and exclusions before coding.
```

## Stage 4 — Job Management / Lifecycle

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `API_SPEC.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 4: Job Management and Test Lifecycle.

Implement the documented lifecycle:
CREATED -> RUNNING -> COMPLETED
RUNNING -> STOPPED
RUNNING -> FAILED

Reject invalid transitions cleanly. Keep HTTP, business logic, schemas, models, and orchestration responsibilities separated.

Do not implement distributed workers or future infrastructure unless explicitly required by the approved Stage 4 design.
```

## Stage 5 — Containerized Worker

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 5: Containerized Worker.

Create the independent worker capable of executing an assigned unit of load-generation work and producing results.

Worker = load generation.
Backend = orchestration.

Create Docker artifacts only as required by this stage. Do not implement the complete multi-worker Redis architecture, frontend, PostgreSQL, Prometheus, Grafana, autoscaling, or recovery system early.

Explain worker lifecycle and exact files before coding.
```

## Stage 6 — Multiple Workers

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 6: Multiple Workers.

Extend the system so independent worker instances can execute portions of a load test. Implement worker identity, work partitioning, result collection, and aggregation using only the approved architecture.

Demonstrate one-worker versus multi-worker behavior.

Do not add Kubernetes, cloud infrastructure, or autoscaling. If a coordination mechanism is needed beyond the current design, explain the alternatives and wait for approval.
```

## Stage 7 — Redis Coordination

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `API_SPEC.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 7: Redis Coordination.

Introduce Redis for task distribution, transient coordination, worker communication, result reporting, and approved heartbeat information.

Before coding, specify:
- task structure;
- queue/data structure;
- acknowledgement;
- result format;
- heartbeat;
- incomplete-task behavior;
- duplicate handling.

Do not use Redis as durable application storage and do not introduce another broker. Explain the communication design first.
```

## Stage 8 — PostgreSQL Persistence

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `API_SPEC.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 8: PostgreSQL Persistence.

Introduce durable application storage for approved test configurations, lifecycle state, history, and results.

Redis remains responsible for transient coordination. PostgreSQL remains responsible for persistence.

Design entities, relationships, repository/service boundaries, initialization/migration approach, and affected files before coding. Do not move responsibilities between Redis and PostgreSQL without approval.
```

## Stage 9 — Metrics / Prometheus

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 9: Metrics and Prometheus.

Design metric ownership, names, labels, collection, and aggregation before coding. Expose only meaningful approved metrics such as request counts, failures, latency, worker activity, heartbeat, and test duration.

Configure Prometheus to collect them.

Do not implement autoscaling or unrelated tracing. Grafana dashboards belong to Stage 10 unless explicitly approved.
```

## Stage 10 — React Dashboard / Grafana

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `API_SPEC.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 10: React Dashboard and Grafana.

React must communicate with FastAPI only. It must not access Redis/PostgreSQL directly.

Implement approved test creation, status, results, worker information, and metrics views. Configure Grafana from existing Prometheus metrics.

Keep the API contract unchanged. Explain pages, components, API flow, state/update mechanism, dashboards, and exact files before coding.
```

## Stage 11 — Horizontal Scaling

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 11: Horizontal Worker Scaling.

Use the existing worker and coordination architecture to run one or more workers and distribute work across them.

Demonstrate measurable one-worker versus multi-worker behavior.

Do not introduce Kubernetes, cloud infrastructure, or autoscaling. Explain the scaling model and Docker/local representation before coding.
```

## Stage 12 — Autoscaling

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 12: Autoscaling.

Design a measurable policy before coding. Define scaling signal, scale-up/down thresholds, cooldown, minimum/maximum workers, decision interval, spike behavior, and worker lifecycle.

Use existing system signals. Do not introduce Kubernetes/cloud autoscaling unless explicitly approved.
```

## Stage 13 — Failure Handling

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 13: Failure Handling.

Define worker failure, heartbeat timeout, incomplete work, reassignment, duplicate handling, test-state behavior, frontend reporting, and metrics.

Implement the smallest recovery mechanism consistent with the existing architecture. Do not silently add reliability infrastructure.
```

## Stage 14 — Networking / Security

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `API_SPEC.md`
- `PROJECT_STRUCTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 14: Networking and Security.

Improve safe target validation, Docker network boundaries, API input validation, conservative resource limits, service exposure, and environment handling.

Prevent accidental unrestricted public load generation.

Do not add enterprise authentication unless approved. Explain the threat model and controls before coding.
```

## Stage 15 — Evaluation

Reference files:
- `AI_CONTEXT.md`
- `TASKS.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `PROMPT.md`

Prompt:

```text
Implement Stage 15: Evaluation.

Create a reproducible evaluation plan covering single/multiple workers, concurrency, request count/duration, throughput, latency, P50/P95/P99, errors, resource usage, scaling, and worker failure.

Clearly define controlled variables, independent variables, dependent variables, repetitions, metrics, and recording method.

Do not redesign the system.
```

# 8. Final audit prompt

```text
Read all project MD files and inspect the complete repository.

Perform a complete architecture and implementation audit.

Verify:
- every required component exists;
- actual files match PROJECT_STRUCTURE.md;
- no undocumented major components exist;
- frontend uses FastAPI;
- backend coordinates but does not generate load;
- workers generate load;
- Redis and PostgreSQL responsibilities remain separate;
- target service is independent;
- Prometheus/Grafana are correctly connected;
- Dockerfiles and docker-compose.yml are consistent;
- API implementation matches API_SPEC.md;
- lifecycle is correct;
- scaling works;
- failure handling works;
- dependencies/configuration are complete;
- tests cover important behavior;
- no unnecessary microservices were introduced;
- no VM/cloud dependency was introduced;
- safety controls prevent unrestricted public load generation;
- documentation reflects reality.

Do not change anything yet. Report PASS, FAIL, inconsistencies, missing files, undocumented files, architecture violations, and recommended fixes.
```

# 9. AI output contract

For every implementation request, the final code response must use this structure:

```text
STAGE
OBJECTIVE
DESIGN
FILES TO CREATE
FILES TO MODIFY
DEPENDENCIES
ENVIRONMENT
EXECUTION FLOW
EXCLUDED/FUTURE WORK

--- FILE: exact/path/to/file ---
complete contents

--- FILE: exact/path/to/another/file ---
complete contents

RUN COMMANDS
TEST COMMANDS
EXPECTED RESULT
DOCUMENTATION UPDATES
STRUCTURE AUDIT
```

Never answer with code that depends on an unstated file.

# 10. Human control

The AI is the implementation assistant, not the project architect.

The workflow is:

```text
Documentation
    ↓
Current Stage
    ↓
AI Design Explanation
    ↓
User Approval
    ↓
AI Implementation
    ↓
Testing
    ↓
Documentation Update
    ↓
Next Stage
```

The project should remain understandable by a human even if a different AI model is used later.

# 11. Completion principle

A stage is complete only when:
- implementation exists;
- required supporting artifacts exist;
- tests/checks pass;
- the implementation follows the documented architecture;
- no unauthorized future functionality was added;
- documentation accurately reflects the result.

Do not optimize for "more code". Optimize for a coherent, working, explainable system.
