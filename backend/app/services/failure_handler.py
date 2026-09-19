"""
Failure handling for the Distributed Load Testing Platform.

Two background tasks:
  1. Heartbeat monitor: scans Redis for `worker:*` keys every 10s.
     Updates the `loadtest_active_workers` gauge.

  2. Orphan reaper: scans the `inflight` hash every 30s.
     Any chunk older than STALE_THRESHOLD seconds is republished to `jobs`.

Both tasks use their own Redis connections.
"""

import asyncio
import json
import time

from app.core.redis_client import get_redis_client
from app.core.metrics import (
    active_workers,
    inflight_jobs,
    orphaned_jobs_reaped_total,
)


HEARTBEAT_INTERVAL = 10        # seconds between heartbeat scans
REAPER_INTERVAL = 30           # seconds between reaper scans
STALE_THRESHOLD_SECONDS = 90   # chunk older than this is considered orphaned


async def heartbeat_monitor():
    """Scan Redis for worker heartbeat keys and publish the count."""
    redis = get_redis_client()
    print("[FailureHandler] Heartbeat monitor started")
    while True:
        try:
            keys = await redis.keys("worker:*")
            count = len(keys)
            active_workers.set(count)
        except Exception as e:
            print(f"[FailureHandler] Heartbeat scan error: {e}")
        await asyncio.sleep(HEARTBEAT_INTERVAL)


async def orphan_reaper():
    """Scan `inflight` hash and re-publish stale chunks."""
    redis = get_redis_client()
    print("[FailureHandler] Orphan reaper started")
    while True:
        try:
            inflight = await redis.hgetall("inflight")
            inflight_jobs.set(len(inflight))

            now = time.time()
            for chunk_id, val in inflight.items():
                try:
                    worker_id, ts_str = val.split(":", 1)
                    age = now - float(ts_str)
                except (ValueError, AttributeError):
                    age = 0

                if age > STALE_THRESHOLD_SECONDS:
                    # Retrieve the original chunk payload
                    payload = await redis.get(f"chunk:{chunk_id}")
                    if payload:
                        # Re-publish to jobs
                        await redis.lpush("jobs", payload)
                        orphaned_jobs_reaped_total.inc()
                        print(f"[FailureHandler] Reaped chunk {chunk_id} "
                              f"(age={age:.0f}s, was {worker_id})")
                    # Remove from inflight regardless (either requeued or gone)
                    await redis.hdel("inflight", chunk_id)
                    # Remove the stored payload if it exists
                    await redis.delete(f"chunk:{chunk_id}")
        except Exception as e:
            print(f"[FailureHandler] Reaper error: {e}")
        await asyncio.sleep(REAPER_INTERVAL)