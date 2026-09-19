from prometheus_client import Counter, Gauge, Histogram

worker_requests_total = Counter(
    'loadtest_worker_requests_total',
    'Total HTTP requests sent by this worker'
)

worker_requests_failed_total = Counter(
    'loadtest_worker_requests_failed_total',
    'Total failed HTTP requests from this worker'
)

worker_request_latency_seconds = Histogram(
    'loadtest_worker_request_latency_seconds',
    'Request latency observed by this worker',
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10]
)

worker_jobs_processed_total = Counter(
    'loadtest_worker_jobs_processed_total',
    'Total load test jobs processed by this worker'
)

worker_active_jobs = Gauge(
    'loadtest_worker_active_jobs',
    'Jobs currently being executed by this worker'
)