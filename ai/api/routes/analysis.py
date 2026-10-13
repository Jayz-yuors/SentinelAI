from fastapi import APIRouter, HTTPException

from ai.api.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
)

from ai.analyzer.repository.scanner import (
    analyze_repository
)

from ai.pipeline.pipeline_service import (
    execute_pipeline
)

from ai.database.postgres.repositories.analysis_repository import (
    get_analysis,
    list_analyses,
)

from ai.database.neo4j.analysis_graph_repository import (
    get_analysis_graph
)


router = APIRouter()


# ---------------------------------------------------------
# Direct analysis
# Existing Phase 1 + Phase 2 + Phase 3 endpoint
# ---------------------------------------------------------

@router.post(
    "/analyze",
    response_model=AnalysisResponse
)
def analyze(
    request: AnalysisRequest
):

    result = analyze_repository(
        request.repositoryUrl,
        request.branch
    )

    return result


# ---------------------------------------------------------
# Full Phase 4 pipeline
# ---------------------------------------------------------

@router.post(
    "/pipeline/analyze"
)
def pipeline_analyze(
    request: AnalysisRequest
):

    return execute_pipeline(
        request.repositoryUrl,
        request.branch
    )


# ---------------------------------------------------------
# Get analysis status/result
# ---------------------------------------------------------

@router.get(
    "/pipeline/{analysis_id}"
)
def get_pipeline_analysis(
    analysis_id: str
):

    result = get_analysis(
        analysis_id
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Analysis '{analysis_id}' "
                f"not found."
            )
        )

    return result


# ---------------------------------------------------------
# Analysis history
# ---------------------------------------------------------

@router.get(
    "/pipeline"
)
def analysis_history(
    repositoryUrl: str | None = None,
    limit: int = 20
):

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    return {
        "success": True,
        "analyses": list_analyses(
            repository_url=repositoryUrl,
            limit=limit
        )
    }


# ---------------------------------------------------------
# Neo4j graph result
# ---------------------------------------------------------

@router.get(
    "/pipeline/{analysis_id}/graph"
)
def analysis_graph(
    analysis_id: str
):

    result = get_analysis_graph(
        analysis_id
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Analysis '{analysis_id}' "
                f"graph not found."
            )
        )

    return {
        "success": True,
        **result
    }