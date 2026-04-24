from dataclasses import dataclass, field
from typing import Dict, Tuple, List

@dataclass
class InputFileConfig:
    """
    Configuration parameters for importing data from different file types. 
    Contains the structure of the input files and the database tables.
    The aim is putting in relation the name of the column in the input
    files and the name of the column in the database table and in the Pandas dataframe.

    If you want to import a column from files, you have to insert the column info
    as a new entry in the dictionary named cols:
    1) Set the name of the column in the input file, it will be the same in the Pandas
       dataframe related to the file (dictionary key)
    2) Set the Pandas type the column should have in the dataframe (first tuple entry)
    3) Set name of the same column in the table of the database (second tuple entry)
    4) Set column SQL type the column should have in the database (third tuple entry)

    Set the time interval in milliseconds between two measure in the input files.

    Three default profiles of input file are present, you can set these profile with
    the three methods. They refer to TOA5 input files generated from standard
    eddy covariance experiment.
    
    Attributes:
        cols: Dict[str, Tuple[type, str, str]]: Key is the name of the column in the input files.
              Value is a tuple contains in order, the pandas type of the column,
              the name of the column in the database table (can be different from file),
              the SQL type of the column in the table (used to create the table). 
    """
    sampling_rate_ms: float
    cols: Dict[str, Tuple[type, str, str]]

    @classmethod
    def gillwindmaster(cls, n_levels: int = 1, sampling_rate_ms: float = 50):
        """
        Set the configuration for standard sonic anemometers, with n vertical 
        levels (Gill Windmaster). For each level (identified by the number i) four
        variable are expected: u_i, v_i, w_i, three components of the wind and 
        Ts_i the sonic temperature. Gill Windmaster, with high precision enabled,
        generate measures with three decimal digits. The maximum value is 50 m/s so
        the database type for sonic measure can be DECIMAL(6,3), to save space. 
        Set the sampling rate for this type of measure.

        Attributes:
            n_levels: number of vertical levels or number of sonic instruments,
                      recorded in the same file.
            sampling_rate_ms: milliseconds between two measure. Default 50ms (20Hz).
        """
        if n_levels <= 0:
            raise ValueError("Number of level/instruments must be non zero and positive.")
        if not isinstance(n_levels, int):
            raise TypeError("Number of level/instruments must be an int.")
        
        cols_gill_windmaster = {}

        for i in range(1, n_levels + 1):
            cols_gill_windmaster["TIMESTAMP"] = ('datetime64[ms]', "datetime", "DATETIME PRIMARY KEY")
            cols_gill_windmaster[f"u_{i}"]  = (float, f"u_{i}", "DECIMAL(6,3)")
            cols_gill_windmaster[f"v_{i}"]  = (float, f"v_{i}", "DECIMAL(6,3)")
            cols_gill_windmaster[f"w_{i}"]  = (float, f"w_{i}", "DECIMAL(6,3)")
            cols_gill_windmaster[f"Ts_{i}"] = (float, f"ts_{i}", "DECIMAL(6,3)")
        
        # Create gill object
        return cls(
            cols = cols_gill_windmaster,
            sampling_rate_ms = sampling_rate_ms
        )
    
    @classmethod
    def defaultTermoigrometer(cls, n_levels: int = 1, sampling_rate_ms: float = 1000):
        """
        Set the configuration for standard termoigrometers, with n vertical 
        levels. For each level (identified by the number i) two
        variable are expected: AirTC{i}, air temperature and RH{i}, air relative 
        humidity. Standard slow termoigrometers (1Hz samplig rate)
        generate measures with one/two decimal digits, so the database
        type for these measure can be DECIMAL(5,2), to save space. 
        Set the sampling rate for this type of measure.

        Attributes:
            n_levels: number of vertical levels or number of termoigrometers,
                      recorded in the same file.
            sampling_rate_ms: milliseconds between two measure. Default 1s (1Hz).
        """
        if n_levels <= 0:
            raise ValueError("Number of level/instruments must be non zero and positive.")
        if not isinstance(n_levels, int):
            raise TypeError("Number of level/instruments must be an int.")
        
        cols_trh = {}

        for i in range(1, n_levels + 1):
            cols_trh["TIMESTAMP"] = ('datetime64[ms]', "datetime", "DATETIME PRIMARY KEY")
            cols_trh[f"AirTC{i}"] = (float, f"t_{i}", "DECIMAL(5,2)")
            cols_trh[f"RH{i}"] = (float, f"rh_{i}", "DECIMAL(5,2)")

        return cls(
            cols = cols_trh,
            sampling_rate_ms = sampling_rate_ms
        )

    @classmethod
    def defaultStatus(cls, sampling_rate_ms: float = 1000):
        """
        Set the configuration to read the status files. They contain info
        about the status of the station, for example a Campbell datalogger. 
        Here an example with battery voltage and info about the SD card
        where files are stored. Set the sampling rate for this type of measure.

        Attributes:
            sampling_rate_ms: milliseconds between two measure. Default 1s (1Hz).
        """
        cols_status = {
            "TIMESTAMP" : ('datetime64[ms]', "datetime", "DATETIME PRIMARY KEY"),
            "BattV_Min": (float, "battVmin", "DECIMAL(5,2)"),
            "CardStatus": (str, "card_status", "VARCHAR(10)")
        }

        return cls( 
            cols = cols_status,
            sampling_rate_ms = sampling_rate_ms
        )
    
    def get_file_cols_name(self) -> List[str]:
        """
        Return a list with the input file column names.
        """
        return list(self.cols.keys())
    
    def get_file_cols_type(self) -> Dict[str, str]:
        """
        Return a dictionary that maps the input file column name with 
        its type.

        Key: column name in the input file,
        Value: pandas type of the column.
        """
        dict = {}
        for key, value in self.cols.items():
            dict[key] = value[0]
        return dict
    
    def get_table_cols_name(self) -> Dict[str, str]:
        """
        Return a dictionary that maps the input file column name with 
        the column name in the database table.

        Key: column name in the input file,
        Value: column name in the database table.
        """
        dict = {}
        for key, value in self.cols.items():
            dict[key] = value[1]
        return dict
    
    def get_table_cols_type(self) -> Dict[str, str]:
        """
        Return a dictionary that maps the column name in the database table 
        with its SQL type. 

        Key: column name in the database table,
        Value: column SQL type in the database table.
        """
        dict = {}
        for value in self.cols.values():
            dict[value[1]] = value[2]
        return dict

