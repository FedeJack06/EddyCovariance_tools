from tob3_py_converter.src import tob3_to_toa5 as tt

from pathlib import Path

path = Path("/media/federico/BackupFoto/trieste_campaign/26458")
start_name = "S"
end_name = ".dat"

# Usa rglob per cercare in questa cartella E in tutte le sottocartelle
# Usa glob se vuoi cercare SOLO nella cartella principale
file_trovati = path.glob(f"{start_name}*{end_name}") #.rglob

# file_trovati è un generatore, possiamo iterarlo
trovato_almeno_uno = False
for file in file_trovati:
    if file.is_file(): # Assicuriamoci che sia un file e non una cartella
        print(f"Find: {file}")
        trovato_almeno_uno = True
        result = tt.tob3toa5(file_path = file,
                            out_dir = path,
                            prefix = "TOA5py_",
                            suffix = "",
                            decimals = 3)

if not trovato_almeno_uno:
    print("Nessun file trovato con quella stringa.")



