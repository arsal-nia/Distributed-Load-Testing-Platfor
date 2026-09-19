from pydantic import BaseModel
from typing import List, Optional


class WorkerInfo(BaseModel):
    worker_id: str
    ttl_seconds: int  # remaining time until heartbeat expires


class WorkerListResponse(BaseModel):
    count: int
    workers: List[WorkerInfo]


class InflightJobInfo(BaseModel):
    chunk_id: str
    worker_id: Optional[str]
    age_seconds: float
    stale: bool  # True if older than the reassignment threshold


class InflightListResponse(BaseModel):
    count: int
    stale_count: int
    jobs: List[InflightJobInfo]