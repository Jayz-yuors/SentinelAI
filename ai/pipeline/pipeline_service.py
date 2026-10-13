import time
import uuid
from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError
)
from pathlib import Path

from ai.analyzer.repository.scanner import (
    analyze_repository
)

from ai.database.neo4j.analysis_graph_repository import (
    save_analysis_graph
)

from ai.database.postgres.repositories.analysis_repository import (
    save_analysis,
    update_analysis_status,
    save_phase_result,
    save_unified_result,
)

from ai.infrastructure.config.settings import (
    PIPELINE_MAX_RETRIES,
    PIPELINE_TIMEOUT_SECONDS,
)

from ai.infrastructure.constants.application_constants import (
    PIPELINE_RUNNING,
    PIPELINE_PHASE_1,
    PIPELINE_PHASE_2,
    PIPELINE_PHASE_3,
    PIPELINE_COMPLETED,
    PIPELINE_FAILED,
    PIPELINE_TIMEOUT,
)

from ai.infrastructure.logging.logger import (
    get_logger
)

from ai.infrastructure.metrics.metrics import (
    analysis_metrics
)


logger = get_logger(
    "sentinelai.pipeline"
)


def _repository_name(
    repository_url: str
):

    clean_url = (
        repository_url
        .rstrip("/")
    )

    name = clean_url.split("/")[-1]

    if name.endswith(".git"):
        name = name[:-4]

    return name or "repository"


