from ai.infrastructure.logging.logger import get_logger


logger = get_logger("sentinelai.request")


def log_request(
    method: str,
    path: str
):
    logger.info(
        "REQUEST %s %s",
        method,
        path
    )


def log_response(
    method: str,
    path: str,
    status_code: int
):
    logger.info(
        "RESPONSE %s %s -> %s",
        method,
        path,
        status_code
    )