from __future__ import annotations

import argparse
import sys

from ai.integrations.local_remediation.github_cli import GitHubCLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SentinelAI terminal GitHub lifecycle automation"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------
    # CREATE PR
    # ------------------------------------------------------------
    x = sub.add_parser(
        "create-pr",
        help="Create a pull request from a SentinelAI candidate branch.",
    )
    x.add_argument("--repo", required=True, help="OWNER/REPOSITORY")
    x.add_argument("--head", required=True, help="Candidate branch")
    x.add_argument("--base", default="main", help="Base branch")
    x.add_argument("--title", required=True, help="Pull request title")
    x.add_argument("--body-file", help="Markdown file containing PR description")
    x.add_argument(
        "--draft",
        action="store_true",
        help="Create the pull request as a draft",
    )

    # ------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------
    x = sub.add_parser(
        "status",
        help="Show open SentinelAI pull requests.",
    )
    x.add_argument("--repo", required=True, help="OWNER/REPOSITORY")
    x.add_argument(
        "--head",
        help="Filter by candidate branch",
    )

    # ------------------------------------------------------------
    # CHECKS
    # ------------------------------------------------------------
    x = sub.add_parser(
        "checks",
        help="Show CI/check status for a pull request.",
    )
    x.add_argument("--repo", required=True, help="OWNER/REPOSITORY")
    x.add_argument("--pr", required=True, help="PR number or URL")

    # ------------------------------------------------------------
    # MERGE
    # ------------------------------------------------------------
    x = sub.add_parser(
        "merge",
        help="Merge a pull request from the terminal.",
    )
    x.add_argument("--repo", required=True, help="OWNER/REPOSITORY")
    x.add_argument("--pr", required=True, help="PR number or URL")
    x.add_argument(
        "--method",
        choices=["merge", "squash", "rebase"],
        default="squash",
        help="Merge method",
    )
    x.add_argument(
        "--keep-branch",
        action="store_true",
        help="Do not delete the candidate branch after merge",
    )
    x.add_argument(
        "--no-auto",
        action="store_true",
        help="Do not enable GitHub auto-merge; merge immediately if allowed",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    gh = GitHubCLI()

    if args.command == "create-pr":
        result = gh.create_pr(
            repo=args.repo,
            head=args.head,
            base=args.base,
            title=args.title,
            body_file=args.body_file,
            draft=args.draft,
        )

    elif args.command == "status":
        result = gh.status(
            repo=args.repo,
            head=args.head,
        )

    elif args.command == "checks":
        result = gh.checks(
            repo=args.repo,
            pr=args.pr,
        )

    elif args.command == "merge":
        result = gh.merge(
            repo=args.repo,
            pr=args.pr,
            method=args.method,
            delete_branch=not args.keep_branch,
            auto=not args.no_auto,
        )

    else:
        parser.error(f"Unsupported command: {args.command}")
        return 2

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
