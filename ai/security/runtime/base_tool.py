from abc import ABC, abstractmethod

from ai.security.runtime.tool_result import ToolResult


class BaseSecurityTool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def run(
        self,
        repository_path: str
    ) -> ToolResult:
        pass