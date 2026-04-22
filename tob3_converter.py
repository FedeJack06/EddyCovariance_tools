from pathlib import Path
from src.tob3_to_toa5 import tob3toa5
from src.utils import setup_logging

setup_logging(__file__)

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