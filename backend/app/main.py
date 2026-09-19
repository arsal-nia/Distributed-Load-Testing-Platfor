import asyncio
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.api.routes import router
from app.core.redis_client import get_redis_client, close_redis_client
from app.core.database import engine, Base
from app.core.metrics import queue_length
from app.services.failure_handler import heartbeat_monitor, orphan_reaper


app = FastAPI(
    title="Distributed Load Testing Platform - Backend",
    description="Coordinates load-test jobs. Does not generate load itself.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}


@app.get("/metrics")
async def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def _publish_queue_metrics():
    """Background task: publish Redis queue length as a Prometheus gauge every 2s."""
    redis = get_redis_client()
    while True:
        try:
            length = await redis.llen("jobs")
            queue_length.set(length)
        except Exception as e:
            print(f"[Metrics] Queue publish error: {e}")
        await asyncio.sleep(2)


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Background tasks
    asyncio.create_task(_publish_queue_metrics())
    asyncio.create_task(heartbeat_monitor())
    asyncio.create_task(orphan_reaper())


@app.on_event("shutdown")
async def shutdown_event():
    await close_redis_client()
    await engine.dispose()