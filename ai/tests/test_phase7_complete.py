from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess, json

from ai.phase7.orchestrator import Phase7Orchestrator

def run():
    with TemporaryDirectory() as d:
        repo=Path(d)/"repo"; repo.mkdir()
        def g(*a):
            return subprocess.run(["git",*a],cwd=repo,capture_output=True,text=True,check=True)
        g("init","-b","main")
        g("config","user.email","sentinelai@test.local")
        g("config","user.name","SentinelAI Test")
        (repo/"app.py").write_text("print('original')\n",encoding="utf-8")
        g("add","."); g("commit","-m","initial")
        # Simulate a verified remediation already produced by Phase 5/6.
        (repo/"app.py").write_text("print('remediated')\n",encoding="utf-8")
        result=Phase7Orchestrator().start(str(repo), push=False)
        assert result.status=="completed"
        assert result.branch and result.branch.startswith("sentinelai/")
        assert Path(result.artifact_directory,"manifest.json").exists()
        assert Path(result.artifact_directory,"changes","remediation.diff").exists()
        assert Path(result.artifact_directory,"security","sbom.cdx.json").exists()
        assert Path(result.artifact_directory,"reports","security-report.html").exists()
        assert result.bundle and Path(result.bundle).exists()
    print("PHASE 7 COMPLETE TEST PASSED")

if __name__=="__main__":
    run()
