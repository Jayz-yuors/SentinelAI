from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DependencyNode:

    name: str

    node_type: str = "file"

    metadata: Dict = field(
        default_factory=dict
    )


@dataclass
class DependencyEdge:

    source: str

    target: str

    dependency_type: str = "depends_on"


@dataclass
class DependencyGraph:

    nodes: Dict[str, DependencyNode] = field(
        default_factory=dict
    )

    edges: List[DependencyEdge] = field(
        default_factory=list
    )

    def add_node(
        self,
        name: str,
        node_type: str = "file",
        metadata=None
    ):

        if name not in self.nodes:

            self.nodes[name] = DependencyNode(
                name=name,
                node_type=node_type,
                metadata=metadata or {}
            )

    def add_edge(
        self,
        source: str,
        target: str,
        dependency_type: str = "depends_on"
    ):

        self.add_node(source)
        self.add_node(target)

        edge = DependencyEdge(
            source=source,
            target=target,
            dependency_type=dependency_type
        )

        if edge not in self.edges:

            self.edges.append(edge)

    def get_dependencies(
        self,
        file_name: str
    ):

        return [
            edge.target
            for edge in self.edges
            if edge.source == file_name
        ]

    def get_dependents(
        self,
        file_name: str
    ):

        return [
            edge.source
            for edge in self.edges
            if edge.target == file_name
        ]

    def to_dict(self):

        return {
            "nodes": [
                {
                    "name": node.name,
                    "type": node.node_type,
                    "metadata": node.metadata
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.dependency_type
                }
                for edge in self.edges
            ]
        }