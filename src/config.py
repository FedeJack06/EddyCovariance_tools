from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class InputFileConfig:
    """
    Configuration parameters for importing data from different files.
    
    Attributes:
        files_name: filename containing this string will be loaded
        db_table_prefix: prefix for table name in the database. 
                         Final table name will be {prefix}_{station_name}
        cols: column names in the file, their type, 
              column names in the database table, their type
    """
    file_name: str
    cols: Dict[str, Tuple[type, str, str]]

    @classmethod
    def gillwindmaster(cls, file_name: str = "Sonic", n_levels: int = 1):
        """
        Constructor for standard Gill Windmaster with n_levels sonic anemometer.
        One sonic for each level.
        """
        if n_levels <= 0:
            raise ValueError("Number of level/instruments must be non zero and positive.")
        if not isinstance(n_levels, int):
            raise TypeError("Number of level/instruments must be an int.")
        
        cols_gill_windmaster = {}

        for i in range(1, n_levels + 1):
            cols_gill_windmaster[f"u_{i}"]  = (float, f"u_{i}", "DECIMAL(6,3)")
            cols_gill_windmaster[f"v_{i}"]  = (float, f"v_{i}", "DECIMAL(6,3)")
            cols_gill_windmaster[f"w_{i}"]  = (float, f"w_{i}", "DECIMAL(6,3)")
            cols_gill_windmaster[f"Ts_{i}"] = (float, f"ts_{i}", "DECIMAL(6,3)")
        
        # Create gill object
        return cls(
            file_name = file_name, 
            cols = cols_gill_windmaster
        )
    
    @classmethod
    def defaultTermoigrometer(cls, file_name: str = "Slow", n_levels: int = 1):
        """
        Constructor fro standard file from termoigrometer.
        Temperature and relative humidity with max 2 decimal of precision.
        One instrumento for each level.
        """
        if n_levels <= 0:
            raise ValueError("Number of level/instruments must be non zero and positive.")
        if not isinstance(n_levels, int):
            raise TypeError("Number of level/instruments must be an int.")
        
        cols_trh = {}

        for i in range(1, n_levels + 1):
            cols_trh[f"AirTC{i}"] = (float, f"t_{i}", "DECIMAL(5,2)")
            cols_trh[f"RH{i}"] = (float, f"rh_{i}", "DECIMAL(5,2)")

        return cls(
            file_name = file_name, 
            cols = cols_trh
        )

    @classmethod
    def defaultStatus(cls, file_name: str = "Stat"):
        """
        Constructor for the structur of default status files, 
        containing info about status of the battery and SD card of the station.
        """
        cols_status = {
            "BattV_Min": (float, "battVmin", "DECIMAL(5,2)"),
            "CardStatus": (str, "card_status", "VARCHAR(10)")
        }

        return cls(
            file_name = file_name, 
            cols = cols_status
        )

@dataclass
class StationConfig:
    station_name: str
    db_table_names: Dict[str, str]
    input_files: List[InputFileConfig]

'''
gill_2 = InputFileConfig.gillwindmaster(n_levels=2)
trh_2 = InputFileConfig.defaultTermoigrometer(n_levels=2)
stat_info = InputFileConfig.defaultStatus()

s_26458 = StationConfig(station_name="26458", 
                              db_table_names= {
                                  "Sonic" : "sonic_26458",
                                  "Slow" : "slow_26458",
                                  "Stat": "stat_26458"
                              },
                              input_files = [gill_2, trh_2, stat_info])

print(s_26458)

#Output:
StationConfig(
    station_name='26458', 
    db_table_names={
        'Sonic': 'sonic_26458', 
        'Slow': 'slow_26458', 
        'Stat': 'stat_26458'
    },
    input_files=[   
        InputFileConfig(
            file_name='Sonic', 
            cols={
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
        InputFileConfig(
            file_name='Slow',
            cols={
                'AirTC1': (<class 'float'>, 't_1', 'DECIMAL(5,2)'), 
                'RH1': (<class 'float'>, 'rh_1', 'DECIMAL(5,2)'), 
                'AirTC2': (<class 'float'>, 't_2', 'DECIMAL(5,2)'), 
                'RH2': (<class 'float'>, 'rh_2', 'DECIMAL(5,2)')
            }
        ), 
        InputFileConfig(
            file_name='Stat', 
            cols={
                'BattV_Min': (<class 'float'>, 'battVmin', 'DECIMAL(5,2)'), 
                'CardStatus': (<class 'str'>, 'card_status', 'VARCHAR(10)')
            }
        )
    ]
)
'''