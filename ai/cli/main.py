from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def print_json(data):
    print(
        json.dumps(
            data,
            indent=2,
            default=str,
        )
    )


# ============================================================
# EXISTING COMMANDS
# ============================================================

def command_scan(args):

    from ai.integrations.security.security_pipeline import (
        SecurityPipeline,
    )

    pipeline = SecurityPipeline()

    result = pipeline.run(
        str(
            Path(args.path).resolve()
        )
    )

    if hasattr(result, "to_dict"):
        result = result.to_dict()

    print_json(result)


def command_gate(args):

    from ai.integrations.security.security_pipeline import (
        SecurityPipeline,
    )

    from ai.integrations.security.security_gate import (
        SecurityGate,
    )

    pipeline = SecurityPipeline()

    profile = pipeline.run(
        str(
            Path(args.path).resolve()
        )
    )

    gate = SecurityGate()

    result = gate.evaluate(
        profile
    )

    print_json(
        result.to_dict()
    )

    if not result.allowed:
        sys.exit(2)


def command_github_check(args):

    from ai.integrations.github.github_workflow import (
        GitHubWorkflow,
    )

    workflow = GitHubWorkflow()

    target = workflow.parse_repository_url(
        args.repository,
        args.branch,
    )

    result = workflow.verify_access(
        target
    )

    print_json(result)


def command_github_branch(args):

    from ai.integrations.github.github_workflow import (
        GitHubWorkflow,
    )

    workflow = GitHubWorkflow()

    target = workflow.parse_repository_url(
        args.repository,
        args.base,
    )

    result = workflow.create_remote_branch(
        target,
        args.candidate,
    )

    if hasattr(result, "data"):
        result = result.data

    print_json(result)


def command_github_pr(args):

    from ai.integrations.github.github_workflow import (
        GitHubWorkflow,
    )

    workflow = GitHubWorkflow()

    target = workflow.parse_repository_url(
        args.repository,
        args.base,
    )

    result = workflow.create_pull_request(
        target=target,
        candidate_branch=args.candidate,
        title=args.title,
        body=args.body,
    )

    if hasattr(result, "__dict__"):
        result = result.__dict__

    print_json(result)


# ============================================================
# LOCAL REMEDIATION
# ============================================================

