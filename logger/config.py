import logging

def setup_logger():
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():

        file_logger = logging.FileHandler("scripts.log")
        stream_logger = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_logger.setFormatter(formatter)
        stream_logger.setFormatter(formatter)

        file_logger.setLevel(logging.INFO)
        stream_logger.setLevel(logging.INFO)

        logger.addHandler(file_logger)
        logger.addHandler(stream_logger)

        logger.setLevel(logging.INFO)

    return logger
