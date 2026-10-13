from abc import ABC, abstractmethod

from ai.ai_gateway.provider_result import ProviderResult


class BaseAIProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> ProviderResult:
        pass

    def is_available(self) -> bool:
        return True