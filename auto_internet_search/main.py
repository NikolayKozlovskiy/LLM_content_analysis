import sys
import logging
from auto_internet_search.core.configuration import prepare_config
from auto_internet_search.core.logging import set_up_basic_logging
from auto_internet_search.core.functions import class_getter

def main(config_file_path: str): 
    config = prepare_config(config_file_path)

    set_up_basic_logging(config["Logging"])
    logger = logging.getLogger(__name__)
    logger.info("Starting components' execution\n")

    for component_name in list(config['Components'].keys()): 
        component_config = config[component_name]
        component = class_getter(component_config)

        component.run()

if __name__ == '__main__':
    main(sys.argv[1])