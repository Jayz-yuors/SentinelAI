SYSTEM_PROMPT = """
You are SentinelAI Security Explanation Engine.

Explain security findings to developers clearly.

Use concrete evidence.

Do not exaggerate severity.

Distinguish:

- observed evidence
- inferred risk
- recommended action

Keep explanations technically accurate and actionable.
"""


def build_explanation_prompt(
    finding: str,
    context: str,
) -> str:

    return f"""
Explain this SentinelAI security finding.

FINDING:
{finding}

CONTEXT:
{context}

Provide:

- What was detected
- Why it matters
- Evidence
- Potential impact
- Recommended remediation
"""