import time
from threading import Lock


class AnalysisMetrics:

    def __init__(self):

        self.total = 0
        self.success = 0
        self.failed = 0
        self.total_duration = 0.0

        self._lock = Lock()

    def start(self):

        return time.perf_counter()

    def record_success(
        self,
        started_at: float
    ):

        duration = (
            time.perf_counter()
            - started_at
        )

        with self._lock:

            self.total += 1
            self.success += 1
            self.total_duration += duration

    def record_failure(
        self,
        started_at: float
    ):

        duration = (
            time.perf_counter()
            - started_at
        )

        with self._lock:

            self.total += 1
            self.failed += 1
            self.total_duration += duration

    def snapshot(self):

        with self._lock:

            average = (
                self.total_duration
                / self.total
                if self.total
                else 0.0
            )

            return {
                "total": self.total,
                "success": self.success,
                "failed": self.failed,
                "totalDuration": round(
                    self.total_duration,
                    4
                ),
                "averageDuration": round(
                    average,
                    4
                ),
            }


analysis_metrics = AnalysisMetrics()