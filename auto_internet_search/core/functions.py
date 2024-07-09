import os
import shutil
import importlib
import logging
import pandas as pd
from configparser import ConfigParser
from typing import Type

from auto_internet_search.core.constants.columns import ColNames

logger = logging.getLogger(__name__)

def class_getter(component_config: ConfigParser) -> Type:
    """Gets and returns a class from a module based on the provided configuration.

    Args:
        component_config (ConfigParser): The configuration parser with module and class info.

    Returns:
        Type: The class specified in the configuration.
    """
    module = importlib.import_module(component_config['module_path'])
    class_result = getattr(module, component_config['class_name'])(component_config)

    return class_result

def delete_directory(directory: str) -> None:
    """Deletes a directory, whether it is empty or not.

    Args:
        directory (str): The directory path.

    Raises:
        OSError: If the directory cannot be deleted.
    """
    try:
        shutil.rmtree(directory)
    except OSError as e:
        logger.warning(f"Unable to handle input directory path '{directory}': {e}")
        raise

def check_or_create_dir(directory: str) -> None:
    """Checks if a directory exists and creates it if it does not.

    Args:
        directory (str): The directory path.

    Raises:
        OSError: If the directory cannot be created.
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as e:
        print(f"Unable to handle input directory path '{directory}': {e}")
        raise

def save_to_excel_country_risk_level(country: str, risk_category: str, df: pd.DataFrame, output_dir: str, mode: str) -> None:
    """Saves a DataFrame to an Excel file with a sheet named after the risk category.

    Args:
        country (str): The country name.
        risk_category (str): The risk category name.
        df (pd.DataFrame): The DataFrame to save.
        output_dir (str): The output directory where the Excel file will be saved.
        mode (str): The file mode ('w' for write, 'a' for append).
    """
    COLUMN_NAMES = [
        ColNames.country,
        ColNames.risk_category_full_name,
        ColNames.commodity,
        ColNames.lang,
        ColNames.prompt,
        ColNames.data_source,
        ColNames.url,
        ColNames.title,
        ColNames.published_date,
        ColNames.publisher,
        ColNames.article_clean_text,
        ColNames.download_state,
        ColNames.upload_time
    ]

    file_path = f'{output_dir}/{country}.xlsx'
    with pd.ExcelWriter(file_path, engine='openpyxl', mode=mode) as writer:
        df = pd.DataFrame(df, columns=COLUMN_NAMES)
        df.to_excel(writer, sheet_name=risk_category, index=False)