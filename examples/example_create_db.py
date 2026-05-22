"""
Script for create a database structure with tables for each stations
as described into the configuration objects.
"""

from .station_config import *
import duckdb as db

database = "./data/database.db"

stations = [s_26458]

# loop over the station
with db.connect(database) as con:
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
            con.execute(query)
            con.sql(f"show {table_name}").show()
    con.sql("show tables").show()