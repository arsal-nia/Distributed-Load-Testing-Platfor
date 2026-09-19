"""
Autoscaler for the Distributed Load Testing Platform.

Runs on the HOST machine (not in Docker). It polls Prometheus
for the Redis queue length, decides whether to scale up or down,
and invokes `docker-compose up -d --scale worker=N`.

Policy:
  - Scale UP   if queue_length > SCALE_UP_THRESHOLD for 2 consecutive checks
  - Scale DOWN if queue_length == 0 for 3 consecutive checks (and cooldown elapsed)
  - Cooldown 30s between scaling events
  - Min workers = 1, Max workers = 8
"""

import subprocess
import sys
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip install requests")
    sys.exit(1)


# -------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------
PROMETHEUS_URL = "http://localhost:9091"
PROJECT_DIR = r"C:\Users\pc\Desktop\Distributed Load Testing Platform"

CHECK_INTERVAL = 5           # seconds between checks
COOLDOWN = 30                # seconds between scale events
SCALE_UP_THRESHOLD = 50      # queue length to trigger scale-up
SCALE_DOWN_THRESHOLD = 0     # queue length to consider scale-down

SCALE_UP_CONSECUTIVE = 2     # must exceed threshold this many times in a row
SCALE_DOWN_CONSECUTIVE = 3   # must be empty this many times in a row

MIN_WORKERS = 1
MAX_WORKERS = 8
SCALE_STEP = 2


# -------------------------------------------------------------
# STATE
# -------------------------------------------------------------
current_workers = 1
last_scale_time = 0
up_streak = 0
down_streak = 0


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def get_queue_length() -> float:
    """Query Prometheus for current queue length. Returns 0 on failure."""
    try:
        url = f"{PROMETHEUS_URL}/api/v1/query"
        r = requests.get(url, params={"query": "loadtest_queue_length"}, timeout=3)
        r.raise_for_status()
        data = r.json()
        results = data.get("data", {}).get("result", [])
        if results:
            return float(results[0]["value"][1])
    except Exception as e:
        log(f"⚠️  Prometheus query failed: {e}")
    return 0.0


def scale_to(n: int):
    """Run docker-compose up -d --scale worker=N."""
    global current_workers, last_scale_time
    n = max(MIN_WORKERS, min(MAX_WORKERS, n))
    if n == current_workers:
        return
    log(f"🐳 Scaling workers: {current_workers} → {n}")
    try:
        result = subprocess.run(
            ["docker-compose", "up", "-d", "--scale", f"worker={n}"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            current_workers = n
            last_scale_time = time.time()
            log(f"✅ Now running {n} worker(s)")
        else:
            log(f"❌ Scale command failed: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        log("❌ Scale command timed out")
    except FileNotFoundError:
        log("❌ docker-compose not found in PATH")


def loop():
    global up_streak, down_streak, last_scale_time

    log(f"🚀 Autoscaler started. Policy: scale up when queue > {SCALE_UP_THRESHOLD}, "
        f"scale down when empty. Step={SCALE_STEP}, Cooldown={COOLDOWN}s")

    while True:
        try:
            qlen = get_queue_length()
            now = time.time()
            cooldown_left = max(0, COOLDOWN - (now - last_scale_time))

            log(f"Queue length = {qlen:.0f}  |  Workers = {current_workers}  |  Cooldown: {cooldown_left:.0f}s")

            # --- SCALE UP LOGIC ---
            if qlen > SCALE_UP_THRESHOLD:
                up_streak += 1
                down_streak = 0
                if up_streak >= SCALE_UP_CONSECUTIVE and cooldown_left == 0:
                    if current_workers < MAX_WORKERS:
                        scale_to(current_workers + SCALE_STEP)
                    else:
                        log("⚠️  At MAX_WORKERS, cannot scale up")
                    up_streak = 0
            else:
                up_streak = 0

            # --- SCALE DOWN LOGIC ---
            if qlen <= SCALE_DOWN_THRESHOLD:
                down_streak += 1
                if down_streak >= SCALE_DOWN_CONSECUTIVE and cooldown_left == 0:
                    if current_workers > MIN_WORKERS:
                        scale_to(current_workers - SCALE_STEP)
                    down_streak = 0
            else:
                down_streak = 0

        except KeyboardInterrupt:
            log("👋 Autoscaler stopped by user")
            break
        except Exception as e:
            log(f"❌ Unexpected error: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        loop()
    except KeyboardInterrupt:
        print("\nAutoscaler terminated.")