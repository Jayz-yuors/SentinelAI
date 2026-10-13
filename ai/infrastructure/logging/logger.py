import logging

from ai.infrastructure.config.settings import LOG_LEVEL


def configure_logging():

    level = getattr(
        logging,
        LOG_LEVEL.upper(),
        logging.INFO
    )

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


configure_logging()


def get_logger(name: str):

    return logging.getLogger(name)