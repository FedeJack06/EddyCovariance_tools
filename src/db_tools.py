import logging
import duckdb as db
import pandas as pd
from .config import InputFileConfig, StationConfig
from .file_manager import get_files_from_station, toa5_to_df

logger = logging.getLogger(__name__)

def df_to_db(con: db.DuckDBPyConnection, df_in: pd.DataFrame, table, map_df_db_cols):
    """
    Parameters
    ----------
    Returns
    ----------
    """
    table_cols = []
    df_cols = []
    for key, value in map_df_db_cols.items():
        df_cols.append(key)
        table_cols.append(value)

    query = f"""
        INSERT INTO {table} ({", ".join(table_cols)})
        SELECT {", ".join(df_cols)} FROM df_in
    """
    try:
        inserted_rows = con.execute(query).fetchone()[0]
        return inserted_rows
    except db.Error as e:
        # Non gestiamo il log qui, ma "rilanciamo" l'errore per farlo gestire a chi chiama la funzione.
        # Questa è un'ottima pratica ("don't be overly defensive").
        raise

def fill_db_files_list(con: db.DuckDBPyConnection, db_table, file_list, config: InputFileConfig) -> None:
    """
    Reads raw data files, renames columns according to configuration, 
    and uploads them to the DuckDB connection.
    """
    for file in file_list:

        df, header = toa5_to_df(file, config=config)

        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].mask(df[numeric_cols] > 999)

        map = config.get_table_cols_name()

        try:
            insert_query = df_to_db(con=con, df_in=df, table=db_table, map_df_db_cols=map)
            logging.info(f"{file}: Query OK, {insert_query} row(s) affected")
        except db.Error as e:
            logging.error(f"Error importing file: {file} | Error: {e}")

def fill_station_db(con: db.DuckDBPyConnection, station: StationConfig, input_dir):
    all_station_files = get_files_from_station(folder_path = input_dir, station=station)

    for config_id, file_list in all_station_files.items():
        config = station.get_input_config(config_id)
        table_name = station.get_table_name(config_id)
        fill_db_files_list(con=con, db_table=table_name, file_list=file_list, config=config)