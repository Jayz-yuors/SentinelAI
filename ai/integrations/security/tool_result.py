from dataclasses import dataclass


@dataclass
class SecurityToolResult:
    tool: str
    command: list[str]
    return_code: int
    stdout: str
    stderr: str
    report_path: str | None = None

    @property
    def success(self) -> bool:
        return self.return_code == 0