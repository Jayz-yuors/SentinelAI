from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
import subprocess, uuid, json, shutil

from .config import Phase7Config
from .artifacts import ArtifactStore
from .logging import ExecutionLogger
from .diff_engine import git_diff, changed_files
from .sarif import risk_to_sarif
from .sbom import generate_cyclonedx
from .reports import render_html, write_pdf

@dataclass
class Phase7Result:
    analysis_id: str
    repository: str
    status: str
    artifact_directory: str
    bundle: str | None
    branch: str | None
    commit: str | None
    gate: dict | None
    risk_before: dict | None
    risk_after: dict | None

class Phase7Orchestrator:
    """Phase 7 wrapper. It consumes Phase 1-6 services and does not rewrite them."""

    def __init__(self, config=None):
        self.config=config or Phase7Config()

    def _git(self, repo, args):
        r=subprocess.run(["git",*args],cwd=repo,capture_output=True,text=True,encoding="utf-8",errors="replace")
        if r.returncode: raise RuntimeError(r.stderr.strip() or f"git {' '.join(args)} failed")
        return r.stdout.strip()

    def _profile_dict(self,p):
        if p is None:return None
        if hasattr(p,"to_dict"): return p.to_dict()
        return {"overall_score":getattr(p,"overall_score",0),"overall_level":getattr(p,"overall_level","INFO"),
                "finding_count":getattr(p,"finding_count",0),"affected_files":getattr(p,"affected_files",0),
                "affected_dependencies":getattr(p,"affected_dependencies",0),"severity_counts":getattr(p,"severity_counts",{})}

    def start(self, repository_path: str, base_branch: str|None=None, before_profile=None, after_profile=None, gate_result=None, ai_record=None, push=False):
        repo=Path(repository_path).resolve()
        if not (repo/".git").exists(): raise ValueError("Phase 7 requires a Git repository.")
        analysis_id=f"ANL-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        store=ArtifactStore(self.config.artifacts_root,analysis_id)
        log=ExecutionLogger(store)
        started=datetime.now(timezone.utc).isoformat()
        original_branch=self._git(repo,["branch","--show-current"])
        log.event("initialization","PASS","Phase 7 started",repository=str(repo),base_branch=original_branch)
        store.write_json("manifest.json",{"analysis_id":analysis_id,"repository":str(repo),"base_branch":original_branch,"started_at":started,"status":"running"})

        try:
            if before_profile is not None: store.write_json("risk/before.json",self._profile_dict(before_profile))
            if after_profile is not None: store.write_json("risk/after.json",self._profile_dict(after_profile))
            if ai_record is not None: store.write_json("ai/remediation.json",ai_record)

            candidate=f"sentinelai/security-remediation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            self._git(repo,["switch","-c",candidate])
            log.event("git","PASS","Candidate branch created",branch=candidate)

            changes=changed_files(repo)
            diff=git_diff(repo)
            store.write_json("changes/changed-files.json",changes)
            store.write_text("changes/remediation.diff",diff)

            gate = gate_result.to_dict() if hasattr(gate_result,"to_dict") else gate_result
            if gate is not None: store.write_json("ci/gate.json",gate)

            if after_profile is not None:
                store.write_json("security/sentinelai-results.sarif",risk_to_sarif(after_profile))
            store.write_json("security/sbom.cdx.json",generate_cyclonedx(repo))

            comparison={}
            if before_profile is not None and after_profile is not None:
                bs=self._profile_dict(before_profile).get("overall_score",0)
                a=self._profile_dict(after_profile).get("overall_score",0)
                comparison={"risk_before":bs,"risk_after":a,"delta":a-bs,"improved":a<bs}
            store.write_json("risk/comparison.json",comparison)

            html=render_html(analysis_id,repo,before_profile,after_profile,comparison,gate,changes)
            store.write_text("reports/security-report.html",html)
            if self.config.generate_pdf:
                write_pdf(store.base/"reports/security-report.pdf","SentinelAI Security Report",html.replace("<"," ").replace(">"," "))

            commit=None
            if changes:
                self._git(repo,["add","."])
                self._git(repo,["commit","-m",f"SentinelAI security remediation {analysis_id}"])
                commit=self._git(repo,["rev-parse","HEAD"])
                log.event("git","PASS","Candidate committed",commit=commit)
                if push:
                    self._git(repo,["push","-u","origin",candidate])
                    log.event("git","PASS","Candidate pushed",branch=candidate)

            manifest={"analysis_id":analysis_id,"repository":str(repo),"base_branch":original_branch,"candidate_branch":candidate,
                      "started_at":started,"completed_at":datetime.now(timezone.utc).isoformat(),"status":"completed",
                      "commit":commit,"gate":gate,"risk_before":self._profile_dict(before_profile),"risk_after":self._profile_dict(after_profile)}
            store.write_json("manifest.json",manifest)
            bundle=store.zip_bundle()
            return Phase7Result(analysis_id,str(repo),"completed",str(store.base),str(bundle),candidate,commit,gate,self._profile_dict(before_profile),self._profile_dict(after_profile))
        except Exception as exc:
            log.event("phase7","FAIL",str(exc))
            store.write_json("manifest.json",{"analysis_id":analysis_id,"repository":str(repo),"status":"failed","error":str(exc)})
            raise
