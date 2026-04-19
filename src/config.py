from dataclasses import dataclass, field
from typing import Dict, Tuple, List

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
    def gillwindmaster(cls, file_name: str = "sonic", n_levels: int = 1):
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
            cols_gill_windmaster["TIMESTAMP"] = ('datetime64[ms]', "datetime", "DATETIME PRIMARY KEY")
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
    def defaultTermoigrometer(cls, file_name: str = "slow", n_levels: int = 1):
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
            cols_trh["TIMESTAMP"] = ('datetime64[ms]', "datetime", "DATETIME PRIMARY KEY")
            cols_trh[f"AirTC{i}"] = (float, f"t_{i}", "DECIMAL(5,2)")
            cols_trh[f"RH{i}"] = (float, f"rh_{i}", "DECIMAL(5,2)")

        return cls(
            file_name = file_name, 
            cols = cols_trh
        )

    @classmethod
    def defaultStatus(cls, file_name: str = "stat"):
        """
        Constructor for the structur of default status files, 
        containing info about status of the battery and SD card of the station.
        """
        cols_status = {
            "TIMESTAMP" : ('datetime64[ms]', "datetime", "DATETIME PRIMARY KEY"),
            "BattV_Min": (float, "battVmin", "DECIMAL(5,2)"),
            "CardStatus": (str, "card_status", "VARCHAR(10)")
        }

        return cls(
            file_name = file_name, 
            cols = cols_status
        )
    
    def get_file_cols_name(self) -> List[str]:
        """
        Return a list of column name of the input files
        """
        return list(self.cols.keys())
    
    def get_file_cols_type(self) -> Dict[str, str]:
        """
        Key: column name in the input file,
        Value: column type in the input file
        """
        dict = {}
        for key, value in self.cols.items():
            dict[key] = value[0]
        return dict
    
    def get_table_cols_name(self) -> Dict[str, str]:
        """
        Key: column name in the input file,
        Value: column name in the database table
        """
        dict = {}
        for key, value in self.cols.items():
            dict[key] = value[1]
        return dict
    
    def get_table_cols_type(self) -> Dict[str, str]:
        """
        Key: column name in the database table,
        Value: column type in the database table
        """
        dict = {}
        for value in self.cols.values():
            dict[value[1]] = value[2]
        return dict

@dataclass
class StationConfig:
    station_name: str
    db_table_names: Dict[str, str] = field(default_factory=dict)
    input_files: Dict[str, 'InputFileConfig'] = field(default_factory=dict)

    def add_input_file_config(self, config_id: str, config: 'InputFileConfig', db_table_name: str):
        """
        Add new InputFileConfig object to the station.
        """
        self.input_files[config_id] = config
        self.db_table_names[config_id] = db_table_name

    def get_files_config(self):
        """
        Get disctionary contains InputFileConfig object
        """
        return self.input_files

    def get_input_config(self, config_id) -> InputFileConfig:
        """
        Get one InputFileConfig object with its id
        """
        return self.input_files[config_id]
    
    def get_table_name(self, config_id):
        """
        Return the name of the table in the database, 
        given the the indetifier of the input config.
        """
        return self.db_table_names[config_id]

'''gill_2 = InputFileConfig.gillwindmaster(n_levels=2)
trh_2 = InputFileConfig.defaultTermoigrometer(n_levels=2)
stat_info = InputFileConfig.defaultStatus()

s_26458 = StationConfig(
    station_name="26458"
)
s_26458.add_input_file_config("sonic", gill_2, "sonic_26458")
s_26458.add_input_file_config("slow", trh_2, "slow_26458")
s_26458.add_input_file_config("stat", stat_info, "stat_26458")

print(s_26458)'''
'''
#Output:
StationConfig(
    station_name='26458', 
    db_table_names={
        'sonic': 'sonic_26458', 
        'slow': 'slow_26458', 
        'stat': 'stat_26458'
    }, 
    input_files={
        'sonic': InputFileConfig(
            file_name='sonic',
            cols={
                'TIMESTAMP': (<class 'datetime', 'datetime', 'DATETIME PRIMARY KEY'),
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
            file_name='slow', 
            cols={
                'TIMESTAMP': (<class 'datetime', 'datetime', 'DATETIME PRIMARY KEY'),
                'AirTC1': (<class 'float'>, 't_1', 'DECIMAL(5,2)'), 
                'RH1': (<class 'float'>, 'rh_1', 'DECIMAL(5,2)'), 
                'AirTC2': (<class 'float'>, 't_2', 'DECIMAL(5,2)'), 
                'RH2': (<class 'float'>, 'rh_2', 'DECIMAL(5,2)')
            }
        ), 
        'stat': InputFileConfig(
            file_name='stat', 
            cols={
                'TIMESTAMP': (<class 'datetime', 'datetime', 'DATETIME PRIMARY KEY'),
                'BattV_Min': (<class 'float'>, 'battVmin', 'DECIMAL(5,2)'), 
                'CardStatus': (<class 'str'>, 'card_status', 'VARCHAR(10)')
            }
        )
    }
)
'''

'''
# Ottenere il nome del file
nome_del_file = config_gill.file_name
print(f"Nome file: {nome_del_file}") 
# Output: Nome file: sonic_data

# Ottenere l'intero dizionario delle colonne
tutte_le_colonne = config_gill.cols
print(f"Dizionario completo: {tutte_le_colonne}")
# Output: {'u_1': (<class 'float'>, 'u_1', 'DECIMAL(6,3)'), 'v_1': ... }

# Accedere alla tupla di configurazione per la colonna "w_1"
config_w1 = config_gill.cols["w_1"]
print(f"Configurazione w_1: {config_w1}")
# Output: Configurazione w_1: (<class 'float'>, 'w_1', 'DECIMAL(6,3)')

# Estrarre la tupla per comodità
tupla_w1 = config_gill.cols["w_1"]

# Indice 0: Il tipo (es. float)
tipo_python = tupla_w1[0]

# Indice 1: Il nome della colonna nel DB (es. 'w_1')
nome_db = tupla_w1[1]

# Indice 2: Il tipo della colonna nel DB (es. 'DECIMAL(6,3)')
tipo_db = tupla_w1[2]

print(f"w_1 -> Python type: {tipo_python.__name__}, DB Name: {nome_db}, DB Type: {tipo_db}")
# Output: w_1 -> Python type: float, DB Name: w_1, DB Type: DECIMAL(6,3)

# In alternativa, puoi concatenare gli accessi (sconsigliato se la riga diventa troppo lunga):
tipo_db_v2 = config_gill.cols["v_2"][2]
print(f"Tipo DB per v_2: {tipo_db_v2}")

for file_col_name, (py_type, db_col_name, db_type) in config_gill.cols.items():
    print(f"Colonna nel file: {file_col_name}")
    print(f"  - Castare a tipo: {py_type.__name__}")
    print(f"  - Salvare nel DB come: {db_col_name}")
    print(f"  - Tipo dato DB: {db_type}")
    print("-" * 20)
'''