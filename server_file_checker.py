from tob3_py_converter.src import tob3_to_toa5 as tt
from src import pre_processing as pp

from pathlib import Path

path = Path("./data")
stringa_da_cercare = "Sonic_2026-03-26_00-01-34.dat"

# Usa rglob per cercare in questa cartella E in tutte le sottocartelle
# Usa glob se vuoi cercare SOLO nella cartella principale
file_trovati = path.glob(f"*{stringa_da_cercare}*") #.rglob

# file_trovati è un generatore, possiamo iterarlo
trovato_almeno_uno = False
for file in file_trovati:
    if file.is_file(): # Assicuriamoci che sia un file e non una cartella
        print(f"Find: {file}")
        trovato_almeno_uno = True
        result = tt.tob3toa5(file_path=file, out_dir=path)
        print(result)

if not trovato_almeno_uno:
    print("Nessun file trovato con quella stringa.")



