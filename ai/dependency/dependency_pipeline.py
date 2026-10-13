from pathlib import Path

from ai.dependency.extractor.dependency_extractor import (
    extract_repository_dependencies
)

from ai.dependency.graph.dependency_graph import (
    build_dependency_graph
)

from ai.dependency.graph.graph_analyzer import (
    analyze_graph
)

from ai.dependency.graph.dependency_risk import (
    calculate_dependency_risk
)


def analyze_dependencies(
    repository_path
):
    """
    Execute the complete Phase 2 dependency pipeline.

    Flow:

        Repository
             ↓
        Dependency Extraction
             ↓
        Dependency Graph
             ↓
        Graph Analysis
             ↓
        Dependency Risk
    """

    repository_path = Path(
        repository_path
    )

    if not repository_path.exists():

        raise FileNotFoundError(
            f"Repository path does not exist: "
            f"{repository_path}"
        )

    if not repository_path.is_dir():

        raise NotADirectoryError(
            f"Repository path is not a directory: "
            f"{repository_path}"
        )

    dependency_data = (
        extract_repository_dependencies(
            repository_path
        )
    )

    graph = build_dependency_graph(
        dependency_data
    )

    graph_analysis = analyze_graph(
        graph
    )

    risk_analysis = calculate_dependency_risk(
        graph
    )

    return {
        "success": True,

        "repositoryPath": str(
            repository_path
        ),

        "dependencyExtraction":
            dependency_data,

        "dependencyGraph":
            graph.to_dict(),

        "graphAnalysis":
            graph_analysis,

        "dependencyRisk":
            risk_analysis,

        "message":
            "Dependency analysis completed successfully"
    }