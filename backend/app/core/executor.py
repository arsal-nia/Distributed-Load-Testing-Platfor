import asyncio
import httpx
from app.core.client import send_request

async def run_load_test(
    url: str,
    total_requests: int,
    concurrency: int,
    stop_event: asyncio.Event = None,
) -> list[tuple[bool, float, int | None]]:
    """
    Execute a load test against the target URL.

    Args:
        url: Target URL.
        total_requests: Total number of requests to send.
        concurrency: Maximum number of simultaneous requests.
        stop_event: Optional event to signal cancellation.

    Returns:
        A list containing the result of every request.
    """
    semaphore = asyncio.Semaphore(concurrency)
    results = []
    # Process in chunks so we can check stop_event between chunks
    chunk_size = max(concurrency * 5, 100)

    async with httpx.AsyncClient() as client:
        for start_idx in range(0, total_requests, chunk_size):
            if stop_event and stop_event.is_set():
                break

            chunk_end = min(start_idx + chunk_size, total_requests)
            tasks = []
            for _ in range(start_idx, chunk_end):
                if stop_event and stop_event.is_set():
                    break
                tasks.append(asyncio.create_task(_execute_request(client, url, semaphore)))

            if tasks:
                chunk_results = await asyncio.gather(*tasks)
                results.extend(chunk_results)

    return results

async def _execute_request(client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        return await send_request(client, url)