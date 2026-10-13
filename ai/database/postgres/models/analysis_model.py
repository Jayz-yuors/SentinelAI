from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AnalysisRecord:

    analysis_id: str

    repository_url: str

    repository_name: str

    branch: str

    status: str

    created_at: datetime

    completed_at: Optional[datetime] = None

    error_message: Optional[str] = None