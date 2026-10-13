from pathlib import Path
from datetime import datetime, timezone
import json, zipfile

class ArtifactStore:
    def __init__(self, root: Path, analysis_id: str):
        self.base = Path(root) / analysis_id
        self.base.mkdir(parents=True, exist_ok=True)
        for name in ("findings","risk","ai","changes","git","github","ci","reports","logs","snapshots"):
            (self.base / name).mkdir(exist_ok=True)

    def write_json(self, relative: str, data):
        p = self.base / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return p

    def write_text(self, relative: str, text: str):
        p = self.base / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def append_jsonl(self, relative: str, event: dict):
        p = self.base / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")

    def snapshot(self, repository: Path, name: str):
        dest = self.base / "snapshots" / name
        if dest.exists():
            import shutil
            shutil.rmtree(dest)
        import shutil
        shutil.copytree(repository, dest, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv", "venv", "node_modules", "artifacts"))
        return dest

    def zip_bundle(self):
        out = self.base.parent / f"{self.base.name}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in self.base.rglob("*"):
                if p.is_file():
                    z.write(p, p.relative_to(self.base.parent))
        return out
