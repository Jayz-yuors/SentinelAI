from ai.dependency.graph.graph_model import (
    DependencyGraph
)


def build_dependency_graph(
    dependency_data
):
    """
    Build a graph from dependency extraction results.
    """

    graph = DependencyGraph()

    for file_data in dependency_data:

        source = file_data["file"]

        graph.add_node(
            source,
            node_type="file",
            metadata={
                "language": file_data.get(
                    "language"
                )
            }
        )

        for dependency in file_data.get(
            "dependencies",
            []
        ):

            dependency_name = dependency[
                "name"
            ]

            dependency_type = dependency[
                "type"
            ]

            if dependency_type == "internal":

                target = dependency[
                    "resolvedFile"
                ]

                graph.add_edge(
                    source,
                    target,
                    "internal_dependency"
                )

            else:

                external_node = (
                    f"external:{dependency_name}"
                )

                graph.add_node(
                    external_node,
                    node_type="external_package",
                    metadata={
                        "package": dependency_name
                    }
                )

                graph.add_edge(
                    source,
                    external_node,
                    "external_dependency"
                )

    return graph