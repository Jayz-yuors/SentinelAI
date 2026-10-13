from ai.ai_gateway.provider_result import (
    ProviderResult,
)


class FallbackManager:

    def __init__(
        self,
        providers: dict,
    ):

        self.providers = providers

    def execute(
        self,
        provider_order: list[str],
        prompt: str,
        system_instruction: str | None = None,
    ) -> ProviderResult:

        failures = []

        for provider_name in provider_order:

            provider = self.providers.get(
                provider_name
            )

            if provider is None:

                failures.append(
                    f"{provider_name}: "
                    "provider not registered"
                )

                continue

            if not provider.is_available():

                failures.append(
                    f"{provider_name}: "
                    "unavailable"
                )

                continue

            result = provider.generate(
                prompt=prompt,
                system_instruction=system_instruction,
            )

            if result.success:

                result.metadata[
                    "fallback_attempts"
                ] = failures

                return result

            failures.append(
                f"{provider_name}: "
                f"{result.error}"
            )

        return ProviderResult.failure_result(
            provider="fallback_manager",
            model="none",
            error=(
                "All configured AI "
                "providers failed."
            ),
            metadata={
                "failures": failures,
            },
        )