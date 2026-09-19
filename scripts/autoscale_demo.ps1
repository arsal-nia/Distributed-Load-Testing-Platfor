# Generates a burst of tests to trigger autoscaling.
# Run with: .\scripts\autoscale_demo.ps1

$ApiUrl = "http://localhost:8001/api/tests"

Write-Host "Submitting a burst of 10 tests to trigger autoscaling..." -ForegroundColor Yellow

for ($i = 1; $i -le 10; $i++) {
    $body = @{
        target_url = "http://target-service:8000/slow/0.5"
        requests = 2000
        concurrency = 20
        workers = 8
    } | ConvertTo-Json

    try {
        $id = (Invoke-RestMethod -Uri $ApiUrl -Method POST -Body $body -ContentType "application/json").test_id
        Invoke-RestMethod -Uri "http://localhost:8001/api/tests/$id/start" -Method POST | Out-Null
        Write-Host "  [$i/10] Created + started test $id"
    } catch {
        Write-Host "  [$i/10] Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "Burst submitted. Watch the autoscaler window for scale-up events." -ForegroundColor Green
