from ai.ai_gateway.prompts.review import (
    SYSTEM_PROMPT as REVIEW_SYSTEM_PROMPT,
    build_review_prompt,
)

from ai.ai_gateway.prompts.remediation import (
    SYSTEM_PROMPT as REMEDIATION_SYSTEM_PROMPT,
    build_remediation_prompt,
)

from ai.ai_gateway.prompts.explanation import (
    SYSTEM_PROMPT as EXPLANATION_SYSTEM_PROMPT,
    build_explanation_prompt,
)

from ai.ai_gateway.prompts.comparison import (
    SYSTEM_PROMPT as COMPARISON_SYSTEM_PROMPT,
    build_comparison_prompt,
)


__all__ = [
    "REVIEW_SYSTEM_PROMPT",
    "REMEDIATION_SYSTEM_PROMPT",
    "EXPLANATION_SYSTEM_PROMPT",
    "COMPARISON_SYSTEM_PROMPT",
    "build_review_prompt",
    "build_remediation_prompt",
    "build_explanation_prompt",
    "build_comparison_prompt",
]