from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ============================================================
# SECURITY REQUEST
# ============================================================

class SecurityAnalysisRequest(BaseModel):

    repositoryUrl: str

    branch: str = "main"


# ============================================================
# SECURITY FINDING
# ============================================================

class SecurityFinding(BaseModel):

    type: str

    category: str

    file: Optional[str] = None

    line: Optional[int] = None

    severity: str

    message: str

    evidence: Optional[str] = None

    id: Optional[str] = None

    package: Optional[str] = None

    version: Optional[str] = None

    fixVersions: List[str] = []


# ============================================================
# SECURITY RISK
# ============================================================

class SecurityRisk(BaseModel):

    overallScore: int

    overallRisk: str

    totalFindings: int

    fileRisks: List[
        Dict[str, Any]
    ]


# ============================================================
# SECURITY RESPONSE
# ============================================================

class SecurityAnalysisResponse(BaseModel):

    success: bool

    securityAnalysis: Dict[
        str,
        Any
    ]

    message: str