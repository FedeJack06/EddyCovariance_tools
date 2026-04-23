import logging
import duckdb as db
import pandas as pd
from typing import Dict, List
from pathlib import Path
from .config import InputFileConfig, StationConfig
from .file_manager import get_files_from_station, toa5_to_df
from .pre_processing import filter_df_toa5

logger = logging.getLogger(__name__)

def df_to_db(con: db.DuckDBPyConnection, 
             df_in: pd.DataFrame, 
             db_table: str, 
             map_df_db_cols: Dict[str, str]):
    """
    Fill a database table with a Pandas dataframe.
    You must specify a relation between the column names 
    in the dataframe and the column names in the table.

    Parameters
    ----------
    con: db.DuckDBPyConnection
        connection to the database
    df_in: pd.DataFrame
        the Pandas dataframe to put into the table
    db_table: str
        the name of the table to fill
    map_df_db_cols: Dict[str, str]
        a map that links the column names in the dataframe (as keys)
        to the column names in the table (as value)

    Returns
    ----------
    Number of rows inserted
    """

    #put the column name in the dataframe and in the table in two list
    #same list index identifies a pair
    table_cols = []
    df_cols = []
    for key, value in map_df_db_cols.items():
        df_cols.append(key)
        table_cols.append(value)

    #query to insert dataframe rows into a table
    query = f"""
        INSERT INTO {db_table} ({", ".join(table_cols)})
        SELECT {", ".join(df_cols)} FROM df_in
    """
    try:
        #get the number of inserted rows
        inserted_rows = con.execute(query).fetchone()[0]
        return inserted_rows
    except db.Error as e:
        # Non gestiamo il log qui, ma "rilanciamo" l'errore per farlo gestire a chi chiama la funzione.
        # Questa è un'ottima pratica ("don't be overly defensive").
        raise

def fill_db_toa5(con: db.DuckDBPyConnection, 
                 db_table: str, 
                 file_list: List[Path],
                 config: InputFileConfig) -> None:
    """
    Fills a database table with a list of TOA5 files.

    Parameters
    ----------
    con: db.DuckDBPyConnection
        connection to the database
    db_table: str
        the name of the table to fill
    file_list: List[Path]
        a list of Path object, containing the files to put 
        into the database table
    config: InputFileConfig
        configuration file input, with all the info about the 
        columns to be inported.
    """
    for file in file_list:
        df, header = toa5_to_df(file, config=config)
        
        #remove 999.99 numbers, replaced with NAN
        df = filter_df_toa5(df)

        #get the dictiocary that link the column name in the dataframe
        #and the column name in the table
        map = config.get_table_cols_name()

        try:
            #insert entire dataframe into the table
            insert_query = df_to_db(con=con, df_in=df, db_table=db_table, map_df_db_cols=map)
            logger.info(f"{file.name}: Query OK, {insert_query} row(s) affected")
        except db.Error as e:
            logger.error(f"Error importing file: {file.name}: {e}")

def fill_db_station_toa5(con: db.DuckDBPyConnection, 
                    station: StationConfig, 
                    input_dir: str) -> None:
    """
    Fills the database with all the files produced by a station.
    StationConfig object is used to put different file types into
    the correct database tables. A table corresponds to a file type,
    and it is filled only with files of the same type.
    Different type of files can be in the same directory. They are sorted
    based on the substring in their name, specified in the station configuration.

    Parameters
    ----------
    con: db.DuckDBPyConnection
        connection to the database
    station: StationConfig
        Station object conaining all the input file configuration
    input_dir: str
        Directory containing all the files produced by the station.
    """
    #get a dict with the input configuration id as key and
    #the list of related files as value
    all_station_files = get_files_from_station(folder_path = input_dir, station=station)

    for config_id, file_list in all_station_files.items():
        #get the InputFileConfig object based on its id
        config = station.get_input_config(config_id)
        #get the database table name associated with this input config
        table_name = station.get_table_name(config_id)
        #fill the table with files of the same type
        fill_db_toa5(con=con, db_table=table_name, file_list=file_list, config=config)