import logging


class DSLog:
    logger = logging.getLogger("pydigitalstrom")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
