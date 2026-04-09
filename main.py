from src import pre_processing as pp
from tob3_py_converter.src import tob3_to_toa5 as tt

out_path = "./data"

############# TOB3 TO TOA5
'''path_file = "data/Slow_2026-03-26_00-01-34.dat"

result = tt.tob3toa5(file_path=path_file, out_dir=out_path)
print(result)'''

############# Check folder

#pp.chech_TOA5('../2026-03-26/26458', dt_max_ms=1000, start_name="TOA5_Slow", end_name=".dat", out_file=True)

############# Despike
#path_file = "data/TOA5py_Sonic_2026-03-26_00-03-23.dat"
'''path_file = "data/TOA5py_Slow_2026-03-26_00-01-34.dat"

df, meta = pp.import_file(path_file)

# where value 999.99 put NAN
#columns_meas = ['u_1', 'v_1', 'w_1', 'Ts_1']
columns_meas = ["AirTC1","RH1","AirTC2","RH2"]

#condition = (df['SS_1'] != "0B") & (df['SS_1'] != "00") # from error status of gill windmaster
#df[columns_meas] = df[columns_meas].mask(condition)

despiked = {}
for c in columns_meas:
    despiked[c], despiked['n_spike_'+c] = pp.despiking_series_robust(df[c], robust_std_dev=4, n_window_points=9, show_plot=True)

print(despiked)'''

'''despiked = pd.DataFrame({
     "u": u,
     "v": v,
     "w": w,
     "T_s": ts
 }, index=time)'''

############ Despike from TOA5
#path_file = "data/TOA5py_Sonic_2026-03-26_00-03-23.dat"
#path_file = "data/TOA5py_Slow_2026-03-26_00-01-34.dat"

#file_desp = pp.despiking_TOA5_robust(path_file, out_path=out_path, robust_std_dev=4, n_window_points=9, show_plot=True)

#pp.daily_file_from_server("../2026-03-26/4175", "./data", "TOA5_", ".dat")

pp.chech_TOA5('./data', dt_max_ms=50, start_name="TOA5_Sonic_2026-03-26_Dail", end_name=".dat", out_file=False)

#pp.import_file('./data/TOA5_Sonic_2026-03-26_Daily.dat')