import argparse
import duckdb as db
import os
from src.utils import setup_logging
from src.config import InputFileConfig, StationConfig
from src.db_tools import fill_db_station_toa5

def from_sd():
    # --- CONFIG ---
    gill_1 = InputFileConfig.gillwindmaster(n_levels=1)
    trh_1 = InputFileConfig.defaultTermoigrometer(n_levels=1)
    stat_info = InputFileConfig.defaultStatus()
    gill_2 = InputFileConfig.gillwindmaster(n_levels=2)
    trh_2 = InputFileConfig.defaultTermoigrometer(n_levels=2)

    s_4174 = StationConfig(
        station_name="4174"
    )
    s_4174.add_input_file_config("sonic", gill_1, "sonic_4174", "TOA5py_4174_sonic*")
    s_4174.add_input_file_config("slow", trh_1, "slow_4174", "TOA5py_4174_slow*")
    s_4174.add_input_file_config("stat", stat_info, "stat_4174", "TOA5py_4174_stat*")


    s_4175 = StationConfig(
        station_name="4175"
    )
    s_4175.add_input_file_config("sonic", gill_1, "sonic_4175", "TOA5py_4175_sonic*")
    s_4175.add_input_file_config("slow", trh_1, "slow_4175", "TOA5py_4175_slow*")
    s_4175.add_input_file_config("stat", stat_info, "stat_4175", "TOA5py_4175_stat*")

    s_6551 = StationConfig(
        station_name="6551"
    )
    s_6551.add_input_file_config("sonic", gill_1, "sonic_6551", "TOA5py_6551_sonic*")
    s_6551.add_input_file_config("slow", trh_1, "slow_6551", "TOA5py_6551_slow*")
    s_6551.add_input_file_config("stat", stat_info, "stat_6551", "TOA5py_6551_stat*")

    s_26428 = StationConfig(
        station_name="26428"
    )
    s_26428.add_input_file_config("sonic", gill_1, "sonic_26428", "TOA5py_26428_sonic*")
    s_26428.add_input_file_config("slow", trh_1, "slow_26428", "TOA5py_26428_slow*")
    s_26428.add_input_file_config("stat", stat_info, "stat_26428", "TOA5py_26428_stat*")

    s_26458 = StationConfig(
        station_name="26458"
    )
    s_26458.add_input_file_config("sonic", gill_2, "sonic_26458", "TOA5py_26458_sonic*")
    s_26458.add_input_file_config("slow", trh_2, "slow_26458", "TOA5py_26458_slow*")
    s_26458.add_input_file_config("stat", stat_info, "stat_26458", "TOA5py_26458_stat*")

    #################################################################
    # --- ESECUZIONE PIPELINE ---

    print("Starting ETL Pipeline from SD...")

    database = "../trieste_campaign.db"
    input_dir = "/media/federico/BackupFoto/trieste_campaign/"
    stations = [s_4174, s_4175, s_6551, s_26428, s_26458]

    with db.connect(database) as con:
        for station in stations:
            print(f"--- Processing Station {station.station_name} ---")
            station_dir = os.path.join(input_dir, station.station_name+"_sd")
            fill_db_station_toa5(con, station, station_dir)
    print("Pipeline executed successfully.")

def from_server(pattern: str):
    # --- CONFIG ---
    gill_1 = InputFileConfig.gillwindmaster(n_levels=1)
    trh_1 = InputFileConfig.defaultTermoigrometer(n_levels=1)
    stat_info = InputFileConfig.defaultStatus()
    gill_2 = InputFileConfig.gillwindmaster(n_levels=2)
    trh_2 = InputFileConfig.defaultTermoigrometer(n_levels=2)

    sonic_filename = "TOA5py_Sonic"+pattern
    slow_filename = "TOA5py_Slow"+pattern
    stat_filename = "TOA5py_Stat"+pattern

    s_4174 = StationConfig(
        station_name="4174"
    )
    s_4174.add_input_file_config("sonic", gill_1, "sonic_4174", sonic_filename)
    s_4174.add_input_file_config("slow", trh_1, "slow_4174", slow_filename)
    s_4174.add_input_file_config("stat", stat_info, "stat_4174", stat_filename)


    s_4175 = StationConfig(
        station_name="4175"
    )
    s_4175.add_input_file_config("sonic", gill_1, "sonic_4175", sonic_filename)
    s_4175.add_input_file_config("slow", trh_1, "slow_4175", slow_filename)
    s_4175.add_input_file_config("stat", stat_info, "stat_4175", stat_filename)

    s_6551 = StationConfig(
        station_name="6551"
    )
    s_6551.add_input_file_config("sonic", gill_1, "sonic_6551", sonic_filename)
    s_6551.add_input_file_config("slow", trh_1, "slow_6551", slow_filename)
    s_6551.add_input_file_config("stat", stat_info, "stat_6551", stat_filename)

    s_26428 = StationConfig(
        station_name="26428"
    )
    s_26428.add_input_file_config("sonic", gill_1, "sonic_26428", sonic_filename)
    s_26428.add_input_file_config("slow", trh_1, "slow_26428", slow_filename)
    s_26428.add_input_file_config("stat", stat_info, "stat_26428", stat_filename)

    s_26458 = StationConfig(
        station_name="26458"
    )
    s_26458.add_input_file_config("sonic", gill_2, "sonic_26458", sonic_filename)
    s_26458.add_input_file_config("slow", trh_2, "slow_26458", slow_filename)
    s_26458.add_input_file_config("stat", stat_info, "stat_26458", stat_filename)

    #################################################################
    # --- ESECUZIONE PIPELINE ---

    print("Starting ETL Pipeline from server...")

    database = "../trieste_campaign_tmp.db"
    input_dir = "/media/federico/BackupFoto/trieste_campaign/"
    stations = [s_4174, s_4175, s_6551, s_26428, s_26458]

    with db.connect(database) as con:
        for station in stations:
            print(f"--- Processing Station {station.station_name} ---")
            station_dir = os.path.join(input_dir, station.station_name)
            fill_db_station_toa5(con, station, station_dir)
    print("Pipeline executed successfully.")

# Setup command line arguments (No hardcoded paths!)
'''parser = argparse.ArgumentParser(description="Trieste Campaign ETL Pipeline")
parser.add_argument("--db", type=str, required=True, help="Path to DuckDB database file")
parser.add_argument("--indir", type=str, required=True, help="Base directory containing station folders")
args = parser.parse_args()'''
# main.py --db my_db.duckdb --indir /path/to/data

setup_logging(__file__)
from_server("*2026-04-09*")

