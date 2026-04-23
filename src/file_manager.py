import os
import logging
from typing import List, Dict, Tuple
import pandas as pd
from .config import InputFileConfig, StationConfig

logger = logging.getLogger(__name__)

def toa5_to_df(input_file : str,
               config: InputFileConfig,
               date_index: bool = False) -> Tuple[pd.DataFrame, List[str]]:
    """
    Import a TOA5 Campbell file into a Pandas Dataframe.
    TOA5 should have the datetime column named "TIMESTAMP", important only
    if you chose to set the datetime column as index.
    The output dataframe has all the columns and types specified in the
    InputFileConfig passed. Be sure you have set the config right.
    The name of the columns in the dataframe are the same of the files.

    Parameters
    ----------
    input_file: str
        path of TOA5 file
    config: InputFileConfig
        configuration file input, with all the info about the 
        columns to be inported.
    date_index: bool
        If true sets the datetime column ("TIMESTAMP") as index and
        removes it from df columns. Default False, so keeps the 
        default numeric index.

    Returns
    -------
    Tuple[pd.DataFrame, List[str]]
        - The file as a dataframe.
        - List of strings containing the original 4 header lines.
    """

    #extract 4 line header from file
    raw_header = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for _ in range(4):
            raw_header.append(f.readline())

    #get pandas dtype for each column from the config object
    types = config.get_file_cols_type()
    #toa5 file to pandas 
    df = pd.read_csv(input_file, sep=",", header=1, skiprows=[2, 3], dtype="string")
    #remove column not specified in the input files configuration
    df = df.filter(items=config.get_file_cols_name())
    #convert the column dtypes to dtypes specified in the config
    try:
        df = df.astype(dtype=types, errors='raise')
    except Exception as e:
        logger.error(f"Error pandas dtype on file {input_file}: {e}")
        pass

    #set datetime column as index
    if date_index:
        #column_name_date = df.dtypes[df.dtypes == 'datetime64[ms]'].index[0]
        df.set_index("TIMESTAMP", inplace=True)
        df.drop(columns=["TIMESTAMP"], inplace=True, errors='ignore')

    return df, raw_header

def csv_to_df(input_file : str,
               config: InputFileConfig,
               index: str = None) -> pd.DataFrame:
    """
    Import a generic csv file into a Pandas Dataframe.
    The input file must have the first row containing the name of
    th columns.
    The output dataframe has all the columns and types specified in the
    InputFileConfig passed. Be sure you have set the config right.
    The name of the columns in the dataframe are the same of the files.
    You can specify the column to set as dataframe index.

    Parameters
    ----------
    input_file: str
        path of csv file
    config: InputFileConfig
        configuration file input, with all the info about the 
        columns to be inported.
    index: str
        The name of the column to set as dataframe index.
        This column will be removed from the columns of the dataframe.
        Default None, so keeps the default numeric index.

    Returns
    -------
    pd.DataFrame
        Dataframe containing the columns choosen in InputConfigFile.
    """

    #get pandas dtype for each column from the config object
    types = config.get_file_cols_type()

    df = pd.read_csv(input_file, sep=",", header=0, dtype="string")
    #remove column not specified in the input files configuration
    df = df.filter(items=config.get_file_cols_name())
    #convert the column dtypes to dtypes specified in the config
    df = df.astype(dtype=types, errors='raise')

    #set datetime column as index
    if index:
        #column_name_date = df.dtypes[df.dtypes == 'datetime64[ms]'].index[0]
        df.set_index(index, inplace=True)
        df.drop(columns=[index], inplace=True, errors='ignore')

    return df

def get_files(folder_path: str,
              start_name: str, 
              end_name: str) -> List:
    """
    Get a sorted list of files from a folder. The name of the files
    must start with "start_name" and end with "end_name".
    The search is case-sensitive.
    The files are returned as String with their relative path.

    Parameters
    ----------
    folder_path: str
        Search is perfomed in this path.
    start_name: str
        First part of the filename to be selected.
    end_name: str
        Final part of the filename to be selected.

    Returns
    -------
    List[str]
        A list of the selected files with their relative path.
    """
    try:
        # get a sorted list of files that start and end with the parameters
        files = sorted([
            os.path.join(folder_path, f) 
            for f in os.listdir(folder_path)
            if f.startswith(start_name) and f.endswith(end_name)
        ])
        # how many files found
        logger.info(f"Find {len(files)} file starting with {start_name} and ending \
                    with {end_name}, in {folder_path}.")
        return files
    except FileNotFoundError:
        logger.error(f"Error: folder {folder_path} not found.")
        return []
    
def get_files_sub(folder_path: str,
                  substring: str) -> List:
    """
    Get a sorted list of files from a folder. The name of the files
    must contains the substring passed.
    The search is case-insensitive.
    The files are returned as String with their relative path.

    Parameters
    ----------
    folder_path: str
        Serach is perfomed in this path.
    substring: str
        Substring contained in the name of the searched files.

    Returns
    -------
    List[str]
        A list of the selected files with their relative path.
    """

    try:
        # get a sorted list of files that contains the substring in their name
        files = sorted([
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path) 
            if substring.lower() in f.lower()
        ])
        # how many files found
        logger.info(f"Find {len(files)} file *{substring}*... in {folder_path}.")
        return files
    except FileNotFoundError:
        logger.error(f"Error: folder {folder_path} not found.")
        return []
    
def get_files_from_station(folder_path: str, 
                           station: StationConfig) -> Dict[str, List]:
    """
    Gets all the files related to one station. One search is performed
    for each InputFileConfig object in the StationConfig.
    Returns a dictionary, with a list of files for each 
    InputFileConfig of the station.
    The files are returned as String with their relative path.

    Parameters
    ----------
    folder_path: str
        Serach is perfomed in this path.
    station: StationConfig
        Station object conaining all the input file configuration.
        Only files containing the "input_files_name" in the filename are selected.
        Serch string case-insensitive

    Returns
    ----------
    Dict[str, List]
        Return a dictionary of list of files. 
        Key is the config ID, value is the related list of input files,
        with their relative path.

    """
    if not isinstance(station, StationConfig):
        raise TypeError("station must be an instance of StationConfig dataclass")
    
    #dictionary: key is the config_id, value is the related list of files
    dict_files = {}

    #get all the substrings to search files
    files_substring = station.input_files_name
    for config_id, substring in files_substring.items():
        #get the list of files of the same type (the same input config)
        list_of_file = get_files_sub(folder_path=folder_path, substring=substring)
        #output
        dict_files[config_id] = list_of_file

    return dict_files

