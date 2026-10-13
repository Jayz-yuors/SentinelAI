# ============================================================
# SENTINELAI — LOCAL FILE REMEDIATION TEST
# ============================================================
#
# Test scenario:
#
#   Git repository
#          +
#   existing target file
#          +
#   developer's local replacement
#          ↓
#       SentinelAI
#
# SentinelAI is expected to:
#
#   1. Verify repository
#   2. Verify target file
#   3. Capture original file
#   4. Compare ORIGINAL vs USER file
#   5. Run SentinelAI analysis
#   6. Generate AI version
#   7. Compare USER vs AI version
#   8. Verify AI version
#   9. Security rescan
#  10. Calculate risk delta
#  11. Apply security gate
#  12. Create candidate branch
#  13. Commit
#  14. Push
#  15. Generate complete documentation
#
# ============================================================

$ErrorActionPreference = "Stop"

$SentinelRoot = Split-Path -Parent $PSScriptRoot

Set-Location $SentinelRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "       SENTINELAI LOCAL REMEDIATION TEST" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# Python
# ------------------------------------------------------------

$Python = Join-Path `
    $SentinelRoot `
    "venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {

    Write-Host "[FAIL] SentinelAI virtual environment not found." `
        -ForegroundColor Red

    Write-Host ""
    Write-Host "Expected:"
    Write-Host $Python

    exit 1
}

Write-Host "[PASS] SentinelAI Python environment." `
    -ForegroundColor Green


# ------------------------------------------------------------
# Ask repository
# ------------------------------------------------------------

Write-Host ""
Write-Host "STEP 1 — GIT REPOSITORY" -ForegroundColor Cyan
Write-Host ""

$Repository = Read-Host `
    "Enter FULL path of the Git repository"

$Repository = $Repository.Trim().Trim('"').Trim("'")

if (-not (Test-Path $Repository -PathType Container)) {

    Write-Host ""
    Write-Host "[FAIL] Repository folder does not exist." `
        -ForegroundColor Red

    exit 1
}

$Repository = (
    Resolve-Path $Repository
).Path

if (-not (Test-Path (Join-Path $Repository ".git"))) {

    Write-Host ""
    Write-Host "[FAIL] This folder is not a Git repository." `
        -ForegroundColor Red

    exit 1
}

Write-Host "[PASS] Git repository found:" `
    -ForegroundColor Green

Write-Host $Repository


# ------------------------------------------------------------
# Ask target path
# ------------------------------------------------------------

Write-Host ""
Write-Host "STEP 2 — TARGET FILE" -ForegroundColor Cyan
Write-Host ""

$TargetRelative = Read-Host `
    "Enter target file path relative to repository"

$TargetRelative = `
    $TargetRelative.Trim().Trim('"').Trim("'")

$TargetRelative = `
    $TargetRelative.Replace("/", "\")

$TargetFile = Join-Path `
    $Repository `
    $TargetRelative


if (-not (Test-Path $TargetFile -PathType Leaf)) {

    Write-Host ""
    Write-Host "[FAIL] Target file does not exist in repository." `
        -ForegroundColor Red

    Write-Host ""
    Write-Host "Expected:"
    Write-Host $TargetFile

    exit 1
}

Write-Host "[PASS] Existing target file found." `
    -ForegroundColor Green

Write-Host $TargetFile


# ------------------------------------------------------------
# Ask local replacement
# ------------------------------------------------------------

Write-Host ""
Write-Host "STEP 3 — LOCAL REPLACEMENT" `
    -ForegroundColor Cyan

Write-Host ""

$LocalFile = Read-Host `
    "Enter FULL path of your local replacement file"

$LocalFile = `
    $LocalFile.Trim().Trim('"').Trim("'")

