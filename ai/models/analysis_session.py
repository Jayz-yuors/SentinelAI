from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AnalysisSession:

    analysis_id: str

    repository_url: str

    repository_name: str

    branch: str

    status: str

    created_at: datetime

    completed_at: Optional[datetime] = None

    error_message: Optional[str] = None

    def to_dict(self):

        return {
            "analysisId": self.analysis_id,
            "repositoryUrl": self.repository_url,
            "repositoryName": self.repository_name,
            "branch": self.branch,
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "completedAt": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
            "errorMessage": self.error_message,
        }