import httpx

from ai.ai_gateway.base_provider import BaseAIProvider
from ai.ai_gateway.provider_config import AIProviderConfig
from ai.ai_gateway.provider_result import ProviderResult


class GroqProvider(BaseAIProvider):

    BASE_URL = (
        "https://api.groq.com/openai/v1/chat/completions"
    )

    def __init__(self):

        self._model = (
            AIProviderConfig.groq_model
        )

        self._api_key = (
            AIProviderConfig.groq_api_key
        )

    @property
    def name(self) -> str:
        return "groq"

    @property
    def model(self) -> str:
        return self._model

    def is_available(self) -> bool:

        return bool(self._api_key)

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> ProviderResult:

        if not self._api_key:

            return ProviderResult.failure_result(
                self.name,
                self.model,
                "GROQ_API_KEY is not configured.",
            )

        messages = []

        if system_instruction:

            messages.append(
                {
                    "role": "system",
                    "content": system_instruction,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        try:

            response = httpx.post(
                self.BASE_URL,
                headers={
                    "Authorization": (
                        f"Bearer {self._api_key}"
                    ),
                    "Content-Type": (
                        "application/json"
                    ),
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.2,
                },
                timeout=(
                    AIProviderConfig
                    .timeout_seconds
                ),
            )

            response.raise_for_status()

            data = response.json()

            choices = data.get(
                "choices",
                [],
            )

            if not choices:

                raise RuntimeError(
                    "Groq returned no choices."
                )

            content = (
                choices[0]
                .get("message", {})
                .get("content", "")
            )

            usage = data.get(
                "usage",
                {},
            )

            return ProviderResult.success_result(
                provider=self.name,
                model=self.model,
                content=content,
                input_tokens=usage.get(
                    "prompt_tokens",
                    0,
                ),
                output_tokens=usage.get(
                    "completion_tokens",
                    0,
                ),
                metadata={
                    "api": "groq-chat-completions",
                },
            )

        except Exception as exc:

            return ProviderResult.failure_result(
                self.name,
                self.model,
                str(exc),
            )