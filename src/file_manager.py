import os
import logging
from .config import InputFileConfig, StationConfig
from typing import List, Dict, Tuple
import pandas as pd
import warnings

logger = logging.getLogger(__name__)

import os

def toa5_to_df(input_file : str,
                config: InputFileConfig
            ) -> Tuple[pd.DataFrame, List[str]]:
    """
    Work with TOA5 file data from Campbell dataloggers (Sonic, Slow, etc.)
    with Sonic Anemometer and Termoigrometers with N vertical levels

    Parameters
    ----------
    input_file: str
        path to file in TOA5
    config: InputFileConfig
        configuration file input
    Returns
    -------
    Tuple[pd.DataFrame, List[str]]
        - The file as a dataframe.
        - List of strings containing the original 4 header lines.
    """
    
    #extract header
    raw_header = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for _ in range(4):
            raw_header.append(f.readline())

    #csv to df
    types = config.get_file_cols_type()
    df = pd.read_csv(input_file, sep=",", header=1, skiprows=[2, 3], dtype="string")
    df = df.filter(items=config.get_file_cols_name())
    df = df.astype(dtype=types, errors='raise')

    return df, raw_header

def get_files_list(folder_path, start_name, end_name):
    """
    Get a sorted list of files in a folder with their full path.

    Parameters
    ----------
    folder_path
        Search is perfomed in this path.
    start_name
        Prefix of the filename to be selected.
    end_name
        Suffix of the filename to be selected.
    """
    try:
        # Usa os.path.join per unire folder_path e f
        files = sorted([
            os.path.join(folder_path, f) 
            for f in os.listdir(folder_path)
            if f.startswith(start_name) and f.endswith(end_name)
        ])
        logger.info(f"Find {len(files)} file {start_name}... in {folder_path}.")
        return files
    except FileNotFoundError:
        logger.error(f"Error: folder {folder_path} not found.")
        return []
    
def get_files_from_config(folder_path, 
                          input_config: InputFileConfig
                        ) -> List:
    """
    Get a sorted list of files related to an ohject InputFileConfig.

    Parameters
    ----------
    folder_path
        Serach is perfomed in this path.
    input_config: InputFileConfig
        Configuration object conaining the identifier of the files.
        Only files containing the configuration name_file attribute in the filename are selected.
        Serch string case-insensitive
    """
    if not isinstance(input_config, InputFileConfig):
        raise TypeError("input_config must be an instance of InputFileConfig dataclass")
    
    substring = input_config.file_name
    try:
        files = sorted([
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path) 
            if substring.lower() in f.lower()
        ])
        logger.info(f"Find {len(files)} file *{substring}*... in {folder_path}.")
        return files
    except FileNotFoundError:
        logger.error(f"Error: folder {folder_path} not found.")
        return []
    
def get_files_from_station(folder_path, 
                           station: StationConfig
                        ) -> Dict[str, List]:
    """
    Return a dictionary of list of files. 
    Key is the config ID, value is the related list of input files.

    """
    if not isinstance(station, StationConfig):
        raise TypeError("station must be an instance of StationConfig dataclass")
    
    dict_files = {}

    configs = station.get_files_config()
    for config_id, config in configs.items():
        list_of_file = get_files_from_config(folder_path=folder_path, input_config=config)
        dict_files[config_id] = list_of_file

    return dict_files

