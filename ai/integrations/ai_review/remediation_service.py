import json
from pathlib import Path
from typing import Any

from ai.ai_gateway.ai_gateway import AIGateway

from .review_models import CodeReviewFinding, RemediationProposal


class AIRemediationService:
    """Generate security remediation or a developer-requested code-change proposal."""

    def __init__(self, gateway: AIGateway | None = None):
        self.gateway = gateway or AIGateway()

    def generate_change_remediation(
        self,
        original_code: str,
        proposed_code: str,
        developer_reason: str,
        file_path: str,
        review: Any,
    ) -> RemediationProposal:

        prompt = f"""
You are SentinelAI's code-change remediation engine.

Developer reason:
{developer_reason}

Target file:
{file_path}

AI review:
{json.dumps(
    self._obj(review),
    indent=2,
    default=str,
)}

ORIGINAL CODE:
{original_code}

DEVELOPER PROPOSED CODE:
{proposed_code}

Determine whether the developer proposal should be preserved
or whether a safer corrected candidate should be generated.

Rules:
- Preserve the developer's intended functionality.
- Do not invent unrelated functionality.
- Do not remove security controls.
- Do not invent dependencies without explaining them.
- Keep changes minimal where possible.
- Return ONLY JSON.

Format:
{{
  "explanation": "...",
  "original_code": "...",
  "replacement_code": "...",
  "patch": "...",
  "confidence": 0.0
}}

If the developer proposal is already appropriate,
return it as replacement_code.
"""

        result = self.gateway.generate(prompt=prompt)

        if not result.success:
            raise RuntimeError(
                f"AI remediation failed: "
                f"{result.error or 'Unknown provider error'}"
            )

        data = self._parse_json(
            result.content or ""
        )

        return RemediationProposal(
            finding_id="developer-change",
            file_path=file_path,
            explanation=str(
                data.get(
                    "explanation",
                    "",
                )
            ),
            original_code=str(
                data.get(
                    "original_code",
                    original_code,
                )
            ),
            replacement_code=str(
                data.get(
                    "replacement_code",
                    proposed_code,
                )
            ),
            patch=str(
                data.get(
                    "patch",
                    "",
                )
            ),
            confidence=self._float_or_none(
                data.get("confidence")
            ),
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
        )

    def generate_remediation(
        self,
        finding: CodeReviewFinding,
        source_code: str,
    ) -> RemediationProposal:

        prompt = f"""
You are SentinelAI's secure remediation engine.

Security finding:
{json.dumps(
    {
        "finding_id": finding.finding_id,
        "severity": finding.severity,
        "title": finding.title,
        "explanation": finding.explanation,
        "recommendation": finding.recommendation,
        "file_path": finding.file_path,
        "line_number": finding.line_number,
    },
    indent=2,
)}

Current source code:
{source_code}

Generate a minimal secure remediation.

Return ONLY JSON:
{{
  "explanation": "...",
  "original_code": "...",
  "replacement_code": "...",
  "patch": "...",
  "confidence": 0.0
}}
"""

        result = self.gateway.generate(prompt=prompt)

        if not result.success:
            raise RuntimeError(
                f"AI security remediation failed: "
                f"{result.error or 'Unknown provider error'}"
            )

        data = self._parse_json(
            result.content or ""
        )

        return RemediationProposal(
            finding_id=finding.finding_id,
            file_path=finding.file_path or "",
            explanation=str(
                data.get(
                    "explanation",
                    "",
                )
            ),
            original_code=str(
                data.get(
                    "original_code",
                    "",
                )
            ),
            replacement_code=str(
                data.get(
                    "replacement_code",
                    "",
                )
            ),
            patch=str(
                data.get(
                    "patch",
                    "",
                )
            ),
            confidence=self._float_or_none(
                data.get("confidence")
            ),
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
        )

    def apply_proposal(
        self,
        repository_path: str,
        proposal: RemediationProposal,
    ) -> Path:

        if not proposal.file_path:
            raise ValueError(
                "Remediation proposal has no file path."
            )

        repository = Path(
            repository_path
        ).resolve()

        file_path = (
            repository / proposal.file_path
        ).resolve()

        if not str(file_path).startswith(
            str(repository)
        ):
            raise ValueError(
                "Remediation file escapes repository."
            )

        if not file_path.exists():
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        current = file_path.read_text(
            encoding="utf-8"
        )

        if proposal.original_code not in current:
            raise ValueError(
                "Original code was not found. "
                "Refusing unsafe remediation."
            )

        file_path.write_text(
            current.replace(
                proposal.original_code,
                proposal.replacement_code,
                1,
            ),
            encoding="utf-8",
        )

        return file_path

    @staticmethod
    def _obj(value):
        if hasattr(value, "to_dict"):
            return value.to_dict()

        if hasattr(value, "__dict__"):
            return vars(value)

        return value

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
            data = json.loads(text)

            return (
                data
                if isinstance(data, dict)
                else {}
            )

        except json.JSONDecodeError:
            return {}

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