@dataclass
class StationConfig:
    """
    Configuration parameters for a single station, identified by station_name,
    for example the serial number of a Campbell datalogger.
    The aim is use this class to contains all the info about the station data
    and related files.

    You can add to a single station multiple InputFileConfig (one for each type
    of input file), using add_input_file_config() method. You have to specify:
    1) An ID that identify the type of input file (e.g. sonic, slow, stat)
    2) A dictionary that associates the config_id and the name of the database table,
       which will contain data from all files of the same type
    3) A dictionary that associates the config_id and the pattern filename in
       all file names of the same type (e.g. S*.dat or *2026-05-10*)

    Attributes:
        station_name: name/id of the station
        db_table_names: dict with config_id as key and database table name as value
        input_files_name: dict with config_id as key and substring, contained in
                          all file names of the same type, as value
        input_files_config: dict with config_id as key and InputFileConfig as value
    """
    station_name: str
    db_table_names: Dict[str, str] = field(default_factory=dict)
    input_files_name: Dict[str, str] = field(default_factory=dict)
    input_files_config: Dict[str, 'InputFileConfig'] = field(default_factory=dict)

    def add_input_file_config(self, config_id: str, config: 'InputFileConfig', db_table_name: str, input_files_name: str):
        """
        Add new InputFileConfig object to the station.
        One config for each type of files generated from the station.

        Attributes:
            config_id: id of the input configuration files
            config: InputFileConfig object contains column info
            db_table_name: name of the database table, which will contain 
                           data from all files of the same type
            input_files_name: a wildcard pattern contained in all file names that 
                              match the stucture described in the config object
                              (e.g. S*.dat or *2026-05-10*)
        """
        self.input_files_config[config_id] = config
        self.db_table_names[config_id] = db_table_name
        self.input_files_name[config_id] = input_files_name

    def get_configs(self):
        """
        Get disctionary contains all InputFileConfig object
        """
        return self.input_files_config

    def get_input_config(self, config_id) -> InputFileConfig:
        """
        Get one InputFileConfig object given its config id

        Attributes:
            config_id: the id of the configuration to return
        """
        return self.input_files_config[config_id]
    
    def get_table_name(self, config_id):
        """
        Get the name of the table in the database, 
        given the the indetifier of the input config.

        Attributes:
            config_id: the id of the configuration
        """
        return self.db_table_names[config_id]
    
    def get_input_file_name(self, config_id) -> str:
        """
        Get the substring the file names must contains, to be imported, 
        given the the indetifier of the input config.

        Attributes:
            config_id: the id of the configuration
        """
        return self.input_files_name[config_id]

