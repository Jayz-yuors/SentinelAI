from datetime import datetime
from threading import Lock


class JobManager:

    def __init__(self):

        self.jobs = {}

        self._lock = Lock()

    def create_job(
        self,
        job_id: str,
        analysis_id: str
    ):

        with self._lock:

            self.jobs[job_id] = {
                "jobId": job_id,
                "analysisId": analysis_id,
                "status": "QUEUED",
                "createdAt": datetime.utcnow().isoformat(),
                "startedAt": None,
                "completedAt": None,
                "error": None,
            }

        return self.jobs[job_id]

    def update_status(
        self,
        job_id: str,
        status: str,
        error: str = None
    ):

        with self._lock:

            if job_id not in self.jobs:
                return None

            job = self.jobs[job_id]

            job["status"] = status

            if status == "RUNNING":
                job["startedAt"] = (
                    datetime.utcnow().isoformat()
                )

            if status in {
                "COMPLETED",
                "FAILED",
                "TIMEOUT"
            }:

                job["completedAt"] = (
                    datetime.utcnow().isoformat()
                )

            if error:
                job["error"] = error

            return dict(job)

    def get_job(
        self,
        job_id: str
    ):

        with self._lock:

            job = self.jobs.get(job_id)

            return (
                dict(job)
                if job
                else None
            )


job_manager = JobManager()