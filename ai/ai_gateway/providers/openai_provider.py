from openai import OpenAI

from ai.ai_gateway.base_provider import BaseAIProvider
from ai.ai_gateway.provider_config import AIProviderConfig
from ai.ai_gateway.provider_result import ProviderResult


class OpenAIProvider(BaseAIProvider):

    def __init__(self):

        self._model = (
            AIProviderConfig.openai_model
        )

        self._api_key = (
            AIProviderConfig.openai_api_key
        )

        self._client = None

        if self._api_key:

            self._client = OpenAI(
                api_key=self._api_key
            )

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return self._model

    def is_available(self) -> bool:

        return self._client is not None

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> ProviderResult:

        if not self._client:

            return ProviderResult.failure_result(
                provider=self.name,
                model=self.model,
                error=(
                    "OPENAI_API_KEY "
                    "is not configured."
                ),
            )

        try:

            if system_instruction:

                response = (
                    self._client.responses.create(
                        model=self.model,
                        instructions=system_instruction,
                        input=prompt,
                    )
                )

            else:

                response = (
                    self._client.responses.create(
                        model=self.model,
                        input=prompt,
                    )
                )

            usage = getattr(
                response,
                "usage",
                None,
            )

            input_tokens = (
                getattr(
                    usage,
                    "input_tokens",
                    0,
                )
                if usage
                else 0
            )

            output_tokens = (
                getattr(
                    usage,
                    "output_tokens",
                    0,
                )
                if usage
                else 0
            )

            content = (
                getattr(
                    response,
                    "output_text",
                    None,
                )
                or ""
            )

            return ProviderResult.success_result(
                provider=self.name,
                model=self.model,
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                metadata={
                    "api": "openai-responses",
                    "response_id": getattr(
                        response,
                        "id",
                        None,
                    ),
                },
            )

        except Exception as exc:

            return ProviderResult.failure_result(
                provider=self.name,
                model=self.model,
                error=str(exc),
            )