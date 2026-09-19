import time
import httpx
from .metrics import (
    worker_requests_total,
    worker_requests_failed_total,
    worker_request_latency_seconds,
)


async def send_request(
    client: httpx.AsyncClient,
    url: str,
) -> tuple[bool, float, int | None]:
    """
    Send one HTTP request and record metrics.
    """
    start = time.perf_counter()

    try:
        response = await client.get(url)
        latency = time.perf_counter() - start
        success = 200 <= response.status_code < 400

        worker_requests_total.inc()
        worker_request_latency_seconds.observe(latency)
        if not success:
            worker_requests_failed_total.inc()

        return success, latency, response.status_code

    except httpx.HTTPError:
        latency = time.perf_counter() - start
        worker_requests_total.inc()
        worker_requests_failed_total.inc()
        worker_request_latency_seconds.observe(latency)
        return False, latency, None