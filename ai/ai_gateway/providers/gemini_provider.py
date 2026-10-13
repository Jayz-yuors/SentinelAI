from google import genai

from ai.ai_gateway.base_provider import BaseAIProvider
from ai.ai_gateway.provider_config import AIProviderConfig
from ai.ai_gateway.provider_result import ProviderResult


class GeminiProvider(BaseAIProvider):
    def __init__(self, model: str | None = None):
        self._model = model or AIProviderConfig.gemini_model
        self._api_key = AIProviderConfig.gemini_api_key
        configured_keys = [
            ("GEMINI_API_KEY", AIProviderConfig.gemini_api_key),
            ("GEMINI_API_KEY_2", AIProviderConfig.gemini_api_key_2),
        ]
        self._clients = []
        for key_name, api_key in configured_keys:
            if not api_key or not api_key.strip():
                continue
            clean_key = api_key.strip()
            if any(existing_key == clean_key for _, existing_key, _ in self._clients):
                continue
            self._clients.append(
                (key_name, clean_key, genai.Client(api_key=clean_key))
            )

        # Keep the primary client attribute for compatibility with existing callers.
        self._client = self._clients[0][2] if self._clients else None

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model

    def is_available(self) -> bool:
        return bool(self._clients)

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> ProviderResult:
        if not self._clients:
            return ProviderResult.failure_result(
                provider=self.name,
                model=self.model,
                error=(
                    "Neither GEMINI_API_KEY nor "
                    "GEMINI_API_KEY_2 is configured."
                ),
            )

        failures = []
        for key_name, api_key, client in self._clients:
            try:
                kwargs = {
                    "model": self.model,
                    "input": prompt,
                    "store": False,
                }
                if system_instruction:
                    kwargs["system_instruction"] = system_instruction

                interaction = client.interactions.create(**kwargs)
                content = getattr(interaction, "output_text", None) or ""
                usage = getattr(interaction, "usage", None)
                input_tokens = (
                    getattr(usage, "total_input_tokens", 0) if usage else 0
                )
                output_tokens = (
                    getattr(usage, "total_output_tokens", 0) if usage else 0
                )
                return ProviderResult.success_result(
                    provider=self.name,
                    model=self.model,
                    content=content,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    metadata={
                        "api": "gemini-interactions",
                        "key_slot": key_name,
                        "interaction_id": getattr(interaction, "id", None),
                    },
                )
            except Exception as exc:
                # Provider exceptions can include request details; never expose keys.
                error = str(exc).replace(api_key, "[REDACTED]")
                failures.append(f"{key_name}: {error}")

        return ProviderResult.failure_result(
            provider=self.name,
            model=self.model,
            error="; ".join(failures),
        )
