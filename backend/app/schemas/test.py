from pydantic import BaseModel, HttpUrl, Field, validator
from enum import Enum
from typing import Optional, List

from app.core.security import validate_target_url


class TestStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class CreateTestRequest(BaseModel):
    target_url: HttpUrl
    requests: int = Field(gt=0, le=100_000)
    concurrency: int = Field(gt=0, le=500)
    duration_seconds: Optional[int] = Field(None, gt=0, le=3600)
    workers: int = Field(default=1, gt=0, le=10)

    @validator("workers")
    def validate_workers(cls, v, values):
        if "concurrency" in values and v > values["concurrency"]:
            raise ValueError("Workers cannot exceed concurrency")
        return v

    @validator("target_url")
    def validate_allowlist(cls, v):
        return validate_target_url(str(v))


class TestResponse(BaseModel):
    test_id: str
    status: TestStatus


class TestStatusResponse(BaseModel):
    test_id: str
    status: TestStatus
    workers: int
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class TestResultsResponse(BaseModel):
    test_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_per_second: float
    average_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_rate: float


class TestSummary(BaseModel):
    test_id: str
    status: TestStatus


class TestListResponse(BaseModel):
    tests: List[TestSummary]
