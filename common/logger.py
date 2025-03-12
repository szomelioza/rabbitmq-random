import logging


def get_logger() -> logging.Logger:
    """Get Logger for app

    Returns:
        loggin.Logger: configured instance of Logger
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logging.getLogger("pika").setLevel(logging.CRITICAL)
    return logging.getLogger()
