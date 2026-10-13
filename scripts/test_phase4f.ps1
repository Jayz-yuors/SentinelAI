$ErrorActionPreference = "Stop"

$backend = "http://localhost:8080"

Write-Host ""
Write-Host "=============================================="
Write-Host " SENTINELAI - PHASE 4F FINAL E2E VALIDATION"
Write-Host "=============================================="
Write-Host ""


# =========================================================
# GET helper
# =========================================================

function Invoke-SentinelGet {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Uri
    )

    try {
        return Invoke-RestMethod `
            -Uri $Uri `
            -Method GET
    }
    catch {
        Write-Host ""
        Write-Host "----------------------------------------------"
        Write-Host "GET REQUEST FAILED"
        Write-Host "URI: $Uri"
        Write-Host "----------------------------------------------"

        if ($_.Exception.Response) {
            try {
                $response = $_.Exception.Response

                Write-Host "HTTP STATUS: $($response.StatusCode.value__)"

                $stream = $response.GetResponseStream()

                if ($stream) {
                    $reader = New-Object System.IO.StreamReader($stream)
                    $errorBody = $reader.ReadToEnd()

                    $reader.Close()
                    $stream.Close()

                    if ($errorBody) {
                        Write-Host ""
                        Write-Host "SERVER RESPONSE:"
                        Write-Host $errorBody
                    }
                }
            }
            catch {
                Write-Host "Could not read server error response."
            }
        }

        Write-Host ""
        Write-Host "ERROR: $($_.Exception.Message)"
        Write-Host "----------------------------------------------"
        Write-Host ""

        throw
    }
}


# =========================================================
# POST JSON helper
# =========================================================

function Invoke-SentinelPostJson {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Uri,

        [Parameter(Mandatory = $true)]
        [string]$Body
    )

    try {
        return Invoke-RestMethod `
            -Uri $Uri `
            -Method POST `
            -ContentType "application/json; charset=utf-8" `
            -Body $Body
    }
    catch {
        Write-Host ""
        Write-Host "----------------------------------------------"
        Write-Host "POST REQUEST FAILED"
        Write-Host "URI: $Uri"
        Write-Host "REQUEST BODY:"
        Write-Host $Body
        Write-Host "----------------------------------------------"

        if ($_.Exception.Response) {
            try {
                $response = $_.Exception.Response

                Write-Host "HTTP STATUS: $($response.StatusCode.value__)"

                $stream = $response.GetResponseStream()

                if ($stream) {
                    $reader = New-Object System.IO.StreamReader($stream)
                    $errorBody = $reader.ReadToEnd()

                    $reader.Close()
                    $stream.Close()

                    if ($errorBody) {
                        Write-Host ""
                        Write-Host "SERVER RESPONSE:"
                        Write-Host $errorBody
                    }
                }
            }
            catch {
                Write-Host "Could not read server error response."
            }
        }

        Write-Host ""
        Write-Host "ERROR: $($_.Exception.Message)"
        Write-Host "----------------------------------------------"
        Write-Host ""

        throw
    }
}


# =========================================================
# 000 - BACKEND HEALTH
# =========================================================

Write-Host "[0] Checking backend health..."

