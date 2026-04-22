from src.tob3_to_toa5 import tob3toa5
from pathlib import Path
import logging
import sys

def setup_logging():
    """Configures global logging: INFO to stdout, ERROR to error.log."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Handler for errors (name_scritp.out)
    error_handler = logging.FileHandler(__file__+".log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))

    # Handler for standard output (terminal)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

    root_logger.addHandler(error_handler)
    root_logger.addHandler(stdout_handler)

setup_logging()

path = Path("../26428_sd")
pattern = "2*.dat"

# Usa rglob per cercare in questa cartella E in tutte le sottocartelle
# Usa glob se vuoi cercare SOLO nella cartella principale
file_trovati = path.glob(pattern) #.rglob

# file_trovati è un generatore, possiamo iterarlo
trovato_almeno_uno = False
for file in file_trovati:
    if file.is_file(): # Assicuriamoci che sia un file e non una cartella
        print(f"Find: {file}")
        trovato_almeno_uno = True
        tob3toa5(file_path = file,
                 out_dir = path,
                 prefix = "TOA5py_",
                 suffix = "",
                 decimals = 3)


if not trovato_almeno_uno:
    print("Nessun file trovato con quella stringa.")