if (-not (Test-Path $LocalFile -PathType Leaf)) {

    Write-Host ""
    Write-Host "[FAIL] Local replacement file does not exist." `
        -ForegroundColor Red

    exit 1
}

$LocalFile = (
    Resolve-Path $LocalFile
).Path

Write-Host "[PASS] Local replacement found." `
    -ForegroundColor Green

Write-Host $LocalFile


# ------------------------------------------------------------
# Verify same filename
# ------------------------------------------------------------

$TargetName = Split-Path `
    $TargetFile `
    -Leaf

$LocalName = Split-Path `
    $LocalFile `
    -Leaf


if ($TargetName -ne $LocalName) {

    Write-Host ""
    Write-Host "[FAIL] File names do not match." `
        -ForegroundColor Red

    Write-Host ""
    Write-Host "Repository target:"
    Write-Host $TargetName

    Write-Host ""
    Write-Host "Local file:"
    Write-Host $LocalName

    exit 1
}

Write-Host "[PASS] Target and replacement filenames match." `
    -ForegroundColor Green


# ------------------------------------------------------------
# Git information
# ------------------------------------------------------------

Push-Location $Repository

try {

    $Branch = (
        git branch --show-current
    ).Trim()

    $Remote = (
        git remote get-url origin 2>$null
    ).Trim()

    $Status = (
        git status --porcelain
    )

}
finally {

    Pop-Location

}


if ([string]::IsNullOrWhiteSpace($Branch)) {

    Write-Host ""
    Write-Host "[FAIL] Could not determine Git branch." `
        -ForegroundColor Red

    exit 1
}


if ([string]::IsNullOrWhiteSpace($Remote)) {

    Write-Host ""
    Write-Host "[FAIL] GitHub origin remote not configured." `
        -ForegroundColor Red

    exit 1
}


Write-Host ""
Write-Host "============================================================" `
    -ForegroundColor Cyan

Write-Host "REPOSITORY INFORMATION" `
    -ForegroundColor Cyan

Write-Host "============================================================" `
    -ForegroundColor Cyan

Write-Host ""

Write-Host "Repository:" -ForegroundColor Yellow
Write-Host $Repository

Write-Host ""
Write-Host "Branch:" -ForegroundColor Yellow
Write-Host $Branch

Write-Host ""
Write-Host "Remote:" -ForegroundColor Yellow
Write-Host $Remote

Write-Host ""
Write-Host "Target:" -ForegroundColor Yellow
Write-Host $TargetRelative

Write-Host ""
Write-Host "Local replacement:" -ForegroundColor Yellow
Write-Host $LocalFile


# ------------------------------------------------------------
# Final confirmation
# ------------------------------------------------------------

Write-Host ""
Write-Host "============================================================" `
    -ForegroundColor Cyan

Write-Host "SENTINELAI WILL PERFORM" `
    -ForegroundColor Cyan

Write-Host "============================================================" `
    -ForegroundColor Cyan

Write-Host ""

Write-Host "1. Capture original repository file"
Write-Host "2. Compare original -> developer file"
Write-Host "3. Analyze repository"
Write-Host "4. Analyze dependencies"
Write-Host "5. Run security analysis"
Write-Host "6. Calculate risk"
Write-Host "7. AI review"
Write-Host "8. AI-generated remediation"
Write-Host "9. Compare developer -> AI"
Write-Host "10. Verify generated code"
Write-Host "11. Security re-scan"
Write-Host "12. Risk comparison"
Write-Host "13. Security gate"
Write-Host "14. Create candidate branch"
Write-Host "15. Commit"
Write-Host "16. Push candidate branch"
Write-Host "17. Generate complete evidence"
Write-Host ""

$Confirm = Read-Host `
    "Continue? (YES/NO)"

if ($Confirm.ToUpper() -ne "YES") {

    Write-Host ""
    Write-Host "Test cancelled." `
        -ForegroundColor Yellow

    exit 0
}


# ------------------------------------------------------------
# Call SentinelAI remediation workflow
# ------------------------------------------------------------

Write-Host ""
Write-Host "============================================================" `
    -ForegroundColor Green

Write-Host "STARTING SENTINELAI" `
    -ForegroundColor Green

Write-Host "============================================================" `
    -ForegroundColor Green

Write-Host ""

& $Python `
    -m ai.cli.main `
    remediate-local `
    --repository "$Repository" `
    --target "$TargetRelative" `
    --local-file "$LocalFile" `
    --push

$ExitCode = $LASTEXITCODE


# ------------------------------------------------------------
# Result
# ------------------------------------------------------------

Write-Host ""

if ($ExitCode -eq 0) {

    Write-Host "============================================================" -ForegroundColor Green

    Write-Host "       SENTINELAI REMEDIATION PASSED" -ForegroundColor Green

    Write-Host "============================================================" -ForegroundColor Green

}
else {

    Write-Host "============================================================" -ForegroundColor Red

    Write-Host "       SENTINELAI REMEDIATION FAILED" -ForegroundColor Red

    Write-Host "============================================================" -ForegroundColor Red

    exit $ExitCode
}
