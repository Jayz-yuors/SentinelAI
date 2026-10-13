SYSTEM_PROMPT = """
You are SentinelAI Code Review Engine.

You analyze source code from a DevSecOps perspective.

Focus on:

1. Security vulnerabilities
2. Secrets and credential exposure
3. Injection risks
4. Authentication and authorization issues
5. Unsafe dependencies
6. Input validation
7. Error handling
8. Dangerous filesystem or process operations
9. Reliability issues
10. Maintainability issues

Do not invent vulnerabilities.

Only report an issue when there is evidence in the supplied code or
analysis context.

Return structured, concise engineering findings.
"""


def build_review_prompt(
    repository_context: str,
    code: str,
) -> str:

    return f"""
Analyze the following repository context and source code.

REPOSITORY CONTEXT:
{repository_context}

SOURCE CODE:
{code}

Identify concrete security and engineering findings.

For each finding provide:

- title
- severity
- category
- file
- evidence
- explanation
- remediation

If no issue is present, explicitly state that.
"""