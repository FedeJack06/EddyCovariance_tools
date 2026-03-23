import pandas as pd
import os

data_path = '../26428/'

# Ottieni tutti i file dat ordinati alfabeticamente
files = sorted([f for f in os.listdir(data_path) if f.startswith('TOA5_Sonic') and f.endswith('.dat')])
print(f"Trovati {len(files)} file CSV da analizzare\n")

for file in files:
    filepath = os.path.join(data_path, file)

    try:
        # header:
        #"TIMESTAMP","RECORD","u_1","v_1","w_1","Ts_1","SS_1","ChkSumF_1","u_2","v_2","w_2","Ts_2","SS_2","ChkSumF_2"
        df = pd.read_csv(filepath, header=1, skiprows=[2, 3], dtype="string")

        if df.empty:
            print(f"Analizzando: {file}")
            print(f"File vuoto, skipping\n")
            continue

        type = [str]*1 + [int]*1 + [float]*4 + [str]*1 + [bool]*1 + [float]*4 + [str]*1 + [bool]*1
        dictionary = dict( zip(df.columns, type) )
        df = df.astype(dictionary)
        
        first_column = df.columns[0]
        df_temp = df.copy()
        df_temp[first_column] = pd.to_datetime(
            df_temp[first_column], 
            format='mixed', 
            errors='coerce'
        )

    except Exception as e:
        print(f"Analizzando: {file}")
        print(f"  ✗ Errore nel processare il file {file}: {e}")