'''gill_2 = InputFileConfig.gillwindmaster(n_levels=2)
trh_2 = InputFileConfig.defaultTermoigrometer(n_levels=2)
stat_info = InputFileConfig.defaultStatus()

s_26458 = StationConfig(
    station_name="26458"
)
s_26458.add_input_file_config("sonic", gill_2, "sonic_26458", "TOA5_26458_sonic")
s_26458.add_input_file_config("slow", trh_2, "slow_26458", "TOA5_26458_slow")
s_26458.add_input_file_config("stat", stat_info, "stat_26458", "TOA5_26458_stat")'''

'''print(s_26458.get_configs())
print()
print(s_26458.get_input_config("sonic"))
print()
print(s_26458.get_input_file_name("sonic"))
print()
print(s_26458.get_table_name("sonic"))'''

'''print(gill_2.get_file_cols_name())
print()
print(gill_2.get_file_cols_type())
print()
print(gill_2.get_table_cols_name())
print()
print(gill_2.get_table_cols_type())'''

'''
StationConfig(
    station_name='26458', 
    db_table_names={
        'sonic': 'sonic_26458', 
        'slow': 'slow_26458', 
        'stat': 'stat_26458'
    }, 
    input_files_name={
        'sonic': 'TOA5_26458_sonic', 
        'slow': 'TOA5_26458_slow', 
        'stat': 'TOA5_26458_stat'
    }, 
    input_files_config={
        'sonic': InputFileConfig(
            cols={
                'TIMESTAMP': ('datetime64[ms]', 'datetime', 'DATETIME PRIMARY KEY'), 
                'u_1': (<class 'float'>, 'u_1', 'DECIMAL(6,3)'), 
                'v_1': (<class 'float'>, 'v_1', 'DECIMAL(6,3)'), 
                'w_1': (<class 'float'>, 'w_1', 'DECIMAL(6,3)'), 
                'Ts_1': (<class 'float'>, 'ts_1', 'DECIMAL(6,3)'), 
                'u_2': (<class 'float'>, 'u_2', 'DECIMAL(6,3)'), 
                'v_2': (<class 'float'>, 'v_2', 'DECIMAL(6,3)'), 
                'w_2': (<class 'float'>, 'w_2', 'DECIMAL(6,3)'), 
                'Ts_2': (<class 'float'>, 'ts_2', 'DECIMAL(6,3)')
            }
        ), 
        'slow': InputFileConfig(
            cols={
                'TIMESTAMP': ('datetime64[ms]', 'datetime', 'DATETIME PRIMARY KEY'), 
                'AirTC1': (<class 'float'>, 't_1', 'DECIMAL(5,2)'), 
                'RH1': (<class 'float'>, 'rh_1', 'DECIMAL(5,2)'), 
                'AirTC2': (<class 'float'>, 't_2', 'DECIMAL(5,2)'), 
                'RH2': (<class 'float'>, 'rh_2', 'DECIMAL(5,2)')
            }
        ), 
        'stat': InputFileConfig(
            cols={
                'TIMESTAMP': ('datetime64[ms]', 'datetime', 'DATETIME PRIMARY KEY'), 
                'BattV_Min': (<class 'float'>, 'battVmin', 'DECIMAL(5,2)'), 
                'CardStatus': (<class 'str'>, 'card_status', 'VARCHAR(10)')
            }
        )
    }
)
'''