from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:

    tool: str
    success: bool

    findings: list[dict[str, Any]] = field(
        default_factory=list
    )

    raw_output: str = ""

    error: str | None = None

    execution_time_ms: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):
        return {
            "tool": self.tool,
            "success": self.success,
            "findings": self.findings,
            "raw_output": self.raw_output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
        }