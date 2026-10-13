from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityToolConfig:
    name: str
    executable: str
    timeout_seconds: int = 300
    enabled: bool = True