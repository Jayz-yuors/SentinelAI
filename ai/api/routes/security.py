import shutil
import subprocess
import tempfile

from pathlib import Path

from fastapi import APIRouter, HTTPException

from ai.api.schemas.security import (
    SecurityAnalysisRequest,
    SecurityAnalysisResponse
)

from ai.security.security_pipeline import (
    analyze_security_repository
)


router = APIRouter(
    prefix="/security",
    tags=["Security Analysis"]
)


# ============================================================
# GIT CLONE
# ============================================================

def clone_repository(
    repository_url: str,
    branch: str,
    destination: str
):

    command = [

        "git",
        "clone",

        "--depth",
        "20",

        "--branch",
        branch,

        repository_url,

        destination
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            result.stderr.strip()
        )


# ============================================================
# SECURITY ANALYSIS ENDPOINT
# ============================================================

@router.post(
    "/analyze",
    response_model=SecurityAnalysisResponse
)
def security_analyze(
    request: SecurityAnalysisRequest
):

    temporary_directory = (
        tempfile.mkdtemp(
            prefix="sentinelai_security_"
        )
    )

    repository_path = (
        Path(temporary_directory)
        / "repository"
    )

    try:

        clone_repository(
            request.repositoryUrl,
            request.branch,
            str(repository_path)
        )

        result = analyze_security_repository(
            repository_path
        )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        shutil.rmtree(
            temporary_directory,
            ignore_errors=True
        )