import json

from ai.intelligence.risk.finding import RiskFinding


class GitleaksParser:

    def parse(self, raw_output: str) -> list[RiskFinding]:

        if not raw_output:
            return []

        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            return []

        if not isinstance(data, list):
            return []

        findings: list[RiskFinding] = []

        for item in data:

            description = (
                item.get("Description")
                or item.get("description")
                or "Secret detected."
            )

            rule_id = (
                item.get("RuleID")
                or item.get("ruleID")
                or item.get("rule_id")
            )

            file_path = (
                item.get("File")
                or item.get("file")
            )

            line_number = (
                item.get("StartLine")
                or item.get("startLine")
            )

            secret = (
                item.get("Secret")
                or item.get("secret")
            )

            findings.append(
                RiskFinding(
                    source="gitleaks",
                    tool="gitleaks",
                    category="secret",
                    severity="high",
                    message=description,
                    file_path=file_path,
                    line_number=line_number,
                    rule_id=rule_id,
                    evidence=secret,
                    confidence=1.0,
                    metadata={
                        "commit": item.get("Commit"),
                        "author": item.get("Author"),
                        "email": item.get("Email"),
                        "date": item.get("Date"),
                        "entropy": item.get("Entropy"),
                        "match": item.get("Match"),
                    },
                )
            )

        return findings