from src import pre_processing as pp

out_dir = "./data/"
in_dir = "./data/"

field_sonic =  ['u_1', 'v_1', 'w_1', 'Ts_1', 'u_2', 'v_2', 'w_2', 'Ts_2']
field_slow = ["AirTC1","RH1","AirTC2","RH2"]

slow_df, h_slow = pp.import_file(in_dir+"TOA5_Slow_2026-03-26_00-01-34.dat", measure_fields=field_slow, clear_df=True)
sonic_df, h_sonic = pp.import_file(in_dir+"TOA5_Sonic_2026-03-26_00-03-23.dat", measure_fields=field_sonic, clear_df=True)
stat_df, h_stat = pp.import_file(in_dir+'TOA5_Stat_2026-03-26_00-02-24.dat', measure_fields=['BattV_Min'])

print(slow_df)
print(sonic_df)
print(stat_df)

############# 999.99 as NAN in Sonic file
sonic_df = sonic_df.mask(sonic_df > 999) 

############# Despike
sonic_despiked = {}
for c in field_sonic:
    sonic_despiked[c], sonic_despiked['n_spike_'+c] = pp.despiking_series_robust(sonic_df[c], robust_std_dev=4, n_window_points=9, show_plot=False)

print(sonic_despiked)

slow_despiked = {}
for c in field_slow:
    slow_despiked[c], slow_despiked['n_spike_'+c] = pp.despiking_series_robust(slow_df[c], robust_std_dev=4, n_window_points=9, show_plot=False)

print(slow_despiked)