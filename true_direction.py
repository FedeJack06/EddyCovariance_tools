import pandas as pd
import os

data_path = '../26428/'

#Sort filename from folder
files = sorted([f for f in os.listdir(data_path) if f.startswith('TOA5_Sonic') and f.endswith('.dat')])
print(f"Trovati {len(files)} file CSV da analizzare\n")

# dataframes container
df_list = []

for file in files:
    filepath = os.path.join(data_path, file)

    try:
        df = pd.read_csv(filepath, header=1, skiprows=[2, 3], dtype="string")

        if df.empty:
            print(f"Analizzando: {file}")
            print(f"File vuoto, skipping\n")
            continue

        #calculate the number of vertical level in the file
        number_of_level = int((df.shape[1]-2)/6)
        print(number_of_level)

        # header:
        #"TIMESTAMP","RECORD","u_1","v_1","w_1","Ts_1","SS_1","ChkSumF_1","u_2","v_2","w_2","Ts_2","SS_2","ChkSumF_2"
        type_list = [str]*1 + [int]*1 + ( [float]*4 + [str]*1 + [bool]*1 )*number_of_level
        dictionary = dict( zip(df.columns, type_list) )
        df = df.astype(dictionary)
        
        first_column = df.columns[0] #datetime column
        
        # first column to datetime
        df[first_column] = pd.to_datetime(
            df[first_column], 
            format='mixed', 
            errors='coerce'
        )
        
        # remove NaN TIMESTAMP
        df = df.dropna(subset=[first_column])

        # append df to list
        df_list.append(df)

    except Exception as e:
        print(f"Analizzando: {file}")
        print(f"  ✗ Errore nel processare il file {file}: {e}")

# Merge all df into one
if df_list:
    all_df = pd.concat(df_list, ignore_index=True)
    
    # order by date asc
    first_column = all_df.columns[0]
    all_df = all_df.sort_values(by=first_column, ascending=True)
    
    # index reset
    all_df = all_df.reset_index(drop=True)
    
    print("\nUnione completata!")
    print(f"Dimensione totale del DataFrame: {all_df.shape}")
    print(all_df)
else:
    print("\nNessun file elaborato con successo. Il DataFrame finale è vuoto.")
    df_finale = pd.DataFrame() # Crea un df vuoto di fallback

