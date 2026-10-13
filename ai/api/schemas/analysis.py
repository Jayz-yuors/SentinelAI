from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ============================================================
# REQUEST
# ============================================================

class AnalysisRequest(BaseModel):

    repositoryUrl: str

    branch: str = "main"


# ============================================================
# LATEST COMMIT
# ============================================================

class LatestCommit(BaseModel):

    hash: Optional[str] = None

    author: Optional[str] = None

    date: Optional[str] = None

    message: Optional[str] = None


# ============================================================
# IMPACT ANALYSIS
# ============================================================

class ImpactAnalysis(BaseModel):

    changed_file_count: int = 0

    impacted_file_types: List[str] = []

    changes: List[Dict[str, Any]] = []


# ============================================================
# PHASE 2 — DEPENDENCY GRAPH
# ============================================================

class DependencyGraph(BaseModel):

    nodes: List[Any] = []

    edges: List[Any] = []


# ============================================================
# PHASE 2 — GRAPH ANALYSIS
# ============================================================

class GraphAnalysis(BaseModel):

    totalNodes: int = 0

    totalEdges: int = 0

    dependencyCounts: Dict[str, Any] = {}

    highImpactFiles: List[Any] = []

    circularDependencies: List[Any] = []


# ============================================================
# PHASE 2 — DEPENDENCY RISK
# ============================================================

class DependencyRisk(BaseModel):

    overallScore: float = 0

    overallRisk: str = "UNKNOWN"

    fileRisks: List[Any] = []


# ============================================================
# PHASE 3 — SECURITY ANALYSIS
# ============================================================

class SecurityAnalysis(BaseModel):

    secrets: Dict[str, Any] = {}

    dependencyVulnerabilities: Dict[str, Any] = {}

    cves: Dict[str, Any] = {}

    staticAnalysis: Dict[str, Any] = {}

    threatAnalysis: Dict[str, Any] = {}

    risk: Dict[str, Any] = {}

    findings: List[Dict[str, Any]] = []

    dependencyContext: Dict[str, Any] = {}


# ============================================================
# RESPONSE
# ============================================================

class AnalysisResponse(BaseModel):

    # ========================================================
    # COMMON
    # ========================================================

    success: bool

    repositoryUrl: str

    repositoryName: str

    branch: str

    # ========================================================
    # PHASE 1
    # ========================================================

    totalFiles: int

    languages: List[str]

    fileTypes: Dict[str, int]

    changedFiles: List[str]

    codeStructure: List[Dict[str, Any]]

    imports: Dict[str, List[str]]

    latestCommit: Optional[LatestCommit] = None

    impactAnalysis: ImpactAnalysis

    # ========================================================
    # PHASE 2
    # ========================================================

    dependencyExtraction: List[Dict[str, Any]] = []

    dependencyGraph: DependencyGraph = DependencyGraph()

    graphAnalysis: GraphAnalysis = GraphAnalysis()

    dependencyRisk: DependencyRisk = DependencyRisk()

    # ========================================================
    # PHASE 3
    # ========================================================

    securityAnalysis: SecurityAnalysis = SecurityAnalysis()

    # ========================================================
    # MESSAGE
    # ========================================================

    message: str
class PipelineAnalysisResponse(BaseModel):
    success: bool
    analysisId: str
    status: str
    result: dict = {}
    error: str | None = None
    attempts: int = 1