def command_remediate_local(args):
    """
    Entry point for the SentinelAI developer-update workflow.

    The important contract is:

        repository_url
        target
        local_file
        reason
        base_branch
        push

    The `reason` is deliberately preserved as first-class
    analysis context. It is NOT merely a CLI display value.

    The eventual remediation workflow must pass this context
    to:

        - AI review
        - AI remediation
        - AI verification
        - risk comparison
        - documentation
        - Git commit / PR evidence
    """

    local_file = Path(args.local_file).resolve()

    if not local_file.exists():
        raise FileNotFoundError(
            f"Local replacement file does not exist: {local_file}"
        )

    if not local_file.is_file():
        raise ValueError(
            f"Local replacement path is not a file: {local_file}"
        )

    if not args.reason.strip():
        raise ValueError(
            "Update reason cannot be empty."
        )

    if not args.repository_url.strip():
        raise ValueError(
            "GitHub repository URL cannot be empty."
        )

    if not args.target.strip():
        raise ValueError(
            "Target file cannot be empty."
        )

    # --------------------------------------------------------
    # Build the complete request context.
    # --------------------------------------------------------
    #
    # This object is intentionally structured so the actual
    # remediation service can pass the same information to
    # every downstream stage.
    #

    remediation_request = {
        "request_type": "local_file_remediation",

        "repository_url": args.repository_url,

        "base_branch": args.base_branch,

        "target": args.target.replace("\\", "/"),

        "local_file": str(local_file),

        "reason": args.reason,

        "push": bool(args.push),

        "analysis_context": {
            "developer_reason": args.reason,

            "requested_change": (
                f"Evaluate the developer supplied replacement "
                f"for {args.target.replace(chr(92), '/')}"
            ),

            "comparison_required": [
                "original_vs_local",
                "local_vs_ai",
                "before_vs_after_risk",
            ],

            "required_ai_stages": [
                "review",
                "remediation",
                "verification",
            ],

            "required_security_stages": [
                "initial_scan",
                "post_remediation_scan",
                "risk_comparison",
                "security_gate",
            ],

            "required_git_stages": [
                "preserve_main",
                "create_candidate_branch",
                "commit_verified_change",
            ],

            "required_github_stages": [
                "push_candidate_branch",
                "create_pull_request",
            ],

            "documentation_requirements": [
                "developer_reason",
                "original_vs_local_comparison",
                "ai_review",
                "ai_remediation",
                "local_vs_ai_comparison",
                "verification",
                "security_results",
                "risk_before",
                "risk_after",
                "risk_comparison",
                "security_gate",
                "git_audit",
                "github_audit",
            ],
        },
    }

    # --------------------------------------------------------
    # Print request information.
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("SENTINELAI — LOCAL REMEDIATION REQUEST")
    print("=" * 60)

    print()
    print("Repository:")
    print(args.repository_url)

    print()
    print("Base branch:")
    print(args.base_branch)

    print()
    print("Target:")
    print(args.target)

    print()
    print("Local replacement:")
    print(local_file)

    print()
    print("Developer reason:")
    print(args.reason)

    print()
    print("Push enabled:")
    print(bool(args.push))

    print()
    print("=" * 60)
    print("AI CONTEXT")
    print("=" * 60)

    print()
    print(
        "The developer reason will be supplied to the "
        "AI review/remediation/verification workflow."
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # This is the integration boundary.
    #
    # We deliberately do not fake an AI result here.
    #
    # The actual LocalRemediationService must consume
    # `remediation_request`.
    # --------------------------------------------------------

    try:

        from ai.integrations.local_remediation.service import (
            LocalRemediationService,
        )

    except ImportError as exc:

        print()
        print(
            "[ERROR] LocalRemediationService is not implemented yet."
        )

        print()
        print(
            "The CLI contract is now ready, but the actual "
            "remediation orchestrator still needs to be wired "
            "to GitHub, AI Gateway, security, risk, verification "
            "and documentation."
        )

        print()
        print(
            "Expected module:"
        )

        print(
            "ai.integrations.local_remediation.service"
        )

        print()
        print(
            "Expected class:"
        )

        print(
            "LocalRemediationService"
        )

        raise RuntimeError(
            "LocalRemediationService is not implemented."
        ) from exc

    # --------------------------------------------------------
    # Execute the real workflow once the service exists.
    # --------------------------------------------------------

    service = LocalRemediationService()

    result = service.execute(
        remediation_request
    )

    if hasattr(result, "to_dict"):
        result = result.to_dict()

    print()
    print("=" * 60)
    print("SENTINELAI — LOCAL REMEDIATION RESULT")
    print("=" * 60)

    print_json(result)


# ============================================================
# ARGUMENT PARSER
# ============================================================

def build_parser():

    parser = argparse.ArgumentParser(
        prog="sentinelai",
        description=(
            "SentinelAI DevSecOps command line interface"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # --------------------------------------------------------
    # scan
    # --------------------------------------------------------

    scan = subparsers.add_parser(
        "scan"
    )

    scan.add_argument(
        "path"
    )

    scan.set_defaults(
        func=command_scan
    )

    # --------------------------------------------------------
    # gate
    # --------------------------------------------------------

    gate = subparsers.add_parser(
        "gate"
    )

    gate.add_argument(
        "path"
    )

    gate.set_defaults(
        func=command_gate
    )

    # --------------------------------------------------------
    # github-check
    # --------------------------------------------------------

    github_check = subparsers.add_parser(
        "github-check"
    )

    github_check.add_argument(
        "repository"
    )

    github_check.add_argument(
        "--branch",
        default=None,
    )

    github_check.set_defaults(
        func=command_github_check
    )

    # --------------------------------------------------------
    # github-create-branch
    # --------------------------------------------------------

    github_branch = subparsers.add_parser(
        "github-create-branch"
    )

    github_branch.add_argument(
        "repository"
    )

    github_branch.add_argument(
        "candidate"
    )

    github_branch.add_argument(
        "--base",
        default=None,
    )

    github_branch.set_defaults(
        func=command_github_branch
    )

    # --------------------------------------------------------
    # github-pr
    # --------------------------------------------------------

    github_pr = subparsers.add_parser(
        "github-pr"
    )

    github_pr.add_argument(
        "repository"
    )

    github_pr.add_argument(
        "candidate"
    )

    github_pr.add_argument(
        "--base",
        default=None,
    )

    github_pr.add_argument(
        "--title",
        required=True,
    )

    github_pr.add_argument(
        "--body",
        required=True,
    )

    github_pr.set_defaults(
        func=command_github_pr
    )

    # --------------------------------------------------------
    # remediate-local
    # --------------------------------------------------------

    remediate = subparsers.add_parser(
        "remediate-local",
        help=(
            "Evaluate a developer supplied local file against "
            "a GitHub repository and run SentinelAI remediation."
        ),
    )

    remediate.add_argument(
        "--repository-url",
        required=True,
        help="GitHub repository URL.",
    )

    remediate.add_argument(
        "--target",
        required=True,
        help=(
            "Repository-relative target file, for example "
            "Stocks_predictor/calculations.py."
        ),
    )

    remediate.add_argument(
        "--local-file",
        required=True,
        help="Absolute path to the developer's replacement file.",
    )

    remediate.add_argument(
        "--reason",
        required=True,
        help=(
            "Developer's reason for proposing the update. "
            "This becomes AI analysis context."
        ),
    )

    remediate.add_argument(
        "--base-branch",
        default="main",
        help="Base Git branch. Defaults to main.",
    )

    remediate.add_argument(
        "--push",
        action="store_true",
        help=(
            "Allow the verified candidate branch to be "
            "pushed to GitHub."
        ),
    )

    remediate.set_defaults(
        func=command_remediate_local
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main():

    parser = build_parser()

    args = parser.parse_args()

    try:

        args.func(args)

    except KeyboardInterrupt:

        print(
            "\nSENTINELAI: Operation cancelled by user.",
            file=sys.stderr,
        )

        sys.exit(130)

    except Exception as exc:

        print(
            f"SENTINELAI ERROR: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()