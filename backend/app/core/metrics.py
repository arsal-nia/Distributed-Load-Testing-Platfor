from prometheus_client import Counter, Gauge

# --- Job lifecycle metrics ---
jobs_created_total = Counter(
    'loadtest_jobs_created_total',
    'Total load test jobs created'
)
jobs_started_total = Counter(
    'loadtest_jobs_started_total',
    'Total load test jobs started'
)
jobs_completed_total = Counter(
    'loadtest_jobs_completed_total',
    'Total load test jobs completed successfully'
)
jobs_failed_total = Counter(
    'loadtest_jobs_failed_total',
    'Total load test jobs that failed'
)
jobs_stopped_total = Counter(
    'loadtest_jobs_stopped_total',
    'Total load test jobs stopped by user'
)

# --- Active state gauge ---
active_jobs = Gauge(
    'loadtest_active_jobs',
    'Number of jobs currently in RUNNING state'
)

# --- Aggregated results from workers ---
aggregated_requests_total = Counter(
    'loadtest_aggregated_requests_total',
    'Total requests reported by workers across all tests'
)
aggregated_requests_failed_total = Counter(
    'loadtest_aggregated_requests_failed_total',
    'Total failed requests reported by workers across all tests'
)

# --- Autoscaling signal ---
queue_length = Gauge(
    'loadtest_queue_length',
    'Current number of jobs waiting in the Redis queue'
)

# --- Failure handling metrics (Stage 13) ---
active_workers = Gauge(
    'loadtest_active_workers',
    'Number of workers currently heartbeating'
)
inflight_jobs = Gauge(
    'loadtest_inflight_jobs',
    'Number of chunks currently being processed'
)
orphaned_jobs_reaped_total = Counter(
    'loadtest_orphaned_jobs_reaped_total',
    'Total chunks that were reassigned because a worker died'
)