import logging
from datetime import datetime
from configparser import ConfigParser

from auto_internet_search.core.functions import check_or_create_dir

def set_up_basic_logging(logging_config: ConfigParser)->None:

    level = logging_config.get("level", fallback="DEBUG")
    format = logging_config.get("format", fallback="%(asctime)s %(filename)s: %(message)s")
    datefmt = logging_config.get("datefmt", fallback="%Y-%m-%d %H:%M:%S")
    log_dir = logging_config.get("log_dir")

    check_or_create_dir(log_dir)

    log_file_path = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}.log"

    logging.basicConfig(
        format=format,
        handlers=[
            logging.FileHandler(log_file_path, 'w'),
            logging.StreamHandler()
        ],
        datefmt=datefmt,
        level=level
    )