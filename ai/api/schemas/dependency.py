from typing import Any

from pydantic import BaseModel


class DependencyAnalysisRequest(BaseModel):

    repositoryUrl: str

    branch: str = "main"


class DependencyAnalysisResponse(BaseModel):

    success: bool

    repositoryUrl: str

    repositoryName: str

    branch: str

    dependencyAnalysis: dict[str, Any]

    message: str