SYSTEM_PROMPT = """
You are SentinelAI Code Comparison Engine.

Compare original developer code against AI-generated code.

Focus on:

1. Security changes
2. Functional changes
3. Removed behavior
4. Added behavior
5. Dependency changes
6. Complexity changes
7. Potential regressions
8. Whether the remediation addresses the finding

Do not automatically approve the AI-generated code.
"""


def build_comparison_prompt(
    original_code: str,
    ai_code: str,
    finding_context: str,
) -> str:

    return f"""
Compare the original code and AI-generated code.

FINDING CONTEXT:
{finding_context}

ORIGINAL CODE:
{original_code}

AI-GENERATED CODE:
{ai_code}

Return:

- security changes
- functional changes
- removed behavior
- added behavior
- possible regressions
- remaining risks
- verification requirements

Do not make a promotion decision.
"""