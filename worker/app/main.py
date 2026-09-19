import asyncio
import json
import os
import statistics
import time
import uuid
from redis.asyncio import Redis
from prometheus_client import start_http_server

from .executor import run_load_test
from .metrics import worker_jobs_processed_total, worker_active_jobs


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
METRICS_PORT = int(os.getenv("WORKER_METRICS_PORT", "8002"))
HEARTBEAT_INTERVAL = 5          # seconds between heartbeats
HEARTBEAT_TTL = 15              # Redis key TTL for the worker


def format_results(results, url, total_requests, concurrency, elapsed):
    total = len(results)
    successes = sum(1 for ok, _, _ in results if ok)
    failures = total - successes
    latencies = [lat for _, lat, _ in results if lat is not None]

    if not latencies:
        return {
            "url": url, "total_requests": total, "concurrency": concurrency,
            "successful": successes, "failed": failures,
            "error_rate": failures / total if total > 0 else 0.0,
            "elapsed_seconds": elapsed,
            "requests_per_second": total / elapsed if elapsed > 0 else 0.0,
            "min_latency_ms": 0.0, "max_latency_ms": 0.0, "avg_latency_ms": 0.0,
            "p50_latency_ms": 0.0, "p95_latency_ms": 0.0, "p99_latency_ms": 0.0,
        }

    latencies_sorted = sorted(latencies)

    def percentile(p):
        idx = int(len(latencies_sorted) * p / 100)
        return latencies_sorted[min(idx, len(latencies_sorted) - 1)]

    return {
        "url": url, "total_requests": total, "concurrency": concurrency,
        "successful": successes, "failed": failures,
        "error_rate": failures / total if total > 0 else 0.0,
        "elapsed_seconds": elapsed,
        "requests_per_second": total / elapsed if elapsed > 0 else 0.0,
        "min_latency_ms": min(latencies) * 1000,
        "max_latency_ms": max(latencies) * 1000,
        "avg_latency_ms": statistics.mean(latencies) * 1000,
        "p50_latency_ms": percentile(50) * 1000,
        "p95_latency_ms": percentile(95) * 1000,
        "p99_latency_ms": percentile(99) * 1000,
    }


async def heartbeat_loop(redis: Redis, worker_id: str):
    """Publish a heartbeat every HEARTBEAT_INTERVAL seconds."""
    key = f"worker:{worker_id}"
    while True:
        try:
            await redis.setex(key, HEARTBEAT_TTL, "alive")
        except Exception as e:
            print(f"[Worker {worker_id}] Heartbeat error: {e}")
        await asyncio.sleep(HEARTBEAT_INTERVAL)


async def consume_jobs(redis: Redis, worker_id: str):
    """Main worker loop: pull jobs, mark inflight, execute, push results."""
    while True:
        try:
            result = await redis.brpop("jobs", timeout=1)
            if result is None:
                continue

            _, job_data_str = result
            job_data = json.loads(job_data_str)
            test_id = job_data["test_id"]
            chunk_index = job_data.get("chunk_index", 0)
            chunk_id = f"{test_id}:{chunk_index}"
            url = job_data["target_url"]
            total_requests = job_data["total_requests"]
            concurrency = job_data["concurrency"]

            print(f"[Worker {worker_id}] Received chunk {chunk_id}: {url} "
                  f"({total_requests} reqs, conc {concurrency})")

            # Mark inflight (store chunk_id -> worker_id:timestamp)
            await redis.hset("inflight", chunk_id, f"{worker_id}:{time.time()}")
            # Store the original payload so the reaper can requeue if needed
            await redis.set(f"chunk:{chunk_id}", job_data_str, ex=3600)

            worker_active_jobs.inc()
            try:
                start_time = time.perf_counter()
                results = await run_load_test(url, total_requests, concurrency)
                elapsed = time.perf_counter() - start_time

                summary = format_results(results, url, total_requests, concurrency, elapsed)
                summary["test_id"] = test_id
                summary["worker_id"] = worker_id
                summary["chunk_index"] = chunk_index

                await redis.lpush("results", json.dumps(summary))
                worker_jobs_processed_total.inc()
                print(f"[Worker {worker_id}] Completed chunk {chunk_id} in {elapsed:.2f}s")
            finally:
                worker_active_jobs.dec()
                # Always remove from inflight, even on error
                await redis.hdel("inflight", chunk_id)
                await redis.delete(f"chunk:{chunk_id}")

        except Exception as e:
            print(f"[Worker {worker_id}] Error: {e}")
            await asyncio.sleep(1)


async def main():
    start_http_server(METRICS_PORT)
    print(f"[Worker] Metrics server listening on port {METRICS_PORT}")

    redis = Redis.from_url(REDIS_URL, decode_responses=True)
    worker_id = f"worker_{uuid.uuid4().hex[:8]}"
    print(f"[Worker {worker_id}] Started. Waiting for jobs...")

    # Run heartbeat and job consumer concurrently
    await asyncio.gather(
        heartbeat_loop(redis, worker_id),
        consume_jobs(redis, worker_id),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker shutting down...")