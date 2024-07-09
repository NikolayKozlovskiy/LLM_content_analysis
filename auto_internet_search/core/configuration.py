import os
import errno
from configparser import ConfigParser, ExtendedInterpolation

def prepare_config(config_file_path: str) -> ConfigParser:
    """Prepares and returns a configuration parser for the given config file path.

    This function checks if the configuration file exists, raises a FileNotFoundError if not,
    and then prepares a ConfigParser with custom converters and options.

    Args:
        config_file_path (str): The path to the configuration file.

    Returns:
        ConfigParser: A ConfigParser object configured with the given file.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
    """

    if not os.path.exists(config_file_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_file_path)
     
    converters = {
        "list": lambda val: [i.strip() for i in val.strip().split("\n")],
        "eval": eval,
    }

    parser: ConfigParser = ConfigParser(
        converters=converters, 
        interpolation=ExtendedInterpolation(),
        inline_comment_prefixes="#",
        allow_no_value=True
    )
    parser.optionxform = lambda option: option

    parser.read(config_file_path)

    return parser