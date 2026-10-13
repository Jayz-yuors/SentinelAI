from fastapi import APIRouter

from ai.infrastructure.health.health_service import (
    application_health,
    complete_health,
)

from ai.infrastructure.metrics.metrics import (
    analysis_metrics
)


router = APIRouter()


@router.get("/health")
def health():

    return application_health()


@router.get("/health/services")
def health_services():

    return complete_health()


@router.get("/health/metrics")
def health_metrics():

    return {
        "success": True,
        "metrics":
            analysis_metrics.snapshot()
    }