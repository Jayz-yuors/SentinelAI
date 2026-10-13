from __future__ import annotations
import shutil
import subprocess
from dataclasses import dataclass

@dataclass
class GitHubCLIResult:
    success: bool
    stdout: str
    stderr: str
    returncode: int

class GitHubCLI:
    """Terminal-native PR/check/merge automation using the official gh CLI."""

    def __init__(self, executable: str = "gh"):
        self.executable = shutil.which(executable) or executable

    def run(self, args: list[str]) -> GitHubCLIResult:
        p = subprocess.run([self.executable, *args], capture_output=True, text=True)
        return GitHubCLIResult(p.returncode == 0, p.stdout.strip(), p.stderr.strip(), p.returncode)

    def create_pr(self, repo, head, base, title, body_file=None, draft=False):
        args=["pr","create","--repo",repo,"--head",head,"--base",base,"--title",title]
        args += ["--body-file",body_file] if body_file else ["--body","SentinelAI verified remediation candidate."]
        if draft: args.append("--draft")
        return self.run(args)

    def status(self, repo, head=None):
        args=["pr","list","--repo",repo,"--state","open","--json","number,title,url,headRefName,baseRefName,state,statusCheckRollup"]
        if head: args += ["--head",head]
        return self.run(args)

    def checks(self, repo, pr):
        return self.run(["pr","checks",pr,"--repo",repo])

    def merge(self, repo, pr, method="squash", delete_branch=True, auto=True):
        if method not in {"merge","squash","rebase"}:
            raise ValueError("method must be merge, squash, or rebase")
        args=["pr","merge",pr,"--repo",repo,f"--{method}"]
        if delete_branch: args.append("--delete-branch")
        if auto: args.append("--auto")
        return self.run(args)
