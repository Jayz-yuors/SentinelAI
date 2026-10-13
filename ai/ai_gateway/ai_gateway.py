from ai.ai_gateway.fallback_manager import (
    FallbackManager,
)
from ai.ai_gateway.provider_config import (
    AIProviderConfig,
)

from ai.ai_gateway.providers.gemini_provider import (
    GeminiProvider,
)

from ai.ai_gateway.providers.groq_provider import (
    GroqProvider,
)


class AIGateway:

    def __init__(self):

        self.providers = {

            "gemini": GeminiProvider(
                AIProviderConfig.gemini_model
            ),

            "groq": GroqProvider(),
        }

        self.fallback_manager = (
            FallbackManager(
                self.providers
            )
        )

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ):

        if not AIProviderConfig.enabled:

            raise RuntimeError(
                "SentinelAI AI gateway "
                "is disabled."
            )

        order = []

        if (
            AIProviderConfig.primary_provider
        ):

            order.append(
                AIProviderConfig
                .primary_provider
            )

        for provider in (
            AIProviderConfig
            .fallback_providers
        ):

            if provider not in order:

                order.append(provider)

        return self.fallback_manager.execute(
            provider_order=order,
            prompt=prompt,
            system_instruction=system_instruction,
        )

    def generate_with_provider(
        self,
        provider_name: str,
        prompt: str,
        system_instruction: str | None = None,
    ):

        provider = self.providers.get(
            provider_name
        )

        if provider is None:

            raise ValueError(
                f"Unknown AI provider: "
                f"{provider_name}"
            )

        return provider.generate(
            prompt=prompt,
            system_instruction=system_instruction,
        )

    def provider_status(self):

        return {
            name: {
                "available": provider.is_available(),
                "model": provider.model,
            }
            for name, provider
            in self.providers.items()
        }
