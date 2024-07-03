import os
import errno
from configparser import ConfigParser, ExtendedInterpolation

def prepare_config(config_file_path): 

    if not os.path.exists(config_file_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_file_path)
    
    converters = {
        "list": lambda val: [i.strip() for i in val.strip().split("\n")],
        "eval": eval,
    }

    parser: ConfigParser = ConfigParser(
        converters=converters, interpolation=ExtendedInterpolation(), inline_comment_prefixes="#", allow_no_value=True
    )
    parser.optionxform = lambda option: option

    parser.read(config_file_path)

    return parser