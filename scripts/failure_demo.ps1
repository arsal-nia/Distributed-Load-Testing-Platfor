# Simulates a worker crash mid-job and shows the reaper reassigning work.
# Run with: .\scripts\failure_demo.ps1

$ApiUrl = "http://localhost:8001/api/tests"

Write-Host "Step 1: Scaling to 3 workers..." -ForegroundColor Yellow
docker-compose up -d --scale worker=3 | Out-Null
Start-Sleep -Seconds 5

Write-Host "Step 2: Submitting a LONG-running test (slow endpoint)..." -ForegroundColor Yellow
$body = @{
    target_url = "http://target-service:8000/slow/0.5"
    requests = 5000
    concurrency = 20
    workers = 3
} | ConvertTo-Json

$id = (Invoke-RestMethod -Uri $ApiUrl -Method POST -Body $body -ContentType "application/json").test_id
Invoke-RestMethod -Uri "http://localhost:8001/api/tests/$id/start" -Method POST | Out-Null
Write-Host "  Created test: $id" -ForegroundColor Cyan

Write-Host "Step 3: Waiting 3 seconds, then KILLING worker-2..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

$containerToKill = "distributedloadtestingplatform-worker-2"
docker kill $containerToKill | Out-Null
Write-Host "  Killed $containerToKill" -ForegroundColor Red

Write-Host "Step 4: Watching inflight + test status for 3 minutes..." -ForegroundColor Yellow
Write-Host "  (Reaper checks every 30s, threshold = 90s, so reassignment takes ~90-120s)" -ForegroundColor Gray

for ($i = 1; $i -le 36; $i++) {
    Start-Sleep -Seconds 5
    $inflight = Invoke-RestMethod -Uri "http://localhost:8001/api/inflight" -ErrorAction SilentlyContinue
    $status = Invoke-RestMethod -Uri "http://localhost:8001/api/tests/$id" -ErrorAction SilentlyContinue
    $w = Invoke-RestMethod -Uri "http://localhost:8001/api/workers" -ErrorAction SilentlyContinue

    Write-Host ("[{0}s] inflight={1} stale={2} | workers={3} | test={4}" -f ($i*5), $inflight.count, $inflight.stale_count, $w.count, $status.status)
}

Write-Host "Done. Get results with:" -ForegroundColor Green
Write-Host "  Invoke-RestMethod http://localhost:8001/api/tests/$id/results"