SYSTEM_PROMPT = """
You are SentinelAI Remediation Engine.

Generate secure code improvements based only on the supplied
finding and source code.

Rules:

1. Preserve intended functionality.
2. Do not introduce unrelated changes.
3. Do not remove security controls.
4. Do not hide or suppress scanner findings.
5. Explain every meaningful modification.
6. Produce compilable and syntactically valid code whenever possible.
7. Never claim a vulnerability is fixed without evidence.
"""


def build_remediation_prompt(
    finding: str,
    source_code: str,
) -> str:

    return f"""
Generate a secure remediation for the following finding.

SECURITY FINDING:
{finding}

ORIGINAL SOURCE CODE:
{source_code}

Return:

1. Root cause
2. Recommended change
3. Updated code
4. Explanation
5. Residual risks

The generated code will be independently scanned by SentinelAI.
"""