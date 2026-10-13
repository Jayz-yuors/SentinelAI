from pathlib import Path
import subprocess

def git_diff(repository: Path, base: str = "HEAD") -> str:
    r = subprocess.run(["git","diff",base,"--"], cwd=repository, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "git diff failed")
    return r.stdout

def changed_files(repository: Path) -> list[dict]:
    r = subprocess.run(["git","status","--porcelain"], cwd=repository, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "git status failed")
    result=[]
    for line in r.stdout.splitlines():
        if len(line) >= 4:
            result.append({"status": line[:2].strip(), "path": line[3:]})
    return result
