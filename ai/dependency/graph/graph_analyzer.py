from typing import Set

from ai.dependency.graph.graph_model import (
    DependencyGraph
)


def calculate_dependency_counts(
    graph: DependencyGraph
):

    result = {}

    for node_name in graph.nodes:

        result[node_name] = {
            "dependencies": len(
                graph.get_dependencies(
                    node_name
                )
            ),
            "dependents": len(
                graph.get_dependents(
                    node_name
                )
            )
        }

    return result


def find_high_impact_files(
    graph: DependencyGraph,
    minimum_dependents: int = 2
):

    counts = calculate_dependency_counts(
        graph
    )

    result = []

    for file_name, data in counts.items():

        if (
            data["dependents"]
            >= minimum_dependents
        ):

            result.append({
                "file": file_name,
                "dependents": data[
                    "dependents"
                ],
                "dependencies": data[
                    "dependencies"
                ]
            })

    return sorted(
        result,
        key=lambda item: item["dependents"],
        reverse=True
    )


def detect_cycles(
    graph: DependencyGraph
):
    """
    Detect cycles using DFS.
    """

    adjacency = {}

    for node in graph.nodes:

        adjacency[node] = []

    for edge in graph.edges:

        adjacency.setdefault(
            edge.source,
            []
        ).append(
            edge.target
        )

    visited: Set[str] = set()
    recursion_stack: Set[str] = set()

    cycles = []

    def dfs(
        node,
        path
    ):

        visited.add(node)
        recursion_stack.add(node)

        for neighbor in adjacency.get(
            node,
            []
        ):

            if neighbor not in visited:

                dfs(
                    neighbor,
                    path + [neighbor]
                )

            elif neighbor in recursion_stack:

                if neighbor in path:

                    index = path.index(
                        neighbor
                    )

                    cycle = (
                        path[index:]
                        + [neighbor]
                    )

                    if cycle not in cycles:

                        cycles.append(
                            cycle
                        )

        recursion_stack.discard(
            node
        )

    for node in graph.nodes:

        if node not in visited:

            dfs(
                node,
                [node]
            )

    return cycles


def find_isolated_nodes(
    graph: DependencyGraph
):

    isolated = []

    for node_name in graph.nodes:

        has_outgoing = bool(
            graph.get_dependencies(
                node_name
            )
        )

        has_incoming = bool(
            graph.get_dependents(
                node_name
            )
        )

        if not has_outgoing and not has_incoming:

            isolated.append(
                node_name
            )

    return sorted(
        isolated
    )


def analyze_graph(
    graph: DependencyGraph
):

    counts = calculate_dependency_counts(
        graph
    )

    high_impact = find_high_impact_files(
        graph
    )

    cycles = detect_cycles(
        graph
    )

    isolated = find_isolated_nodes(
        graph
    )

    return {
        "totalNodes": len(
            graph.nodes
        ),

        "totalEdges": len(
            graph.edges
        ),

        "dependencyCounts": counts,

        "highImpactFiles": high_impact,

        "circularDependencies": cycles,

        "isolatedNodes": isolated
    }