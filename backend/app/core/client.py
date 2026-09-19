import time
import httpx

async def send_request(
    client: httpx.AsyncClient,
    url: str,
) -> tuple[bool, float, int | None]:
    """
    Send one HTTP request.

    Returns:
        success: Whether the request was successful.
        latency: Request duration in seconds.
        status_code: HTTP status code, or None if the request failed.
    """
    start = time.perf_counter()
    try:
        response = await client.get(url)
        latency = time.perf_counter() - start
        success = 200 <= response.status_code < 400
        return success, latency, response.status_code
    except httpx.HTTPError:
        latency = time.perf_counter() - start
        return False, latency, None