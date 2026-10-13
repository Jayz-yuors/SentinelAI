from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/devsecops",
    tags=["DevSecOps"],
)


class RepositoryRequest(BaseModel):
    repository_path: str = Field(
        ...,
        min_length=1,
    )


@router.get("/status")
def devsecops_status():
    return {
        "service": "SentinelAI DevSecOps API",
        "status": "UP",
    }


@router.post("/scan")
def scan_repository(
    request: RepositoryRequest,
):
    """
    Run the SentinelAI security pipeline against
    a local repository.
    """

    repository_path = Path(
        request.repository_path
    ).resolve()

    if not repository_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Repository path does not exist: "
                f"{repository_path}"
            ),
        )

    if not repository_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Repository path must be a directory.",
        )

    try:

        from ai.integrations.security.security_pipeline import (
            SecurityPipeline,
        )

        pipeline = SecurityPipeline()

        # Use the existing runtime API.
        if hasattr(pipeline, "run"):
            result = pipeline.run(
                str(repository_path)
            )

        elif hasattr(
            pipeline,
            "run_all_available",
        ):
            result = pipeline.run_all_available(
                str(repository_path)
            )

        else:
            raise RuntimeError(
                "SecurityPipeline has neither "
                "run() nor run_all_available()."
            )

        if hasattr(
            result,
            "to_dict",
        ):
            result = result.to_dict()

        return {
            "success": True,
            "repository": str(
                repository_path
            ),
            "result": result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/gate")
def evaluate_gate(
    request: RepositoryRequest,
):
    """
    Run the security pipeline and evaluate
    the resulting risk profile against the
    SentinelAI security gate.
    """

    repository_path = Path(
        request.repository_path
    ).resolve()

    if not repository_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Repository path does not exist: "
                f"{repository_path}"
            ),
        )

    try:

        from ai.integrations.security.security_pipeline import (
            SecurityPipeline,
        )

        from ai.integrations.security.security_gate import (
            SecurityGate,
        )

        pipeline = SecurityPipeline()

        if hasattr(pipeline, "run"):
            profile = pipeline.run(
                str(repository_path)
            )

        elif hasattr(
            pipeline,
            "run_all_available",
        ):
            profile = pipeline.run_all_available(
                str(repository_path)
            )

        else:
            raise RuntimeError(
                "SecurityPipeline has neither "
                "run() nor run_all_available()."
            )

        gate = SecurityGate()

        gate_result = gate.evaluate(
            profile
        )

        return {
            "success": True,
            "repository": str(
                repository_path
            ),
            "gate": gate_result.to_dict(),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )