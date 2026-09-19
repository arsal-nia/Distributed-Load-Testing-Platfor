import asyncio
import random
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Controlled Test Target",
    description="Safely testable HTTP service for load-testing experiments.",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Root endpoint – basic health and info."""
    return {
        "service": "Controlled Test Target",
        "status": "operational",
        "endpoints": ["/fast", "/slow/{delay}", "/error", "/health"],
    }


@app.get("/fast")
async def fast_endpoint():
    """
    Fast endpoint – responds immediately with a small payload.
    Use this to measure baseline latency and throughput.
    """
    return {"status": "ok", "message": "Fast response"}


@app.get("/slow/{delay}")
async def slow_endpoint(delay: float):
    """
    Slow endpoint – introduces a controlled delay (in seconds).
    Use this to test latency distribution and concurrency behavior.

    Args:
        delay: Delay in seconds (0.1 to 10.0 recommended).
    """
    if delay < 0:
        raise HTTPException(status_code=400, detail="Delay must be non-negative")
    
    if delay > 30:
        # Safety cap – prevents accidentally overloading the target service itself.
        raise HTTPException(
            status_code=400,
            detail="Delay too high (max 30 seconds)",
        )

    await asyncio.sleep(delay)
    return {"status": "ok", "message": f"Delayed response of {delay}s"}


@app.get("/error")
async def error_endpoint(
    status_code: int = Query(
        500,
        description="HTTP status code to return (e.g., 400, 404, 500)",
        ge=400,
        le=599,
    ),
    message: str = Query(
        "Simulated error",
        description="Optional error message to include in the response.",
    ),
):
    """
    Error endpoint – returns a configurable HTTP error status.
    Use this to test failure handling, retry logic, and error-rate metrics.

    Args:
        status_code: HTTP status code (400-599).
        message: Custom error message.
    """
    raise HTTPException(status_code=status_code, detail=message)


@app.get("/health")
async def health_check():
    """Readiness/liveness probe for orchestration."""
    return {"status": "healthy", "service": "target-service"}