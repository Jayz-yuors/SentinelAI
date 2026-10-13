import subprocess
import time


class CommandRunner:

    @staticmethod
    def run(
        command: list[str],
        cwd: str | None = None,
        timeout: int = 300,
    ):

        start = time.perf_counter()

        try:

            process = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            elapsed = int(
                (time.perf_counter() - start) * 1000
            )

            return {
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "execution_time_ms": elapsed,
                "timed_out": False,
            }

        except subprocess.TimeoutExpired as exc:

            elapsed = int(
                (time.perf_counter() - start) * 1000
            )

            return {
                "returncode": -1,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
                "execution_time_ms": elapsed,
                "timed_out": True,
            }

        except Exception as exc:

            elapsed = int(
                (time.perf_counter() - start) * 1000
            )

            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(exc),
                "execution_time_ms": elapsed,
                "timed_out": False,
            }