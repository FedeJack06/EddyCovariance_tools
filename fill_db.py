# main.py
import argparse
import duckdb as db
from src.utils import setup_logging
from src.config import InputFileConfig, StationConfig
from src.db_tools import fill_db_station_toa5

def main():
    # Setup command line arguments (No hardcoded paths!)
    '''parser = argparse.ArgumentParser(description="Trieste Campaign ETL Pipeline")
    parser.add_argument("--db", type=str, required=True, help="Path to DuckDB database file")
    parser.add_argument("--indir", type=str, required=True, help="Base directory containing station folders")
    args = parser.parse_args()'''

    setup_logging(__file__)

    #################################################################
    # --- CONFIGURAZIONI ---
    # Definiamo rigorosamente le regole per ogni sensore usando la Dataclass
    gill_1 = InputFileConfig.gillwindmaster(n_levels=1)
    trh_1 = InputFileConfig.defaultTermoigrometer(n_levels=1)
    stat_info = InputFileConfig.defaultStatus()

    s_26458 = StationConfig(
        station_name="26428"
    )
    s_26458.add_input_file_config("sonic", gill_1, "sonic_26428", "TOA5_26428_sonic")
    s_26458.add_input_file_config("slow", trh_1, "slow_26428", "TOA5_26428_slow")
    s_26458.add_input_file_config("stat", stat_info, "stat_26428", "TOA5_26428_stat")

    #################################################################
    # --- ESECUZIONE PIPELINE ---

    print("Starting ETL Pipeline...")

    '''df = toa5_to_df_db("data/TOA5_Sonic_2026-03-26_00-03-23.dat", config=gill_2)
    print(df)'''

    database = "../empty_trieste_campaign.db"
    input_dir = "../26428_sd"
    stations = [s_26458]#, "26428", "6551", "4175", "4174"]

    with db.connect(database) as con:
        for station in stations:
            print(f"--- Processing Station {station.station_name} ---")
            #station_path = os.path.join(args.indir, station)
            fill_db_station_toa5(con, station, input_dir)
    print("Pipeline executed successfully.")

if __name__ == "__main__":
    main()

# main.py --db my_db.duckdb --indir /path/to/data