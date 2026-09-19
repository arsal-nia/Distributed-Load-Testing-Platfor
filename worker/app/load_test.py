import asyncio

import statistics

from executor import run_load_test


async def main():
    url = input("Target URL: ")
    total_requests = int(input("Number of requests: "))
    concurrency = int(input("Concurrency: "))

    print("\nStarting load test...\n")

    results = await run_load_test(
        url=url,
        total_requests=total_requests,
        concurrency=concurrency,
    )

    print_summary(results)

def print_summary(results: list[tuple[bool, float, int | None]]):
    total = len(results)
    successes = sum(1 for ok, _, _ in results if ok)
    failures = total - successes
    latencies = [lat for _, lat, _ in results]

    if not latencies:
        print("No requests completed.")
        return

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print("\n=== RESULTS ===")
    print(f"Total requests: {total}")
    print(f"Successful:     {successes}")
    print(f"Failed:         {failures}")
    print(f"Error rate:     {failures / total * 100:.2f}%")
    print("\n--- Latency (seconds) ---")
    print(f"Min:   {min(latencies):.4f}")
    print(f"Max:   {max(latencies):.4f}")
    print(f"Avg:   {statistics.mean(latencies):.4f}")
    print(f"P50:   {p50:.4f}")
    print(f"P95:   {p95:.4f}")
    print(f"P99:   {p99:.4f}")

if __name__ == "__main__":
    asyncio.run(main())