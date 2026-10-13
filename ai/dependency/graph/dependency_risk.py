from ai.dependency.graph.graph_model import (
    DependencyGraph
)

from ai.dependency.graph.graph_analyzer import (
    analyze_graph
)


def calculate_dependency_risk(
    graph: DependencyGraph
):
    """
    Calculate a basic dependency risk score.

    This is NOT the final AI decision engine.
    It provides Phase 2 structural risk signals
    that will later be consumed by the AI layer.
    """

    analysis = analyze_graph(
        graph
    )

    risks = []

    for file_name, counts in analysis[
        "dependencyCounts"
    ].items():

        dependency_count = counts[
            "dependencies"
        ]

        dependent_count = counts[
            "dependents"
        ]

        score = 0

        if dependency_count >= 5:
            score += 20
        elif dependency_count >= 3:
            score += 10

        if dependent_count >= 5:
            score += 30
        elif dependent_count >= 3:
            score += 20
        elif dependent_count >= 2:
            score += 10

        if score >= 40:
            level = "HIGH"

        elif score >= 20:
            level = "MEDIUM"

        else:
            level = "LOW"

        risks.append({
            "file": file_name,
            "score": score,
            "riskLevel": level,
            "dependencyCount": dependency_count,
            "dependentCount": dependent_count
        })

    circular_dependencies = analysis[
        "circularDependencies"
    ]

    if circular_dependencies:

        for cycle in circular_dependencies:

            risks.append({
                "file": cycle[0],
                "score": 50,
                "riskLevel": "HIGH",
                "dependencyCount": 0,
                "dependentCount": 0,
                "reason": "Circular dependency",
                "cycle": cycle
            })

    risks.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    if not risks:

        overall_score = 0

    else:

        overall_score = max(
            item["score"]
            for item in risks
        )

    if overall_score >= 40:

        overall_level = "HIGH"

    elif overall_score >= 20:

        overall_level = "MEDIUM"

    else:

        overall_level = "LOW"

    return {
        "overallScore": overall_score,
        "overallRisk": overall_level,
        "fileRisks": risks,
        "circularDependencyCount": len(
            circular_dependencies
        )
    }