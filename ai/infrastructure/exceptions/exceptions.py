class SentinelAIException(Exception):
    """Base SentinelAI exception."""

    def __init__(
        self,
        message: str,
        code: str = "SENTINELAI_ERROR"
    ):
        super().__init__(message)
        self.message = message
        self.code = code


class ConfigurationException(SentinelAIException):
    pass


class DatabaseException(SentinelAIException):
    pass


class Neo4jException(SentinelAIException):
    pass


class PipelineException(SentinelAIException):
    pass


class AnalysisException(SentinelAIException):
    pass


class JobException(SentinelAIException):
    pass


class AnalysisNotFoundException(SentinelAIException):
    pass