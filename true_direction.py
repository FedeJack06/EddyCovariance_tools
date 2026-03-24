import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

def load_and_merge_sonic_data(folder_path):
    """
    Legge, unisce e ordina cronologicamente i file TOA5_Sonic da una cartella.
    
    Args:
        folder_path (str): Il percorso della cartella contenente i file .dat.
        
    Returns:
        pd.DataFrame: Un singolo DataFrame contenente tutti i dati puliti e ordinati. 
                      Restituisce un DataFrame vuoto in caso di errore o assenza di file.
    """
    # Ottieni tutti i file dat ordinati alfabeticamente
    files = sorted([f for f in os.listdir(folder_path) if f.startswith('TOA5_Sonic') and f.endswith('.dat')])
    print(f"Trovati {len(files)} file da analizzare in '{folder_path}'\n")

    # Contenitore per i dataframes
    df_list = []

    for file in files:
        filepath = os.path.join(folder_path, file)

        try:
            df = pd.read_csv(filepath, header=1, skiprows=[2, 3], dtype="string")

            if df.empty:
                print(f"Analizzando: {file} -> File vuoto, skipping")
                continue

            # Calcola il numero di livelli verticali nel file
            number_of_level = int((df.shape[1]-2)/6)

            # Crea e applica il dizionario dei tipi
            type_list = [str]*1 + [int]*1 + ( [float]*4 + [str]*1 + [bool]*1 ) * number_of_level
            dictionary = dict( zip(df.columns, type_list) )
            df = df.astype(dictionary)
            
            first_column = df.columns[0] # Colonna datetime
            
            # Converti la prima colonna in datetime
            df[first_column] = pd.to_datetime(
                df[first_column], 
                format='mixed', 
                errors='coerce'
            )
            
            # Rimuovi i TIMESTAMP non validi (NaT)
            df = df.dropna(subset=[first_column])

            # Aggiungi alla lista
            df_list.append(df)

        except Exception as e:
            print(f"  ✗ Errore nel processare il file {file}: {e}")

    # Unisci tutti i df in uno solo
    if df_list:
        all_df = pd.concat(df_list, ignore_index=True)
        
        # Ordina per data crescente
        first_column = all_df.columns[0]
        all_df = all_df.sort_values(by=first_column, ascending=True)
        
        # Resetta l'indice
        all_df = all_df.reset_index(drop=True)

        #find rows with at least one 999.99 record
        row_999 = (all_df == 999.999).any(axis=1)

        all_df_clean = all_df[~row_999]

        all_df_clean = all_df_clean.reset_index(drop=True)
        
        print("\nUnione completata con successo!")
        print(f"Dimensione totale del DataFrame: {all_df.shape}")
        
        return all_df_clean
    else:
        print("\nNessun file elaborato con successo. Il DataFrame finale è vuoto.")
        return pd.DataFrame()

def wind_dir(df):
    _df = df.copy()
    number_of_level = int((_df.shape[1]-2)/6)
    
    #set datetime as df index
    _df.set_index('TIMESTAMP', inplace=True)

    col_wind_name = []
    for i in range(number_of_level):
        col_wind_name.append(f'u_{i+1}')
        col_wind_name.append(f'v_{i+1}')

    # average of u_1 e v_1 over 5 min ('5min' or '5T')
    df_5min = _df[col_wind_name].resample('5min').mean()

    # sonic coordinate system
    # u > 0: to Nord
    # v > 0: to West
    #WIND TO:
    #df_5min['wind_dir_deg'] = (np.degrees(np.arctan2(-df_5min['v_1'], df_5min['u_1']))) % 360
    # WIND FROM:
    df_5min['wind_dir_1'] = (np.degrees(np.arctan2(df_5min['v_1'], -df_5min['u_1']))) % 360

    # wind speed
    df_5min['wind_speed_1'] = np.sqrt(df_5min['u_1']**2 + df_5min['v_1']**2)

    if number_of_level == 2:
        # WIND FROM:
        df_5min['wind_dir_2'] = (np.degrees(np.arctan2(df_5min['v_2'], -df_5min['u_2']))) % 360

        # wind speed
        df_5min['wind_speed_2'] = np.sqrt(df_5min['u_2']**2 + df_5min['v_2']**2)


    # reset index
    df_5min.reset_index(inplace=True)
    return df_5min

df_6551 = load_and_merge_sonic_data('../6551/')
df_26458 = load_and_merge_sonic_data('../26458/')
df_26428 = load_and_merge_sonic_data('../26428/')

print(df_6551.u_1.max())
print(df_6551.v_1.max())

df_6551_avg = wind_dir(df_6551)
df_26458_avg = wind_dir(df_26458)
df_26428_avg = wind_dir(df_26428)
print(type(df_6551_avg['TIMESTAMP']))

plt.figure(1)
plt.plot(df_6551_avg['TIMESTAMP'], df_6551_avg['wind_dir_1'], label="Medica")
plt.plot(df_26428_avg['TIMESTAMP'], df_26428_avg['wind_dir_1'], label ="Chirurgica")
plt.plot(df_26458_avg['TIMESTAMP'], df_26458_avg['wind_dir_1'], label = "E1")
plt.plot(df_26458_avg['TIMESTAMP'], df_26458_avg['wind_dir_2'], label = "E2")
plt.legend()

plt.figure(2)
plt.plot(df_6551_avg['TIMESTAMP'], df_6551_avg['wind_speed_1'], label="Medica")
plt.plot(df_26428_avg['TIMESTAMP'], df_26428_avg['wind_speed_1'], label ="Chirurgica")
plt.plot(df_26458_avg['TIMESTAMP'], df_26458_avg['wind_speed_1'], label = "E1")
plt.plot(df_26458_avg['TIMESTAMP'], df_26458_avg['wind_speed_2'], label = "E2")
plt.legend()

plt.show()
