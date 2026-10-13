from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Phase7Config:
    artifacts_root: Path = Path(os.getenv("SENTINELAI_ARTIFACTS_ROOT", "artifacts"))
    max_gate_score: int = int(os.getenv("SENTINELAI_SECURITY_GATE_MAX_SCORE", "50"))
    block_critical: bool = os.getenv("SENTINELAI_SECURITY_GATE_BLOCK_CRITICAL", "true").lower() == "true"
    block_high: bool = os.getenv("SENTINELAI_SECURITY_GATE_BLOCK_HIGH", "false").lower() == "true"
    keep_snapshots: bool = os.getenv("SENTINELAI_KEEP_SNAPSHOTS", "true").lower() == "true"
    generate_pdf: bool = os.getenv("SENTINELAI_GENERATE_PDF", "true").lower() == "true"
    github_enabled: bool = os.getenv("GITHUB_TOKEN", "").strip() != ""