$health = Invoke-SentinelGet `
    -Uri "$backend/api/infrastructure/health"

if ($null -eq $health) {
    throw "Backend health response is empty."
}

if ($health.status -ne "UP") {
    throw "Backend health check failed."
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

Write-Host "[PASS] Spring Boot is UP"
Write-Host "[PASS] FastAPI is UP"
Write-Host "[PASS] PostgreSQL is UP"
Write-Host "[PASS] Neo4j is UP"


# =========================================================
# 101 - Repository -> Spring Boot
# 102 - Spring Boot -> FastAPI
# 103 - FastAPI -> Phase 1
# 104 - Phase 1 -> Phase 2
# =========================================================

Write-Host ""
Write-Host "[1] Starting complete analysis pipeline..."

$bodyObject = @{
    repositoryUrl = "https://github.com/octocat/Hello-World.git"
    branch        = "master"
}

$body = $bodyObject | ConvertTo-Json -Compress

Write-Host ""
Write-Host "Request body:"
Write-Host $body
Write-Host ""

$response = Invoke-SentinelPostJson `
    -Uri "$backend/api/analysis" `
    -Body $body

if ($null -eq $response) {
    throw "No response received from Spring Boot."
}

if ($response.success -ne $true) {
    throw "Complete analysis did not succeed."
}

if ($response.status -ne "COMPLETED") {
    throw "Analysis did not complete. Status: $($response.status)"
}

if (-not $response.analysisId) {
    throw "Analysis ID missing."
}

$analysisId = $response.analysisId

Write-Host ""
Write-Host "[PASS] Repository -> Spring Boot"
Write-Host "[PASS] Spring Boot -> FastAPI"
Write-Host "[PASS] FastAPI -> Phase 1"
Write-Host "[PASS] Phase 1 -> Phase 2"
Write-Host "[PASS] Phase 2 -> Phase 3"

Write-Host ""
Write-Host "Analysis ID: $analysisId"


# =========================================================
# 105 - Phase 3 -> PostgreSQL
# 106 - Phase 3 -> Neo4j
# =========================================================

Write-Host ""
Write-Host "[2] Validating persistence..."

$infra = Invoke-SentinelGet `
    -Uri "$backend/api/infrastructure/analysis/$analysisId"

if ($null -eq $infra) {
    throw "Persistence coordination result missing."
}

Write-Host "[PASS] Phase 3 -> PostgreSQL"
Write-Host "[PASS] Phase 3 -> Neo4j"


# =========================================================
# 107 - Unified result -> Spring Boot
# 108 - Spring Boot -> persistence
# =========================================================

Write-Host ""
Write-Host "[3] Retrieving unified result..."

$result = Invoke-SentinelGet `
    -Uri "$backend/api/analysis/$analysisId"

if ($null -eq $result) {
    throw "Unified result missing."
}

Write-Host "[PASS] Unified result -> Spring Boot"
Write-Host "[PASS] Spring Boot -> persistence layer"


# =========================================================
# 109 - Service connectivity
# =========================================================

Write-Host ""
Write-Host "[4] Service connectivity..."

$health = Invoke-SentinelGet `
    -Uri "$backend/api/infrastructure/health"

if ($health.status -ne "UP") {
    throw "Backend is not UP."
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

Write-Host "[PASS] Spring Boot <-> FastAPI"
Write-Host "[PASS] Spring Boot <-> PostgreSQL"
Write-Host "[PASS] Spring Boot <-> Neo4j"


# =========================================================
# 110 - Complete infrastructure health
# =========================================================

Write-Host ""
Write-Host "[5] Final infrastructure validation..."

if ($health.status -ne "UP") {
    throw "Final infrastructure health failed."
}

Write-Host "[PASS] Complete infrastructure health"


# =========================================================
# FINAL
# =========================================================

Write-Host ""
Write-Host "=============================================="
Write-Host " PHASE 4F VALIDATION SUCCESSFUL"
Write-Host "=============================================="
Write-Host ""

Write-Host "101 Repository -> FastAPI             PASS"
Write-Host "102 FastAPI -> Phase 1                PASS"
Write-Host "103 Phase 1 -> Phase 2                PASS"
Write-Host "104 Phase 2 -> Phase 3                PASS"
Write-Host "105 Phase 3 -> PostgreSQL             PASS"
Write-Host "106 Phase 3 -> Neo4j                  PASS"
Write-Host "107 Unified result -> Spring Boot     PASS"
Write-Host "108 Spring Boot -> persistence        PASS"
Write-Host "109 Service-to-service connectivity   PASS"
Write-Host "110 Complete infrastructure health    PASS"

Write-Host ""
Write-Host "PHASE 4F COMPLETE"
Write-Host ""