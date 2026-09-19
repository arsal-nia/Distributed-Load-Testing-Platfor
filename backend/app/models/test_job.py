import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from app.schemas.test import CreateTestRequest, TestStatus

@dataclass
class TestJob:
    id: str
    config: CreateTestRequest
    status: TestStatus = TestStatus.CREATED
    results: Optional[List[tuple[bool, float, int | None]]] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    stop_event: Optional[asyncio.Event] = None
    task: Optional[asyncio.Task] = None
    error: Optional[str] = None

    def to_summary(self):
        return {
            "test_id": self.id,
            "status": self.status.value,
        }