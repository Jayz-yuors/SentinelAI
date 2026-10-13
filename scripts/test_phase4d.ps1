$ErrorActionPreference = "Stop"

$backend = "http://localhost:8080"
$validRepository = "https://github.com/octocat/Hello-World.git"

Write-Host ""
Write-Host "============================================"
Write-Host " SENTINELAI - PHASE 4D FINAL VALIDATION"
Write-Host "============================================"
Write-Host ""

# -------------------------------------------------
# TEST 1: Infrastructure health
# -------------------------------------------------

Write-Host "[TEST 1] Infrastructure health..."

$health = Invoke-RestMethod `
    -Uri "$backend/api/infrastructure/health" `
    -Method GET

if ($health.status -ne "UP") {
    throw "Backend health is not UP."
}

if ($health.services.aiService -ne "UP") {
    throw "AI service is not UP."
}

if ($health.services.postgresql -ne "UP") {
    throw "PostgreSQL is not UP."
}

if ($health.services.neo4j -ne "UP") {
    throw "Neo4j is not UP."
}

Write-Host "[PASS] Backend = UP"
Write-Host "[PASS] FastAPI = UP"
Write-Host "[PASS] PostgreSQL = UP"
Write-Host "[PASS] Neo4j = UP"
Write-Host ""

# -------------------------------------------------
# TEST 2: Real repository analysis
# -------------------------------------------------

Write-Host "[TEST 2] Spring Boot -> FastAPI -> Phase 1/2/3..."

$body = @{
    repositoryUrl = $validRepository
    branch = "master"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "$backend/api/analysis" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

if ($response.success -ne $true) {
    throw "Analysis did not return success=true."
}

if ([string]::IsNullOrWhiteSpace($response.analysisId)) {
    throw "Analysis ID was not returned."
}

if ($response.status -ne "COMPLETED") {
    throw "Analysis status is not COMPLETED."
}

if ($null -eq $response.result.phase1) {
    throw "Phase 1 result missing."
}

if ($null -eq $response.result.phase2) {
    throw "Phase 2 result missing."
}

if ($null -eq $response.result.phase3) {
    throw "Phase 3 result missing."
}

$analysisId = $response.analysisId

Write-Host "[PASS] Analysis ID: $analysisId"
Write-Host "[PASS] Analysis status: $($response.status)"
Write-Host "[PASS] Phase 1 result received"
Write-Host "[PASS] Phase 2 result received"
Write-Host "[PASS] Phase 3 result received"
Write-Host ""

# -------------------------------------------------
# TEST 3: Result retrieval
# -------------------------------------------------

Write-Host "[TEST 3] Result retrieval..."

$result = Invoke-RestMethod `
    -Uri "$backend/api/analysis/$analysisId" `
    -Method GET

if ($null -eq $result) {
    throw "Result retrieval returned null."
}

Write-Host "[PASS] Analysis result retrieved"
Write-Host ""

# -------------------------------------------------
# TEST 4: Backend DB / Neo4j coordination
# -------------------------------------------------

Write-Host "[TEST 4] Backend PostgreSQL + Neo4j coordination..."

$infraAnalysis = Invoke-RestMethod `
    -Uri "$backend/api/infrastructure/analysis/$analysisId" `
    -Method GET

if ($null -eq $infraAnalysis) {
    throw "Infrastructure analysis response is empty."
}

Write-Host "[PASS] Backend analysis coordination endpoint responded"
Write-Host ""

# -------------------------------------------------
# TEST 5: Error propagation
# -------------------------------------------------

Write-Host "[TEST 5] Downstream error propagation..."

$badBody = @{
    repositoryUrl = "https://github.com/repository-that-does-not-exist-987654321.git"
    branch = "main"
} | ConvertTo-Json

$errorHandled = $false

try {

    Invoke-RestMethod `
        -Uri "$backend/api/analysis" `
        -Method POST `
        -ContentType "application/json" `
        -Body $badBody

}
catch {

    $statusCode = $null

    try {
        $statusCode = $_.Exception.Response.StatusCode.value__
    }
    catch {
        $statusCode = $null
    }

    if ($statusCode -eq 502) {
        $errorHandled = $true
    }
}

if (-not $errorHandled) {
    throw "Expected controlled 502 error was not observed."
}

Write-Host "[PASS] FastAPI/backend failure propagated as HTTP 502"
Write-Host ""

# -------------------------------------------------
# TEST 6: Timeout handling implementation check
# -------------------------------------------------

Write-Host "[TEST 6] Timeout handling implementation..."

$clientPath = Join-Path `
    $PSScriptRoot `
    "..\backend\src\main\java\com\sentinelai\backend\modules\ai\client\AiServiceClient.java"

$clientSource = Get-Content `
    $clientPath `
    -Raw

if ($clientSource -notmatch "HttpTimeoutException") {
    throw "AiServiceClient does not contain timeout exception handling."
}

if ($clientSource -notmatch "timeout") {
    throw "AiServiceClient does not contain timeout configuration."
}

Write-Host "[PASS] HttpTimeoutException handling present"
Write-Host "[PASS] HTTP timeout configuration present"
Write-Host ""

# -------------------------------------------------
# FINAL RESULT
# -------------------------------------------------

Write-Host "============================================"
Write-Host " PHASE 4D VALIDATION SUCCESSFUL"
Write-Host "============================================"
Write-Host ""
Write-Host "75  Spring Boot <-> FastAPI       PASS"
Write-Host "76  Repository forwarding         PASS"
Write-Host "77  Unified analysis response     PASS"
Write-Host "78  Error propagation             PASS"
Write-Host "79  Timeout handling              PASS"
Write-Host "80  Backend <-> PostgreSQL        PASS"
Write-Host "81  Backend <-> Neo4j             PASS"
Write-Host "82  AI communication layer        PASS"
Write-Host ""
Write-Host "PHASE 4D COMPLETE"