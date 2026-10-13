import json
from typing import Any

from ai.ai_gateway.ai_gateway import AIGateway

from .review_models import CodeReviewFinding, CodeReviewResult


class AIReviewService:
    """AI review service for both security findings and developer-proposed changes."""

    def __init__(self, gateway: AIGateway | None = None):
        self.gateway = gateway or AIGateway()

    def review_change(
        self,
        original_code: str,
        proposed_code: str,
        developer_reason: str,
        file_path: str,
        repository_context: str = "",
    ) -> CodeReviewResult:
        """Review ORIGINAL -> PROPOSED as a software change, not only as a security finding."""

        prompt = f"""
You are SentinelAI's senior code-review engine.

Developer reason:
{developer_reason}

Target file:
{file_path}

Repository context:
{repository_context}

ORIGINAL CODE:
{original_code}

PROPOSED LOCAL CODE:
{proposed_code}

Evaluate the proposed change against the original.

Return ONLY valid JSON:
{{
  "summary": "...",
  "findings": [
    {{
      "finding_id": "change-review-1",
      "severity": "info|low|medium|high|critical",
      "title": "...",
      "explanation": "...",
      "file_path": "{file_path}",
      "line_number": null,
      "recommendation": "...",
      "confidence": 0.0
    }}
  ]
}}

Discuss:
1. Whether the proposal satisfies the developer reason.
2. Functional/architectural impact.
3. Compatibility/regression risks.
4. Security implications.
5. Maintainability and unnecessary changes.
6. Testing/verification requirements.

Do not claim that a test passed unless the supplied evidence proves it.
"""

        result = self.gateway.generate(prompt=prompt)

        if not result.success:
            raise RuntimeError(
                f"AI review failed: "
                f"{result.error or 'Unknown provider error'}"
            )

        return self._result_from_text(
            result.content or "",
            result,
        )

    def review_findings(
        self,
        findings: list[Any],
        repository_context: str = "",
    ) -> CodeReviewResult:
        findings_payload = []

        for finding in findings:
            findings_payload.append(
                {
                    "finding_id": getattr(finding, "fingerprint", None)
                    or getattr(finding, "rule_id", "unknown"),
                    "source": getattr(finding, "source", None),
                    "rule_id": getattr(finding, "rule_id", None),
                    "severity": getattr(finding, "severity", None),
                    "title": getattr(finding, "title", None),
                    "message": getattr(finding, "message", None),
                    "file_path": getattr(finding, "file_path", None),
                    "line_number": getattr(finding, "line_number", None),
                }
            )

        prompt = f"""
You are SentinelAI's secure code review engine.

Repository context:
{repository_context}

Findings:
{json.dumps(findings_payload, indent=2)}

For every finding determine:
1. Whether the finding appears actionable.
2. Why it is a security concern.
3. What code change is recommended.
4. Confidence from 0 to 1.

Return ONLY valid JSON:
{{
  "summary": "...",
  "findings": [
    {{
      "finding_id": "...",
      "severity": "...",
      "title": "...",
      "explanation": "...",
      "file_path": "...",
      "line_number": null,
      "recommendation": "...",
      "confidence": 0.0
    }}
  ]
}}
"""

        result = self.gateway.generate(prompt=prompt)

        if not result.success:
            raise RuntimeError(
                f"AI security review failed: "
                f"{result.error or 'Unknown provider error'}"
            )

        return self._result_from_text(
            result.content or "",
            result,
        )

    def _result_from_text(
        self,
        text: str,
        result: Any,
    ) -> CodeReviewResult:
        parsed = self._parse_json(text)

        findings_result = []

        for item in parsed.get("findings", []):
            findings_result.append(
                CodeReviewFinding(
                    finding_id=str(
                        item.get("finding_id", "unknown")
                    ),
                    severity=str(
                        item.get("severity", "medium")
                    ),
                    title=str(
                        item.get("title", "")
                    ),
                    explanation=str(
                        item.get("explanation", "")
                    ),
                    file_path=item.get("file_path"),
                    line_number=item.get("line_number"),
                    recommendation=item.get("recommendation"),
                    confidence=self._float_or_none(
                        item.get("confidence")
                    ),
                )
            )

        return CodeReviewResult(
            summary=str(
                parsed.get("summary", "")
            ),
            findings=findings_result,
            provider=getattr(
                result,
                "provider",
                None,
            ),
            model=getattr(
                result,
                "model",
                None,
            ),
            raw_response=text,
        )

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = text.strip()

        if text.startswith("```"):
            text = text.replace(
                "```json",
                "",
                1,
            ).replace(
                "```",
                "",
            ).strip()

        try:
            value = json.loads(text)

            return (
                value
                if isinstance(value, dict)
                else {}
            )

        except json.JSONDecodeError:
            return {
                "summary": "AI response could not be parsed.",
                "findings": [],
            }

    @staticmethod
    def _float_or_none(
        value: Any,
    ) -> float | None:
        try:
            return (
                None
                if value is None
                else float(value)
            )

        except (TypeError, ValueError):
            return None