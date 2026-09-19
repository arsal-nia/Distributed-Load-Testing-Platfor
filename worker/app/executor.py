import asyncio

import httpx

from .client import send_request


async def run_load_test(
    url: str,
    total_requests: int,
    concurrency: int,
) -> list[tuple[bool, float, int | None]]:
    """
    Execute a load test against the target URL.

    Args:
        url: Target URL.
        total_requests: Total number of requests to send.
        concurrency: Maximum number of simultaneous requests.

    Returns:
        A list containing the result of every request.
    """

    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient() as client:

        async def execute_request():
            async with semaphore:
                return await send_request(client, url)

        tasks = [
            asyncio.create_task(execute_request())
            for _ in range(total_requests)
        ]

        results = await asyncio.gather(*tasks)

    return results