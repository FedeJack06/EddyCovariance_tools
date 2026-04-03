import pandas as pd
from src import despike

path_file = "data/TOA5_Sonic_2026-03-26_04-01-54.dat"

df = pd.read_csv(path_file, sep=",", header=0, skiprows=[0,2,3], dtype="string")#, dtype='float', parse_dates=[[0,1]], encoding='ISO-8859-1')
type_list = [str]*1 + [int]*1 + [float]*4 + [str]*1 + [bool]*1
dictionary = dict( zip(df.columns, type_list) )
df = df.astype(dictionary)

first_column = df.columns[0]
# Converte la colonna in datetime
df[first_column] = pd.to_datetime(
    df[first_column], 
    format='mixed', 
    errors='coerce'
)

df.set_index('TIMESTAMP', inplace=True)
df.drop(columns=['TIMESTAMP'], inplace=True, errors='ignore')
df.drop(columns=['RECORD'], inplace=True)

# where value 999.99 put NAN
columns_meas = ['u_1', 'v_1', 'w_1', 'Ts_1']
condition = (df['SS_1'] != "0B") & (df['SS_1'] != "00") # from error status of gill windmaster
df[columns_meas] = df[columns_meas].mask(condition)

despiked, n_spike = despike.despiking_series_robust(df.w_1, robust_std_dev=4, n_window_points=10, show_plot=True)
