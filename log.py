import logging

def setup_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname).4s (%(lineno)3s %(funcName)s)  %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger