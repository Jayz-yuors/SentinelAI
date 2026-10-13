from datetime import datetime, timezone

class ExecutionLogger:
    def __init__(self, store):
        self.store = store

    def event(self, stage: str, status: str, message: str, **data):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage": stage,
            "status": status,
            "message": message,
            "data": data,
        }
        self.store.append_jsonl("logs/execution.jsonl", payload)
        return payload
