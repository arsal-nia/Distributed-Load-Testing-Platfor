from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
import uuid
from datetime import datetime
from app.core.database import Base


class TestModel(Base):
    __tablename__ = "tests"

    id = Column(String, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    total_requests = Column(Integer, nullable=False)
    concurrency = Column(Integer, nullable=False)
    workers = Column(Integer, nullable=False)

    # Work partitioning tracking
    expected_chunks = Column(Integer, default=1)
    received_chunks = Column(Integer, default=0)

    status = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Raw worker results (list of dicts)
    worker_results = Column(JSON, default=list)


class ResultModel(Base):
    __tablename__ = "results"

    id = Column(String, primary_key=True, default=lambda: f"res_{uuid.uuid4().hex[:8]}")
    test_id = Column(String, index=True, nullable=False)
    chunk_index = Column(Integer, default=0)
    worker_id = Column(String, nullable=True)

    total_requests = Column(Integer, nullable=False)
    successful_requests = Column(Integer, nullable=False)
    failed_requests = Column(Integer, nullable=False)
    requests_per_second = Column(Float, nullable=False)
    average_latency_ms = Column(Float, nullable=False)
    p50_latency_ms = Column(Float, nullable=False)
    p95_latency_ms = Column(Float, nullable=False)
    p99_latency_ms = Column(Float, nullable=False)
    error_rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)