param(
    [int]$Requests = 2000,
    [int[]]$WorkerCounts = @(1, 2, 4)
)

$ErrorActionPreference = "Stop"
$results = @()

foreach ($n in $WorkerCounts) {
    Write-Host "`n=== Scaling to $n worker(s) ===" -ForegroundColor Cyan
    docker-compose up -d --scale worker=$n | Out-Null
    Start-Sleep -Seconds 5  # let workers register

    # Create test
    $body = @{
        target_url = "http://target-service:8000/fast"
        requests = $Requests
        concurrency = 20
        workers = $n
    } | ConvertTo-Json

    $id = (Invoke-RestMethod -Uri http://localhost:8001/api/tests -Method POST -Body $body -ContentType "application/json").test_id
    Write-Host "Created test: $id"

    $start = Get-Date
    Invoke-RestMethod -Uri "http://localhost:8001/api/tests/$id/start" -Method POST | Out-Null

    # Poll until completed (max 60s)
    $deadline = (Get-Date).AddSeconds(60)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 500
        $status = Invoke-RestMethod -Uri "http://localhost:8001/api/tests/$id"
        if ($status.status -eq "COMPLETED" -or $status.status -eq "FAILED") { break }
    }
    $elapsed = (Get-Date) - $start

    $r = Invoke-RestMethod -Uri "http://localhost:8001/api/tests/$id/results"

    $results += [PSCustomObject]@{
        Workers    = $n
        Requests   = $r.total_requests
        Success    = $r.successful_requests
        Failed     = $r.failed_requests
        WallSec    = [math]::Round($elapsed.TotalSeconds, 2)
        ReqPerSec  = [math]::Round($r.requests_per_second, 1)
        AvgMs      = [math]::Round($r.average_latency_ms, 1)
        P95Ms      = [math]::Round($r.p95_latency_ms, 1)
    }
}

Write-Host "`n=== SCALING RESULTS ===" -ForegroundColor Green
$results | Format-Table -AutoSize | Out-String | Write-Host