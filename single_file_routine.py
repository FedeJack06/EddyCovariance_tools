import sys
import os
from tob3_py_converter.src import tob3_to_toa5 as tt
from src import pre_processing as pp

if len(sys.argv) < 2:
    print("Errore: Nessun file passato in input.")
    sys.exit(1)

file_da_convertire = sys.argv[1]
cartella_parente = os.path.dirname(file_da_convertire)

if not os.path.exists(file_da_convertire):
    print(f"Errore: Il file {file_da_convertire} non esiste.")
    sys.exit(1)

print(f"Inizio la routine per: {file_da_convertire}")

dest_folder = cartella_parente+'/conv'

# ROUTINE

result = tt.tob3toa5(file_path=file_da_convertire, out_dir=dest_folder)
print(result)
