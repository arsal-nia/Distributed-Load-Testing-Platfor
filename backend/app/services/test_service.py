import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.db_models import TestModel, ResultModel
from app.schemas.test import CreateTestRequest, TestStatus, TestResultsResponse
from app.core.redis_client import get_redis_client
from app.core.metrics import (
    jobs_created_total,
    jobs_started_total,
    jobs_completed_total,
    jobs_failed_total,
    jobs_stopped_total,
    active_jobs,
    aggregated_requests_total,
    aggregated_requests_failed_total,
)


class TestService:
    def __init__(self, db: AsyncSession):
        self.db = db

    ALLOWED_TRANSITIONS = {
        TestStatus.CREATED:   [TestStatus.RUNNING],
        TestStatus.RUNNING:   [TestStatus.COMPLETED, TestStatus.STOPPED, TestStatus.FAILED],
        TestStatus.COMPLETED: [],
        TestStatus.STOPPED:   [],
        TestStatus.FAILED:    [],
    }

    def _validate_transition(self, current_status: TestStatus, new_status: TestStatus):
        allowed = self.ALLOWED_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Invalid state transition: {current_status.value} -> {new_status.value}. "
                f"Allowed transitions: {[s.value for s in allowed] if allowed else 'None'}"
            )

    # ------------------------------------------------------------
    # REQUEST-SCOPED METHODS
    # ------------------------------------------------------------

    async def create_test(self, request: CreateTestRequest) -> TestModel:
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        db_test = TestModel(
            id=test_id,
            target_url=str(request.target_url),
            total_requests=request.requests,
            concurrency=request.concurrency,
            workers=request.workers,
            status=TestStatus.CREATED.value,
            worker_results=[],
            expected_chunks=1,
            received_chunks=0,
        )
        self.db.add(db_test)
        await self.db.commit()
        await self.db.refresh(db_test)
        jobs_created_total.inc()
        return db_test

    async def start_test(self, test_id: str) -> TestModel:
        result = await self.db.execute(select(TestModel).where(TestModel.id == test_id))
        db_test = result.scalar_one_or_none()
        if not db_test:
            raise KeyError(f"Test {test_id} not found")

        current_status = TestStatus(db_test.status)
        self._validate_transition(current_status, TestStatus.RUNNING)

        # Compute chunks
        num_chunks = min(db_test.workers, db_test.total_requests)
        chunk_size = db_test.total_requests // num_chunks
        remainder = db_test.total_requests % num_chunks

        chunks = []
        for i in range(num_chunks):
            size = chunk_size + (1 if i < remainder else 0)
            chunks.append({
                "chunk_index": i,
                "total_requests": size,
                "target_url": db_test.target_url,
                "concurrency": db_test.concurrency,
                "test_id": db_test.id,
            })

        # Update DB with chunk info
        db_test.status = TestStatus.RUNNING.value
        db_test.started_at = datetime.utcnow()
        db_test.expected_chunks = num_chunks
        db_test.received_chunks = 0
        db_test.worker_results = []
        await self.db.commit()
        await self.db.refresh(db_test)

        jobs_started_total.inc()
        active_jobs.inc()

        # Publish all chunks in background
        asyncio.create_task(_publish_chunks(chunks))

        return db_test

    async def stop_test(self, test_id: str) -> TestModel:
        result = await self.db.execute(select(TestModel).where(TestModel.id == test_id))
        db_test = result.scalar_one_or_none()
        if not db_test:
            raise KeyError(f"Test {test_id} not found")

        current_status = TestStatus(db_test.status)
        self._validate_transition(current_status, TestStatus.STOPPED)

        db_test.status = TestStatus.STOPPED.value
        db_test.completed_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(db_test)

        jobs_stopped_total.inc()
        active_jobs.dec()
        return db_test

    async def get_test(self, test_id: str) -> TestModel:
        result = await self.db.execute(select(TestModel).where(TestModel.id == test_id))
        db_test = result.scalar_one_or_none()
        if not db_test:
            raise KeyError(f"Test {test_id} not found")
        return db_test

    async def get_results(self, test_id: str) -> TestResultsResponse:
        # Aggregate result is stored with worker_id = 'aggregated'
        result = await self.db.execute(
            select(ResultModel)
            .where(ResultModel.test_id == test_id)
            .where(ResultModel.worker_id == "aggregated")
            .order_by(ResultModel.created_at.desc())
        )
        db_result = result.scalar_one_or_none()
        if not db_result:
            test_result = await self.db.execute(select(TestModel).where(TestModel.id == test_id))
            db_test = test_result.scalar_one_or_none()
            if not db_test:
                raise KeyError(f"Test {test_id} not found")
            if db_test.status in (TestStatus.RUNNING.value, TestStatus.CREATED.value):
                raise ValueError(f"Cannot get results for test in state {db_test.status}")
            return TestResultsResponse(
                test_id=test_id,
                total_requests=0, successful_requests=0, failed_requests=0,
                requests_per_second=0.0, average_latency_ms=0.0,
                p50_latency_ms=0.0, p95_latency_ms=0.0, p99_latency_ms=0.0,
                error_rate=0.0,
            )

        return TestResultsResponse(
            test_id=test_id,
            total_requests=db_result.total_requests,
            successful_requests=db_result.successful_requests,
            failed_requests=db_result.failed_requests,
            requests_per_second=db_result.requests_per_second,
            average_latency_ms=db_result.average_latency_ms,
            p50_latency_ms=db_result.p50_latency_ms,
            p95_latency_ms=db_result.p95_latency_ms,
            p99_latency_ms=db_result.p99_latency_ms,
            error_rate=db_result.error_rate,
        )

    async def list_tests(self) -> List[TestModel]:
        result = await self.db.execute(select(TestModel).order_by(TestModel.created_at.desc()))
        return result.scalars().all()


