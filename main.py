from src import pre_processing as pp

path_file = "data/TOA5_Sonic_2026-03-26_04-01-54.dat"

df = pp.import_file(path_file)

# where value 999.99 put NAN
columns_meas = ['u_1', 'v_1', 'w_1', 'Ts_1']
condition = (df['SS_1'] != "0B") & (df['SS_1'] != "00") # from error status of gill windmaster
df[columns_meas] = df[columns_meas].mask(condition)

despiked = {}
for c in columns_meas:
    despiked[c], despiked['n_spike_'+c] = pp.despiking_series_robust(df[c], robust_std_dev=4, n_window_points=9, show_plot=False)

print(despiked)

'''ES3_10m_clean = pd.DataFrame({
     "u": u_clean,
     "v": v_clean,
     "w": w_clean,
     "T_s": ts_clean
 }, index=time)'''
