from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ProviderResult:

    success: bool
    provider: str
    model: str

    content: Optional[str] = None
    error: Optional[str] = None

    input_tokens: int = 0
    output_tokens: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def success_result(
        cls,
        provider: str,
        model: str,
        content: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ):

        return cls(
            success=True,
            provider=provider,
            model=model,
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata=metadata or {},
        )

    @classmethod
    def failure_result(
        cls,
        provider: str,
        model: str,
        error: str,
        metadata: Optional[dict[str, Any]] = None,
    ):

        return cls(
            success=False,
            provider=provider,
            model=model,
            error=error,
            metadata=metadata or {},
        )

    def to_dict(self):

        return {
            "success": self.success,
            "provider": self.provider,
            "model": self.model,
            "content": self.content,
            "error": self.error,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "metadata": self.metadata,
        }