"""
File with an example of configuration of two stations.
Two stations with the same sensors but with different number
of vertical levels.
"""

from src.config import InputFileConfig, StationConfig

# --- CONFIG the input file type ---
#file type produced by one sonic anemometer
#expected variables: 3D wind speed (u_1, v_1, w_1) and sonic temperature Ts_1
gill_1 = InputFileConfig.gillwindmaster(n_levels=1, sampling_rate_ms=50)

#file type produced by one termoigrometer
#expected variables: air temperature AirTC1 and relative humidity RH1
trh_1 = InputFileConfig.defaultTermoigrometer(n_levels=1, sampling_rate_ms=1000)

#file type containing info about the station status (battery voltage and SD card status)
stat_info = InputFileConfig.defaultStatus(sampling_rate_ms=1000)

#file type produced by two sonic anemometer connected to the same station
#expected variables: 3D wind speed (u_1, v_1, w_1, u_2, v_2, w_2) and sonic temperature (Ts_1, Ts_2)
gill_2 = InputFileConfig.gillwindmaster(n_levels=2, sampling_rate_ms=50)

#file type produced by two termoigrometer connected to the same station
#expected variables: air temperature (AirTC1, AirTC2) and relative humidity (RH1, RH2)
trh_2 = InputFileConfig.defaultTermoigrometer(n_levels=2, sampling_rate_ms=1000)


# --- CONFIG the stations ---
#a station with one vertical level
s_4175 = StationConfig(
    station_name="4175"
)
#add the input file structure of the station
#Here, you specify which table each file type should be inserted into, and
#which is the common pattern for locating input files of the same type
s_4175.add_input_file_config(config_id="sonic", 
                             config=gill_1, 
                             db_table_name="sonic_4175", 
                             input_files_name="TOA5py_Sonic*")
s_4175.add_input_file_config(config_id="slow", 
                             config=trh_1, 
                             db_table_name="slow_4175", 
                             input_files_name="TOA5py_Slow*")
s_4175.add_input_file_config(config_id="stat", 
                             config=stat_info, 
                             db_table_name="stat_4175", 
                             input_files_name="TOA5py_Stat*")

#a station with 2 vertical levels
s_26458 = StationConfig(
    station_name="26458"
)
s_26458.add_input_file_config("sonic", gill_2, "sonic_26458", "TOA5py_Sonic*")
s_26458.add_input_file_config("slow", trh_2, "slow_26458", "TOA5py_Slow*")
s_26458.add_input_file_config("stat", stat_info, "stat_26458", "TOA5py_Stat*")