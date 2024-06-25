import importlib
from configparser import ConfigParser
from typing import Type

def class_getter(component_config: ConfigParser) -> Type:

    module = importlib.import_module(component_config['module_path'])
    class_result = getattr(module, component_config['class_name'])(component_config)

    return class_result