def execute_pipeline(
    repository_url: str,
    branch: str = "main",
):

    analysis_id = str(
        uuid.uuid4()
    )

    started_at = (
        analysis_metrics.start()
    )

    repository_name = _repository_name(
        repository_url
    )

    logger.info(
        "Starting analysis %s",
        analysis_id
    )

    save_analysis(
        analysis_id=analysis_id,
        repository_url=repository_url,
        repository_name=repository_name,
        branch=branch,
        status=PIPELINE_RUNNING,
    )

    update_analysis_status(
        analysis_id,
        PIPELINE_PHASE_1
    )

    attempts = 0

    while attempts <= PIPELINE_MAX_RETRIES:

        attempts += 1

        try:

            logger.info(
                "Analysis %s attempt %s",
                analysis_id,
                attempts
            )

            # -------------------------------------------------
            # PHASE 1 + PHASE 2 + PHASE 3
            # Existing scanner already performs the complete
            # Phase 1 -> Phase 2 -> Phase 3 analysis.
            # -------------------------------------------------

            update_analysis_status(
                analysis_id,
                PIPELINE_PHASE_1
            )

            with ThreadPoolExecutor(
                max_workers=1
            ) as executor:

                future = executor.submit(
                    analyze_repository,
                    repository_url,
                    branch
                )

                try:

                    result = future.result(
                        timeout=PIPELINE_TIMEOUT_SECONDS
                    )

                except TimeoutError:

                    update_analysis_status(
                        analysis_id,
                        PIPELINE_TIMEOUT,
                        "Analysis exceeded pipeline timeout."
                    )

                    analysis_metrics.record_failure(
                        started_at
                    )

                    return {
                        "success": False,
                        "analysisId": analysis_id,
                        "status": PIPELINE_TIMEOUT,
                        "result": {},
                        "error": (
                            "Analysis exceeded "
                            "pipeline timeout."
                        ),
                        "attempts": attempts,
                    }

            if not result.get(
                "success",
                False
            ):

                raise RuntimeError(
                    result.get(
                        "message",
                        "Repository analysis failed."
                    )
                )

            # -------------------------------------------------
            # Persist phase results
            # -------------------------------------------------

            update_analysis_status(
                analysis_id,
                PIPELINE_PHASE_1
            )

            save_phase_result(
                analysis_id,
                1,
                {
                    "success": True,
                    "repositoryUrl":
                        result.get(
                            "repositoryUrl"
                        ),
                    "repositoryName":
                        result.get(
                            "repositoryName"
                        ),
                    "branch":
                        result.get(
                            "branch"
                        ),
                    "totalFiles":
                        result.get(
                            "totalFiles",
                            0
                        ),
                    "languages":
                        result.get(
                            "languages",
                            []
                        ),
                    "fileTypes":
                        result.get(
                            "fileTypes",
                            {}
                        ),
                    "changedFiles":
                        result.get(
                            "changedFiles",
                            []
                        ),
                    "codeStructure":
                        result.get(
                            "codeStructure",
                            []
                        ),
                    "imports":
                        result.get(
                            "imports",
                            {}
                        ),
                    "latestCommit":
                        result.get(
                            "latestCommit"
                        ),
                    "impactAnalysis":
                        result.get(
                            "impactAnalysis",
                            {}
                        ),
                }
            )

            update_analysis_status(
                analysis_id,
                PIPELINE_PHASE_2
            )

            save_phase_result(
                analysis_id,
                2,
                {
                    "dependencyExtraction":
                        result.get(
                            "dependencyExtraction",
                            []
                        ),
                    "dependencyGraph":
                        result.get(
                            "dependencyGraph",
                            {}
                        ),
                    "graphAnalysis":
                        result.get(
                            "graphAnalysis",
                            {}
                        ),
                    "dependencyRisk":
                        result.get(
                            "dependencyRisk",
                            {}
                        ),
                }
            )

            update_analysis_status(
                analysis_id,
                PIPELINE_PHASE_3
            )

            save_phase_result(
                analysis_id,
                3,
                {
                    "securityAnalysis":
                        result.get(
                            "securityAnalysis",
                            {}
                        )
                }
            )

            # -------------------------------------------------
            # Unified result
            # -------------------------------------------------

            unified_result = {
                "analysisId": analysis_id,
                "status": PIPELINE_COMPLETED,

                "repositoryUrl":
                    result.get(
                        "repositoryUrl"
                    ),

                "repositoryName":
                    result.get(
                        "repositoryName"
                    ),

                "branch":
                    result.get(
                        "branch"
                    ),

                "phase1": {
                    "totalFiles":
                        result.get(
                            "totalFiles",
                            0
                        ),
                    "languages":
                        result.get(
                            "languages",
                            []
                        ),
                    "fileTypes":
                        result.get(
                            "fileTypes",
                            {}
                        ),
                    "changedFiles":
                        result.get(
                            "changedFiles",
                            []
                        ),
                    "codeStructure":
                        result.get(
                            "codeStructure",
                            []
                        ),
                    "imports":
                        result.get(
                            "imports",
                            {}
                        ),
                    "latestCommit":
                        result.get(
                            "latestCommit"
                        ),
                    "impactAnalysis":
                        result.get(
                            "impactAnalysis",
                            {}
                        ),
                },

                "phase2": {
                    "dependencyExtraction":
                        result.get(
                            "dependencyExtraction",
                            []
                        ),
                    "dependencyGraph":
                        result.get(
                            "dependencyGraph",
                            {}
                        ),
                    "graphAnalysis":
                        result.get(
                            "graphAnalysis",
                            {}
                        ),
                    "dependencyRisk":
                        result.get(
                            "dependencyRisk",
                            {}
                        ),
                },

                "phase3": {
                    "securityAnalysis":
                        result.get(
                            "securityAnalysis",
                            {}
                        )
                },

                # Backward-compatible top-level fields
                "totalFiles":
                    result.get(
                        "totalFiles",
                        0
                    ),

                "languages":
                    result.get(
                        "languages",
                        []
                    ),

                "changedFiles":
                    result.get(
                        "changedFiles",
                        []
                    ),

                "dependencyGraph":
                    result.get(
                        "dependencyGraph",
                        {}
                    ),

                "dependencyRisk":
                    result.get(
                        "dependencyRisk",
                        {}
                    ),

                "securityAnalysis":
                    result.get(
                        "securityAnalysis",
                        {}
                    ),
            }

            save_unified_result(
                analysis_id,
                unified_result
            )

            # -------------------------------------------------
            # Neo4j
            # -------------------------------------------------

            try:

                save_analysis_graph(
                    analysis_id,
                    repository_url,
                    repository_name,
                    unified_result
                )

            except Exception as graph_error:

                # Graph persistence must not destroy a
                # successfully completed analysis.

                logger.error(
                    "Neo4j persistence failed for %s: %s",
                    analysis_id,
                    graph_error
                )

            update_analysis_status(
                analysis_id,
                PIPELINE_COMPLETED
            )

            analysis_metrics.record_success(
                started_at
            )

            logger.info(
                "Analysis completed %s",
                analysis_id
            )

            return {
                "success": True,
                "analysisId": analysis_id,
                "status": PIPELINE_COMPLETED,
                "result": unified_result,
                "attempts": attempts,
            }

        except Exception as exc:

            logger.exception(
                "Analysis %s failed on attempt %s",
                analysis_id,
                attempts
            )

            if attempts > PIPELINE_MAX_RETRIES:

                update_analysis_status(
                    analysis_id,
                    PIPELINE_FAILED,
                    str(exc)
                )

                analysis_metrics.record_failure(
                    started_at
                )

                return {
                    "success": False,
                    "analysisId": analysis_id,
                    "status": PIPELINE_FAILED,
                    "result": {},
                    "error": str(exc),
                    "attempts": attempts,
                }

    return {
        "success": False,
        "analysisId": analysis_id,
        "status": PIPELINE_FAILED,
        "result": {},
        "error": "Pipeline failed.",
        "attempts": attempts,
    }