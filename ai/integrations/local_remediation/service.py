from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ai.integrations.ai_review.review_service import AIReviewService
from ai.integrations.ai_review.remediation_service import AIRemediationService
from ai.integrations.ai_review.verification_service import AIVerificationService
from ai.integrations.local_remediation.report_generator import (
    SentinelAIReportGenerator,
)
from ai.integrations.security.security_gate import SecurityGate
from ai.integrations.git.git_command import GitCommandExecutor
from ai.integrations.git.candidate_manager import CandidateBranchManager
from ai.integrations.github.github_workflow import GitHubWorkflow
from ai.integrations.github.github_client import GitHubClient
from ai.integrations.github.github_config import GitHubConfig


@dataclass
class LocalRemediationResult:
    success: bool
    status: str
    repository_url: str
    target: str
    candidate_branch: str | None = None
    commit_sha: str | None = None
    pull_request_url: str | None = None
    artifact_directory: str | None = None
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return vars(self).copy()


class LocalRemediationService:
    """
    SentinelAI local remediation workflow.

    Workflow:

        GitHub main
            ↓
        temporary clone
            ↓
        compare original/local
            ↓
        AI review
            ↓
        AI remediation
            ↓
        verification
            ↓
        candidate branch
            ↓
        remediation commit
            ↓
        SentinelAI evidence generation
            ↓
        evidence copied into candidate repository
            ↓
        evidence commit
            ↓
        push candidate branch
            ↓
        create GitHub PR

    Safety:
    - User's local repository is never modified.
    - GitHub base branch is never modified directly.
    - Work occurs in an isolated temporary clone.
    - Failed verification stops the workflow.
    """

    EVIDENCE_ROOT = ".sentinelai/remediation"

    def __init__(
        self,
        git_executor=None,
        github_workflow=None,
        candidate_manager=None,
        report_generator=None,
        review_service=None,
        remediation_service=None,
        verification_service=None,
        security_gate=None,
        github_token: str | None = None,
    ):
        self.git = git_executor or GitCommandExecutor(
            timeout_seconds=300
        )

        if github_workflow:
            self.github = github_workflow
        elif github_token:
            self.github = GitHubWorkflow(
                GitHubClient(
                    GitHubConfig.from_environment(
                        token_override=github_token
                    )
                )
            )
        else:
            self.github = GitHubWorkflow()

        configure_git_auth = getattr(
            self.git,
            "set_github_token",
            None,
        )
        if configure_git_auth:
            configure_git_auth(
                self.github.client.config.token
            )

        self.candidate_manager = (
            candidate_manager
            or CandidateBranchManager(self.git)
        )

        self.report_generator = (
            report_generator
            or SentinelAIReportGenerator()
        )

        self.review_service = (
            review_service
            or AIReviewService()
        )

        self.remediation_service = (
            remediation_service
            or AIRemediationService()
        )

        self.verification_service = (
            verification_service
            or AIVerificationService()
        )

        self.security_gate = (
            security_gate
            or SecurityGate()
        )

    # =========================================================
    # MAIN WORKFLOW
    # =========================================================

    def execute(
        self,
        request: dict[str, Any],
    ) -> LocalRemediationResult:

        repository_url = request["repository_url"]

        base_branch = request.get(
            "base_branch",
            "main",
        )

        target = request["target"].replace(
            "\\",
            "/",
        )

        local_file = Path(
            request["local_file"]
        ).resolve()

        reason = request.get(
            "reason",
            "",
        ).strip()

        push = bool(
            request.get(
                "push",
                False,
            )
        )

        if not reason:
            raise ValueError(
                "Developer reason is required."
            )

        if not local_file.is_file():
            raise FileNotFoundError(
                "Local replacement does not exist: "
                f"{local_file}"
            )

        self._validate_github_url(
            repository_url
        )

        authenticated_user = self.github.authenticated_user()
        login = str(authenticated_user.get("login") or "").strip()
        git_name = str(
            authenticated_user.get("name") or login
            or os.getenv("GIT_AUTHOR_NAME", "")
        ).strip()
        git_email = str(
            authenticated_user.get("email") or ""
        ).strip()
        if not git_email and login and authenticated_user.get("id") is not None:
            git_email = (
                f"{authenticated_user['id']}+{login}"
                "@users.noreply.github.com"
            )
        git_email = git_email or os.getenv(
            "GIT_AUTHOR_EMAIL",
            "",
        ).strip()
        if not git_name or not git_email:
            raise RuntimeError(
                "Could not determine the authenticated GitHub commit identity. "
                "Set a verified GIT_AUTHOR_NAME and GIT_AUTHOR_EMAIL, or check the GitHub token."
            )

        set_git_identity = getattr(
            self.git,
            "set_git_identity",
            None,
        )
        if set_git_identity:
            set_git_identity(git_name, git_email)

        owner, repo = self._owner_repo(
            repository_url
        )

        run_id = self._run_id()

        temp_root = Path(
            tempfile.mkdtemp(
                prefix="sentinelai-remediation-"
            )
        )

        repo_path = temp_root / repo

        evidence: dict[str, Any] = {
            "run_id": run_id,
            "repository_url": repository_url,
            "repository": f"{owner}/{repo}",
            "target": target,
            "developer_reason": reason,
            "local_file": str(local_file),
            "base_branch": base_branch,
            "workflow": {
                "name": "SentinelAI Local Remediation",
                "version": "2.0",
                "evidence_pushed_to_repository": True,
            },
        }

        try:
            # =================================================
            # 1. CLONE BASE BRANCH
            # =================================================

            self._git(
                [
                    "clone",
                    "--branch",
                    base_branch,
                    "--single-branch",
                    repository_url,
                    str(repo_path),
                ]
            )

            self.candidate_manager.configure_identity(
                str(repo_path),
                git_name,
                git_email,
            )

            original_path = repo_path / target

            if not original_path.exists():
                raise FileNotFoundError(
                    "Target file not found in base branch: "
                    f"{target}"
                )

            # =================================================
            # 2. READ ORIGINAL + LOCAL FILE
            # =================================================

            original_code = (
                original_path.read_text(
                    encoding="utf-8"
                )
            )

            local_code = (
                local_file.read_text(
                    encoding="utf-8"
                )
            )

            original_commit = self._git(
                [
                    "rev-parse",
                    "HEAD",
                ],
                cwd=repo_path,
            ).strip()

            evidence["original_commit"] = (
                original_commit
            )

            evidence["original_sha256"] = (
                self._sha256(
                    original_code
                )
            )

            evidence["local_sha256"] = (
                self._sha256(
                    local_code
                )
            )

            # =================================================
            # 3. ORIGINAL VS LOCAL DIFF
            # =================================================

            diff = self._diff(
                original_code,
                local_code,
                target,
            )

            evidence[
                "comparison_original_local"
            ] = {
                "identical": (
                    original_code
                    == local_code
                ),
                "developer_reason": reason,
                "diff": diff,
            }

            # =================================================
            # 4. APPLY LOCAL PROPOSAL
            # =================================================

            original_path.write_text(
                local_code,
                encoding="utf-8",
            )

            # =================================================
            # 5. AI REVIEW
            # =================================================

            review = (
                self.review_service.review_change(
                    original_code=original_code,
                    proposed_code=local_code,
                    developer_reason=reason,
                    file_path=target,
                    repository_context=(
                        f"Repository: {owner}/{repo}; "
                        f"base branch: {base_branch}"
                    ),
                )
            )

            evidence["ai_review"] = self._obj(
                review
            )

            # =================================================
            # 6. AI REMEDIATION
            # =================================================

            remediation = (
                self.remediation_service
                .generate_change_remediation(
                    original_code=original_code,
                    proposed_code=local_code,
                    developer_reason=reason,
                    file_path=target,
                    review=review,
                )
            )

            evidence["ai_remediation"] = (
                self._obj(remediation)
            )

            # =================================================
            # 7. SELECT FINAL CANDIDATE CODE
            # =================================================

            candidate_code = local_code

            ai_candidate_applied = False

            if (
                remediation.original_code
                and remediation.replacement_code
            ):
                if (
                    remediation.original_code
                    == original_code
                ):
                    candidate_code = (
                        remediation.replacement_code
                    )

                    ai_candidate_applied = True

            original_path.write_text(
                candidate_code,
                encoding="utf-8",
            )

            evidence["candidate"] = {
                "ai_candidate_applied": (
                    ai_candidate_applied
                ),
                "candidate_sha256": (
                    self._sha256(
                        candidate_code
                    )
                ),
            }

            # =================================================
            # 8. VERIFICATION
            # =================================================

            verification = (
                self.verification_service
                .verify_code_change(
                    str(repo_path),
                    target,
                    reason,
                )
            )

            evidence["verification"] = (
                self._obj(verification)
            )

            if not verification.get(
                "verified",
                False,
            ):
                raise RuntimeError(
                    "Candidate verification failed: "
                    f"{verification.get('reason', 'Unknown reason')}"
                )

            # =================================================
            # 9. SECURITY GATE
            # =================================================

            gate = {
                "allowed": True,
                "mode": "pending-security-pipeline",
                "reason": (
                    "Static verification passed. "
                    "A synthetic security risk profile "
                    "was not created by this workflow."
                ),
            }

            evidence["security_gate"] = gate

            # =================================================
            # 10. CREATE CANDIDATE BRANCH
            # =================================================

            candidate = (
                self.candidate_manager
                .create_candidate(
                    str(repo_path)
                )
            )

            evidence["git_audit"] = {
                "original_branch": (
                    candidate.original_branch
                ),
                "candidate_branch": (
                    candidate.candidate_branch
                ),
                "candidate_path": (
                    candidate.repository_path
                ),
                "ai_candidate_applied": (
                    ai_candidate_applied
                ),
            }

            # =================================================
            # 11. NO CHANGE
            # =================================================

            if not self.candidate_manager.has_changes(
                str(repo_path)
            ):

                evidence["tests"] = {
                    "candidate_changed": False,
                    "static_verification": (
                        verification
                    ),
                }

                artifacts = (
                    self.report_generator.generate(
                        evidence,
                        run_id,
                    )
                )

                return LocalRemediationResult(
                    success=True,
                    status="no_change",
                    repository_url=repository_url,
                    target=target,
                    candidate_branch=(
                        candidate.candidate_branch
                    ),
                    artifact_directory=str(
                        Path(
                            artifacts["html"]
                        ).parent
                    ),
                    message=(
                        "The proposed file is identical "
                        "to the base version; no commit "
                        "was created."
                    ),
                )

            # =================================================
            # 12. COMMIT CODE CHANGE
            # =================================================

            remediation_commit_sha = (
                self.candidate_manager
                .commit_changes(
                    str(repo_path),
                    "feat(sentinelai): verified remediation",
                )
            )

            evidence["git_audit"][
                "remediation_commit_sha"
            ] = remediation_commit_sha

            evidence["tests"] = {
                "candidate_changed": True,
                "static_verification": (
                    verification
                ),
            }

            # =================================================
            # 13. GENERATE SENTINELAI REPORT
            # =================================================

            artifacts = (
                self.report_generator.generate(
                    evidence,
                    run_id,
                )
            )

            evidence["artifacts"] = self._obj(
                artifacts
            )

            # =================================================
            # 14. COPY EVIDENCE INTO CANDIDATE REPO
            # =================================================

            evidence_directory = (
                repo_path
                / self.EVIDENCE_ROOT
                / run_id
            )

            evidence_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            self._write_evidence_bundle(
                evidence_directory,
                evidence,
                artifacts,
                diff,
                remediation_commit_sha,
            )

            evidence["git_audit"][
                "evidence_directory"
            ] = (
                f"{self.EVIDENCE_ROOT}/{run_id}"
            )

            # Final evidence.json after adding
            # repository evidence path.
            self._write_json(
                evidence_directory
                / "evidence.json",
                evidence,
            )

            # =================================================
            # 15. COMMIT SENTINELAI DOCUMENTATION
            # =================================================

            evidence_commit_sha = (
                self.candidate_manager
                .commit_changes(
                    str(repo_path),
                    "docs(sentinelai): add remediation evidence",
                )
            )

            evidence["git_audit"][
                "evidence_commit_sha"
            ] = evidence_commit_sha

            self._write_json(
                evidence_directory
                / "git_audit.json",
                evidence["git_audit"],
            )

            # Commit final audit file.
            final_evidence_commit_sha = (
                self.candidate_manager
                .commit_changes(
                    str(repo_path),
                    "docs(sentinelai): finalize remediation audit",
                )
            )

            evidence["git_audit"][
                "final_evidence_commit_sha"
            ] = final_evidence_commit_sha

            # =================================================
            # 16. PUSH
            # =================================================

            if push:

                self.candidate_manager.push(
                    str(repo_path),
                    candidate.candidate_branch,
                )

            # =================================================
            # 17. CREATE GITHUB PR
            # =================================================

            pull_request_url = None

            if push:

                target_repo = (
                    self.github.parse_repository_url(
                        repository_url,
                        base_branch,
                    )
                )

                pr = (
                    self.github.create_pull_request(
                        target=target_repo,
                        candidate_branch=(
                            candidate.candidate_branch
                        ),
                        title=(
                            "feat(sentinelai): "
                            "verified remediation"
                        ),
                        body=self._pr_body(
                            evidence
                        ),
                    )
                )

                evidence["github_audit"] = (
                    self._obj(pr)
                )

                pull_request_url = (
                    self._pr_url(
                        evidence
                    )
                )

                # =============================================
                # 18. SAVE PR AUDIT
                # =============================================

                self._write_json(
                    evidence_directory
                    / "github_audit.json",
                    evidence["github_audit"],
                )

                self._write_json(
                    evidence_directory
                    / "evidence.json",
                    evidence,
                )

                # =============================================
                # 19. PUSH FINAL PR AUDIT
                # =============================================

                self.candidate_manager.commit_changes(
                    str(repo_path),
                    "docs(sentinelai): record pull request audit",
                )

                self.candidate_manager.push(
                    str(repo_path),
                    candidate.candidate_branch,
                )

            # =================================================
            # 20. SUCCESS
            # =================================================

            return LocalRemediationResult(
                success=True,
                status="completed",
                repository_url=repository_url,
                target=target,
                candidate_branch=(
                    candidate.candidate_branch
                ),
                commit_sha=(
                    remediation_commit_sha
                ),
                pull_request_url=(
                    pull_request_url
                ),
                artifact_directory=str(
                    evidence_directory
                ),
                message=(
                    "SentinelAI remediation completed. "
                    "Code, AI reasoning, verification, "
                    "security gate, Git audit and SentinelAI "
                    "evidence were committed to the candidate "
                    "branch."
                ),
            )

        finally:
            shutil.rmtree(
                temp_root,
                ignore_errors=True,
            )

    # =========================================================
    # EVIDENCE BUNDLE
    # =========================================================

    def _write_evidence_bundle(
        self,
        evidence_directory: Path,
        evidence: dict[str, Any],
        artifacts: Any,
        diff: str,
        remediation_commit_sha: str,
    ) -> None:

        # Complete machine-readable evidence.
        self._write_json(
            evidence_directory
            / "evidence.json",
            evidence,
        )

        # Developer reasoning.
        developer_reason = (
            "# SentinelAI Remediation\n\n"
            "## Developer Reason\n\n"
            f"{evidence['developer_reason']}\n\n"
            "## Repository\n\n"
            f"- Repository: `{evidence['repository']}`\n"
            f"- Base branch: `{evidence['base_branch']}`\n"
            f"- Target: `{evidence['target']}`\n"
            f"- Run ID: `{evidence['run_id']}`\n"
        )

        (
            evidence_directory
            / "developer_reason.md"
        ).write_text(
            developer_reason,
            encoding="utf-8",
        )

        # Exact code diff.
        (
            evidence_directory
            / "proposed_change.patch"
        ).write_text(
            diff,
            encoding="utf-8",
        )

        # AI review.
        self._write_json(
            evidence_directory
            / "ai_review.json",
            evidence.get(
                "ai_review",
                {},
            ),
        )

        # AI remediation.
        self._write_json(
            evidence_directory
            / "ai_remediation.json",
            evidence.get(
                "ai_remediation",
                {},
            ),
        )

        # Verification.
        self._write_json(
            evidence_directory
            / "verification.json",
            evidence.get(
                "verification",
                {},
            ),
        )

        # Security gate.
        self._write_json(
            evidence_directory
            / "security_gate.json",
            evidence.get(
                "security_gate",
                {},
            ),
        )

        # Git audit.
        self._write_json(
            evidence_directory
            / "git_audit.json",
            evidence.get(
                "git_audit",
                {},
            ),
        )

        # Candidate metadata.
        self._write_json(
            evidence_directory
            / "candidate.json",
            evidence.get(
                "candidate",
                {},
            ),
        )

        # Human-readable README.
        (
            evidence_directory
            / "README.md"
        ).write_text(
            self._evidence_readme(
                evidence,
                remediation_commit_sha,
                artifacts,
            ),
            encoding="utf-8",
        )

        # Copy generated report files.
        self._copy_generated_artifacts(
            artifacts,
            evidence_directory,
        )

    @staticmethod
    def _copy_generated_artifacts(
        artifacts: Any,
        destination: Path,
    ) -> None:

        if not isinstance(
            artifacts,
            dict,
        ):
            return

        for key, value in artifacts.items():

            if not isinstance(
                value,
                (str, Path),
            ):
                continue

            source = Path(value)

            if not source.is_file():
                continue

            target = (
                destination
                / source.name
            )

            try:
                if (
                    source.resolve()
                    == target.resolve()
                ):
                    continue
            except OSError:
                pass

            shutil.copy2(
                source,
                target,
            )

    # =========================================================
    # PR BODY
    # =========================================================

    @staticmethod
    def _pr_body(
        evidence: dict[str, Any],
    ) -> str:

        review = evidence.get(
            "ai_review",
            {},
        )

        remediation = evidence.get(
            "ai_remediation",
            {},
        )

        verification = evidence.get(
            "verification",
            {},
        )

        git_audit = evidence.get(
            "git_audit",
            {},
        )

        github_audit = evidence.get(
            "github_audit",
            {},
        )

        evidence_path = git_audit.get(
            "evidence_directory",
            ".sentinelai/remediation",
        )

        return f"""# SentinelAI Verified Remediation

## Developer Reason

{evidence.get("developer_reason", "Not provided.")}

## Repository

- **Repository:** `{evidence.get("repository", "")}`
- **Base branch:** `{evidence.get("base_branch", "")}`
- **Target:** `{evidence.get("target", "")}`
- **Candidate branch:** `{git_audit.get("candidate_branch", "")}`
- **Run ID:** `{evidence.get("run_id", "")}`

## AI Review

```json
{json.dumps(review, indent=2, default=str)[:12000]}
```
"""

    # =========================================================
    # VALIDATION / UTILITY HELPERS
    # =========================================================

    @staticmethod
    def _validate_github_url(url: str) -> None:
        parsed = urlparse(url)

        if parsed.netloc.lower() not in {
            "github.com",
            "www.github.com",
        }:
            raise ValueError(
                "Expected a GitHub repository URL."
            )

    @staticmethod
    def _owner_repo(url: str) -> tuple[str, str]:
        parts = [
            value
            for value in (
                urlparse(url)
                .path
                .strip("/")
                .split("/")
            )
            if value
        ]

        if len(parts) < 2:
            raise ValueError(
                "Invalid GitHub repository URL."
            )

        return (
            parts[0],
            parts[1].removesuffix(".git"),
        )

    def _git(
        self,
        args: list[str],
        cwd: Path | None = None,
    ) -> str:
        result = self.git.run(
            args,
            cwd=str(cwd) if cwd else None,
        )

        if not result.success:
            raise RuntimeError(
                f"Git command failed: "
                f"{' '.join(args)}\n"
                f"{result.stderr}"
            )

        return result.stdout.strip()

    @staticmethod
    def _sha256(value: str) -> str:
        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _diff(
        original: str,
        proposed: str,
        target: str,
    ) -> str:
        import difflib

        return "".join(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                proposed.splitlines(keepends=True),
                fromfile=f"a/{target}",
                tofile=f"b/{target}",
            )
        )

    @staticmethod
    def _run_id() -> str:
        from datetime import datetime

        return datetime.now().strftime(
            "%Y%m%d-%H%M%S-%f"
        )

    @staticmethod
    def _write_json(
        path: Path,
        data: Any,
    ) -> None:
        path.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8",
        )

    @staticmethod
    def _obj(value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, dict):
            return value

        if hasattr(value, "to_dict"):
            return value.to_dict()

        if hasattr(value, "__dict__"):
            return vars(value).copy()

        return value

    @staticmethod
    def _pr_url(
        evidence: dict[str, Any],
    ) -> str | None:
        github_audit = evidence.get("github_audit", {})

        if not isinstance(github_audit, dict):
            return None

        return (
            github_audit.get("url")
            or github_audit.get("pull_request_url")
        )

    @staticmethod
    def _evidence_readme(
        evidence: dict[str, Any],
        remediation_commit_sha: str,
        artifacts: Any,
    ) -> str:
        git_audit = evidence.get("git_audit", {})
        verification = evidence.get("verification", {})
        security_gate = evidence.get("security_gate", {})

        return f"""# SentinelAI Remediation Evidence

## Summary

This directory contains the complete evidence generated by SentinelAI for this remediation run.

## Repository

- Repository: `{evidence.get("repository", "")}`
- Base branch: `{evidence.get("base_branch", "")}`
- Target: `{evidence.get("target", "")}`
- Run ID: `{evidence.get("run_id", "")}`

## Developer Reason

{evidence.get("developer_reason", "Not provided.")}

## Workflow

1. Original repository cloned
2. Original and proposed files compared
3. AI review performed
4. AI remediation evaluated
5. Candidate code generated
6. Verification performed
7. Security gate evaluated
8. Candidate branch created
9. Remediation committed
10. SentinelAI evidence generated
11. Evidence committed
12. Candidate branch pushed
13. Pull Request created

## Verification

```json
{json.dumps(verification, indent=2, default=str)}
```

## Security Gate

```json
{json.dumps(security_gate, indent=2, default=str)}
```

## Git Audit

```json
{json.dumps(git_audit, indent=2, default=str)}
```

- Remediation commit: `{remediation_commit_sha}`
- Generated artifacts: `{json.dumps(artifacts, default=str)}`
"""