# ============================================================
# BACKGROUND TASKS (module-level)
# ============================================================

_results_listener_started = False
_results_listener_lock = asyncio.Lock()


async def _publish_chunks(chunks: list):
    """Publish all chunks to Redis, then ensure listener is running."""
    global _results_listener_started

    try:
        redis = get_redis_client()
        for chunk in chunks:
            await redis.lpush("jobs", json.dumps(chunk))
        print(f"[Background] Published {len(chunks)} chunks for test {chunks[0]['test_id']}")

        async with _results_listener_lock:
            if not _results_listener_started:
                _results_listener_started = True
                asyncio.create_task(_listen_for_results())
                print("[Background] Started results listener")
    except Exception as e:
        print(f"[Background] Error publishing chunks: {e}")


async def _listen_for_results():
    redis = get_redis_client()
    print("[Background] Results listener active")
    while True:
        try:
            result = await redis.brpop("results", timeout=1)
            if result is None:
                continue
            _, data = result
            result_data = json.loads(data)
            test_id = result_data.get("test_id")
            if test_id:
                await _process_result(test_id, result_data)
        except Exception as e:
            print(f"[Background] Error in listener: {e}")
            await asyncio.sleep(1)


async def _process_result(test_id: str, result_data: Dict[str, Any]):
    """Process a single worker result. Aggregate when all chunks received."""
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(TestModel).where(TestModel.id == test_id))
            db_test = result.scalar_one_or_none()
            if not db_test:
                print(f"[Background] Test {test_id} not found")
                return

            # Append raw result
            existing = db_test.worker_results or []
            db_test.worker_results = existing + [result_data]
            db_test.received_chunks = (db_test.received_chunks or 0) + 1

            jobs_completed_total.inc()
            aggregated_requests_total.inc(result_data.get("total_requests", 0))
            aggregated_requests_failed_total.inc(result_data.get("failed", 0))

            # Check if all chunks received
            all_received = db_test.received_chunks >= (db_test.expected_chunks or 1)

            if all_received and db_test.status == TestStatus.RUNNING.value:
                all_results = db_test.worker_results

                total = sum(r.get("total_requests", 0) for r in all_results)
                successful = sum(r.get("successful", 0) for r in all_results)
                failed = sum(r.get("failed", 0) for r in all_results)

                # Workers run in parallel -> use MAX elapsed time
                max_elapsed = max((r.get("elapsed_seconds", 0) for r in all_results), default=0)

                # Weighted averages by request count
                weight = total if total > 0 else 1
                avg_latency = sum(r.get("avg_latency_ms", 0) * r.get("total_requests", 0) for r in all_results) / weight
                p50 = sum(r.get("p50_latency_ms", 0) * r.get("total_requests", 0) for r in all_results) / weight
                p95 = sum(r.get("p95_latency_ms", 0) * r.get("total_requests", 0) for r in all_results) / weight
                p99 = sum(r.get("p99_latency_ms", 0) * r.get("total_requests", 0) for r in all_results) / weight

                rps = total / max_elapsed if max_elapsed > 0 else 0.0

                db_test.status = TestStatus.COMPLETED.value
                db_test.completed_at = datetime.utcnow()

                aggregated = ResultModel(
                    test_id=test_id,
                    chunk_index=0,
                    worker_id="aggregated",
                    total_requests=total,
                    successful_requests=successful,
                    failed_requests=failed,
                    requests_per_second=rps,
                    average_latency_ms=avg_latency,
                    p50_latency_ms=p50,
                    p95_latency_ms=p95,
                    p99_latency_ms=p99,
                    error_rate=failed / total if total > 0 else 0.0,
                )
                session.add(aggregated)

                active_jobs.dec()
                print(f"[Background] Test {test_id} COMPLETE: {total} reqs in {max_elapsed:.2f}s ({rps:.1f} req/s)")

            await session.commit()

    except Exception as e:
        print(f"[Background] Error processing result for {test_id}: {e}")