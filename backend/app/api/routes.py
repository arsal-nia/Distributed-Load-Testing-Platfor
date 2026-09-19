import logging
import time
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import get_redis_client
from app.core.security import verify_token
from app.schemas.test import (
    CreateTestRequest,
    TestResponse,
    TestStatusResponse,
    TestResultsResponse,
    TestListResponse,
    TestSummary,
    TestStatus,
)
from app.schemas.worker import (
    WorkerInfo,
    WorkerListResponse,
    InflightJobInfo,
    InflightListResponse,
)
from app.services.test_service import TestService
from app.models.db_models import TestModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["tests"])


# ---------------- WRITE ENDPOINTS (auth-protected) ----------------

@router.post(
    "/tests",
    response_model=TestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_token)],
)
async def create_test(request: CreateTestRequest, db: AsyncSession = Depends(get_db)):
    service = TestService(db)
    try:
        db_test = await service.create_test(request)
        return TestResponse(test_id=db_test.id, status=TestStatus(db_test.status))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/tests/{test_id}/start",
    response_model=TestResponse,
    dependencies=[Depends(verify_token)],
)
async def start_test(test_id: str, db: AsyncSession = Depends(get_db)):
    service = TestService(db)
    try:
        db_test = await service.start_test(test_id)
        return TestResponse(test_id=db_test.id, status=TestStatus(db_test.status))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")


@router.post(
    "/tests/{test_id}/stop",
    response_model=TestResponse,
    dependencies=[Depends(verify_token)],
)
async def stop_test(test_id: str, db: AsyncSession = Depends(get_db)):
    service = TestService(db)
    try:
        db_test = await service.stop_test(test_id)
        return TestResponse(test_id=db_test.id, status=TestStatus(db_test.status))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")


# ---------------- READ ENDPOINTS (open) ----------------

@router.get("/tests/{test_id}", response_model=TestStatusResponse)
async def get_test_status(test_id: str, db: AsyncSession = Depends(get_db)):
    service = TestService(db)
    try:
        db_test = await service.get_test(test_id)
        return TestStatusResponse(
            test_id=db_test.id,
            status=TestStatus(db_test.status),
            workers=db_test.workers,
            started_at=db_test.started_at.isoformat() if db_test.started_at else None,
            completed_at=db_test.completed_at.isoformat() if db_test.completed_at else None,
            error=db_test.error,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")


@router.get("/tests/{test_id}/results", response_model=TestResultsResponse)
async def get_test_results(test_id: str, db: AsyncSession = Depends(get_db)):
    service = TestService(db)
    try:
        return await service.get_results(test_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/tests", response_model=TestListResponse)
async def list_tests(db: AsyncSession = Depends(get_db)):
    service = TestService(db)
    tests = await service.list_tests()
    return TestListResponse(
        tests=[TestSummary(test_id=t.id, status=TestStatus(t.status)) for t in tests]
    )


@router.get("/workers", response_model=WorkerListResponse)
async def list_workers():
    try:
        redis = get_redis_client()
        keys = await redis.keys("worker:*")
        workers = []
        for key in keys:
            worker_id = key.split("worker:", 1)[1]
            ttl = await redis.ttl(key)
            workers.append(WorkerInfo(worker_id=worker_id, ttl_seconds=max(0, ttl)))
        return WorkerListResponse(count=len(workers), workers=workers)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {e}")


@router.get("/inflight", response_model=InflightListResponse)
async def list_inflight():
    try:
        redis = get_redis_client()
        inflight = await redis.hgetall("inflight")
        now = time.time()
        jobs = []
        stale_count = 0
        for chunk_id, val in inflight.items():
            try:
                worker_id, ts_str = val.split(":", 1)
                age = now - float(ts_str)
            except (ValueError, AttributeError):
                worker_id = None
                age = 0.0
            is_stale = age > 90
            if is_stale:
                stale_count += 1
            jobs.append(InflightJobInfo(
                chunk_id=chunk_id,
                worker_id=worker_id,
                age_seconds=round(age, 1),
                stale=is_stale,
            ))
        return InflightListResponse(count=len(jobs), stale_count=stale_count, jobs=jobs)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {e}")
