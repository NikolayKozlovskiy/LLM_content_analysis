import os
import shutil
import importlib
import pandas as pd
from configparser import ConfigParser
from typing import Type

from auto_internet_search.core.constants.columns import ColNames

def class_getter(component_config: ConfigParser) -> Type:

    module = importlib.import_module(component_config['module_path'])
    class_result = getattr(module, component_config['class_name'])(component_config)

    return class_result


def delete_directory(directory: str) -> None:
    """
    Delete a directory both Empty or Non-Empty

    Args:
        directory (str): The directory path
    """

    try:
        shutil.rmtree(directory)
    except OSError as e:
        print(f"Unable to handle input directory path '{directory}': {e}")
        raise


def check_or_create_dir(directory: str) -> None:
    """
    Check if a directory exists and create it if it doesn't

    Args:
        directory (str): The directory path
    """

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as e:
        print(f"Unable to handle input directory path '{directory}': {e}")
        raise

def save_to_excel_country_risk_level(country, risk_category, df, output_dir, mode):

    
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
        ColNames.upload_time,
        ColNames.manual_check_suggested,
        ColNames.reason_for_manual_check
    ]

    file_path = f'{output_dir}/{country}.xlsx'
    with pd.ExcelWriter(file_path, engine='openpyxl', mode=mode) as writer:
            df = pd.DataFrame(df, columns=COLUMN_NAMES)
            df[ColNames.manual_check_suggested] = df[ColNames.manual_check_suggested].astype(int)  # Ensure the column is int
            df.to_excel(writer, sheet_name=risk_category, index=False)

