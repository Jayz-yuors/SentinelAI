from ai.ai_gateway.ai_gateway import AIGateway


def main():

    print()
    print("=" * 70)
    print(" SENTINELAI — COMPLETE AI GATEWAY TEST")
    print("=" * 70)
    print()

    gateway = AIGateway()

    # ---------------------------------------------------------
    # 1. Registration
    # ---------------------------------------------------------

    print("[1] Checking provider registration...")

    expected = {
        "gemini",
        "groq",
    }

    actual = set(
        gateway.providers.keys()
    )

    assert actual == expected, (
        f"Expected {expected}, got {actual}"
    )

    print("[PASS] Gemini and Groq providers registered")
    print()

    # ---------------------------------------------------------
    # 2. Configuration
    # ---------------------------------------------------------

    print("[2] Checking provider configuration...")

    statuses = gateway.provider_status()

    for name, status in statuses.items():

        state = (
            "CONFIGURED"
            if status["available"]
            else "NOT CONFIGURED"
        )

        print(
            f"  {name:<10}: "
            f"{state:<16} "
            f"{status['model']}"
        )

    print()

    configured = [
        name
        for name, status in statuses.items()
        if status["available"]
    ]

    assert configured, (
        "No AI providers are configured."
    )

    print(
        f"[PASS] Configured providers: "
        f"{', '.join(configured)}"
    )

    print()

    # ---------------------------------------------------------
    # 3. Direct provider tests
    # ---------------------------------------------------------

    print("[3] Testing configured providers...")
    print()

    prompt = (
        'Return exactly this JSON: '
        '{"status":"ok","service":"SentinelAI"}'
    )

    system_instruction = (
        "You are a SentinelAI infrastructure "
        "test provider. "
        "Return only the requested JSON."
    )

    successful_providers = []

    for provider_name in (
        "gemini",
        "groq",
    ):

        provider = gateway.providers[
            provider_name
        ]

        if not provider.is_available():

            print(
                f"[SKIP] {provider_name}: "
                "not configured"
            )

            continue

        print(
            f"  Testing {provider_name}..."
        )

        result = (
            gateway.generate_with_provider(
                provider_name=provider_name,
                prompt=prompt,
                system_instruction=(
                    system_instruction
                ),
            )
        )

        if result.success:

            print(
                f"  [PASS] "
                f"{provider_name} -> "
                f"{result.model}"
            )

            assert result.content

            successful_providers.append(
                provider_name
            )

        else:

            print(
                f"  [FAIL] "
                f"{provider_name}: "
                f"{result.error}"
            )

    print()

    assert successful_providers, (
        "No AI provider successfully "
        "completed a request."
    )

    print(
        "[PASS] Provider generation test"
    )

    print()

    # ---------------------------------------------------------
    # 4. Gateway automatic routing
    # ---------------------------------------------------------

    print(
        "[4] Testing automatic gateway routing..."
    )

    result = gateway.generate(
        prompt=prompt,
        system_instruction=system_instruction,
    )

    assert result.success
    assert result.content
    assert result.provider
    assert result.model

    print(
        f"[PASS] Gateway routed to "
        f"{result.provider}/{result.model}"
    )

    print()

    # ---------------------------------------------------------
    # 5. Fallback metadata
    # ---------------------------------------------------------

    print(
        "[5] Checking fallback metadata..."
    )

    assert isinstance(
        result.metadata,
        dict,
    )

    assert (
        "fallback_attempts"
        in result.metadata
    )

    print(
        "[PASS] Fallback metadata present"
    )

    print()

    # ---------------------------------------------------------
    # 6. Result structure
    # ---------------------------------------------------------

    print(
        "[6] Validating ProviderResult..."
    )

    serialized = result.to_dict()

    required_fields = {
        "success",
        "provider",
        "model",
        "content",
        "error",
        "input_tokens",
        "output_tokens",
        "metadata",
    }

    assert required_fields.issubset(
        serialized.keys()
    )

    print(
        "[PASS] ProviderResult structure"
    )

    print()

    # ---------------------------------------------------------
    # Final
    # ---------------------------------------------------------

    print("=" * 70)
    print(
        " COMPLETE AI GATEWAY TEST PASSED"
    )
    print("=" * 70)
    print()

    print(
        "Successful providers:"
    )

    for provider in successful_providers:

        print(
            f"  ✓ {provider}"
        )

    print()

    print(
        "AI Gateway status: READY"
    )

    print()


if __name__ == "__main__":
    main()
