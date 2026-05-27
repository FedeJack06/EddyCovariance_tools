#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import duckdb as db
import pandas as pd
from typing import Dict, List
from pathlib import Path
from .config import InputFileConfig, StationConfig
from .file_manager import get_files_from_station, toa5_to_df

logger = logging.getLogger(__name__)

def df_to_db(con: db.DuckDBPyConnection, 
             df_in: pd.DataFrame, 
             db_table: str, 
             map_df_db_cols: Dict[str, str] = None) -> tuple[int, int]:
    """
    Fill a database table with a Pandas dataframe.
    You can specify a relation between the column names 
    in the dataframe and the column names in the table.
    If you don't pass the relation, the table and df must
    have the same column name.

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
    int: 
        Number of inserted rows
    int:
        Number of skipped rows: difference between df rows and inserted rows
    """

    if map_df_db_cols is not None:
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
            ON CONFLICT DO NOTHING
        """
    else: #insert all df column into table
        query = f"INSERT INTO {db_table} BY NAME SELECT * FROM df_in ON CONFLICT DO NOTHING"

    try:
        inserted_rows = con.execute(query).fetchone()[0]
    except db.Error as e:
        raise

    skipped = len(df_in) - inserted_rows

    return inserted_rows, skipped

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

        #get the dictiocary that link the column name in the dataframe
        #and the column name in the table
        map = config.get_table_cols_name()

        try:
            #insert entire dataframe into the table
            inserted_rows, skipped_rows = df_to_db(con=con, df_in=df, db_table=db_table, map_df_db_cols=map)
            logger.info(f"{file.name}: Query OK, {inserted_rows} row(s) affected")
            if skipped_rows > 0:
                logger.warning(f"Warning on {file.name}: {skipped_rows} duplicate row(s) skipped, {inserted_rows} inserted.")
        except db.Error as e:
            logger.error(f"Error importing file: {file.name}: {e}")

def fill_db_station_toa5(con: db.DuckDBPyConnection, 
                    station: StationConfig, 
                    input_dir: str,
                    configs: List[str] = None) -> None:
    """
    Fills the database with the files produced by a station.
    StationConfig object is used to put different file types into
    the correct database tables. A table corresponds to a file type,
    and it is filled only with files of the same type.
    Different type of files can be in the same directory. They are sorted
    based on the substring in their name, specified in the station configuration.
    Only file type listed in config parameter will be inseted into db.

    Parameters
    ----------
    con: db.DuckDBPyConnection
        connection to the database
    station: StationConfig
        Station object conaining all the input file configuration
    input_dir: str
        Directory containing all the files produced by the station.
    configs: List[str] = None
        List of id of InputFileConfig in the station, to insert into database.
        If None, all InputFileConfig of station will be inseted.
    """
    #get a dict with the input configuration id as key and
    #the list of related files as value
    all_station_files = get_files_from_station(input_dir, station, configs)

    for config_id, file_list in all_station_files.items():
        #get the InputFileConfig object based on its id
        config = station.get_input_config(config_id)
        #get the database table name associated with this input config
        table_name = station.get_table_name(config_id)
        #fill the table with files of the same type
        fill_db_toa5(con=con, db_table=table_name, file_list=file_list, config=config)

def _db_df(db_path: str | Path, 
           table: str, 
           query: str, 
           params: list = None) -> pd.DataFrame:
    """
    Executes a query and returns a DataFrame
    indexed by the table's PRIMARY KEY column.

    """
    db_path = Path(db_path)
    with db.connect(db_path) as con:
        # get table metadata, one row for each column info
        table_info = con.execute(f"PRAGMA table_info({table})").df()
        # pk column = 1 if is primary key. List of name of pk column
        pk_cols = (table_info[table_info["pk"] > 0].sort_values("pk")["name"].tolist())

        df = con.execute(query, params or []).df()

    # if found pk column
    if pk_cols:
        # index or multindex based on pk column finded
        # drop column index
        df = df.set_index(pk_cols if len(pk_cols) > 1 else pk_cols[0], drop=True)
    else:
        logger.warning(f"No PRIMARY KEY found in {table}, default index in df")

    return df

def table_to_df(db_path: str | Path,
                table: str,
                orderby: str = "1 ASC") -> pd.DataFrame:
    """Get entire db table into a Pandas df"""
    
    query = f"SELECT * FROM {table} ORDER BY {orderby}"
    return _db_df(db_path, table, query)

def table_to_df_date(db_path: str | Path,
                   table: str,
                   start_date: str,
                   end_date: str,
                   orderby: str = "1 ASC") -> pd.DataFrame:
    """
    Get dataframe from a table between two date.

    Parameters
    ----------
    db_path: str | Path
        Path to input database file
    table: str
        Table name to be imported
    start_date: str
        First date to be selected
    end_date: str
        Last date to be selected
    orderby: str
        Column name to order rows ASC or DESC.
        Default is order by the first column (datetime) ascending

    Returns
    -------
    pd.DataFrame
        pd.DataFrame indexed by PRIMARY KEY
    """
    query = f"SELECT * FROM {table} WHERE datetime BETWEEN ? AND ? ORDER BY {orderby}"
    return _db_df(db_path, table, query, [start_date, end_date])

def table_to_df_dates(db_path: str | Path,
                   table: str,
                   dates: List[tuple],
                   orderby: str = "1 ASC") -> pd.DataFrame:
    """
    Get a dataframe from a table from some data intervals.

    Parameters
    ----------
    db_path: str | Path
        Path to input database file
    table: str
        Table name to be imported
    dates: List[tuple]
        List of (start_date, end_date) tuples.
    orderby: str
        Column name to order rows ASC or DESC.
        Default is order by the first column (datetime) ascending

    Returns
    -------
    pd.DataFrame
        pd.DataFrame indexed by PRIMARY KEY
    """
    conditions = " OR ".join(["(datetime BETWEEN ? AND ?)"] * len(dates))
    query = f"SELECT * FROM {table} WHERE {conditions} ORDER BY {orderby}"
    params = [date for interval in dates for date in interval]

    return _db_df(db_path, table, query, params)

def create_station_db(db_path: str | Path,
              stations: List[StationConfig]) -> None:
    """
    Create a database structure with tables for each station
    as described in the configuration objects.
    """
    db_path = Path(db_path)

    with db.connect(db_path) as con:
        for station in stations:
            for config_id, config in station.get_configs().items():
                table_name = station.get_table_name(config_id)
                cols_type = config.get_table_cols_type()
                cols_query = ", ".join(f"{k} {v}" for k, v in cols_type.items())
                query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {cols_query}
                    )
                """
                try:
                    con.execute(query)
                    logger.info(f"Table created (or already exists): {table_name}")
                except db.Error as e:
                    logger.error(f"Error creating {table_name}: {e}")

def create_flux_table(conn, table_name):
    """
    Create flux table in DuckDB with columns for each sonic level.
    
    Parameters
    ----------
    conn : duckdb.DuckDBPyConnection
    table_name : str
    n_levels : int
        Number of sonic levels.
    """
    cols = ["datetime TIMESTAMP PRIMARY KEY"]
    cols += [
        # avg wind components
        "u DOUBLE",
        "v DOUBLE",
        "w DOUBLE",
        "ts DOUBLE",
        "u_real DOUBLE",
        "v_real DOUBLE",
        "w_real DOUBLE",
        # second order moments
        "uw DOUBLE",
        "vw DOUBLE",
        "uv DOUBLE",
        "wT DOUBLE",
        "uT DOUBLE",
        "vT DOUBLE",
        "uu DOUBLE",
        "vv DOUBLE",
        "ww DOUBLE",
        "TT DOUBLE",
        "sigu DOUBLE",
        "sigv DOUBLE",
        "sigw DOUBLE",
        "sigT DOUBLE",
        "ustar DOUBLE",
        "TKE DOUBLE",
    ]
    
    cols_def = ", ".join(cols)
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_def})")
        