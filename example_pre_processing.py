from src import pre_processing as pp

#################################################################
# --- CONFIG ---
from station_config import *

out_dir = "./data/"
in_dir = "./data/"

slow_df, h_slow = pp.toa5_to_df(in_dir+"TOA5_Slow_2026-03-26_00-01-34.dat", config=trh_2, date_index=True)
sonic_df, h_sonic = pp.toa5_to_df(in_dir+"TOA5_Sonic_2026-03-26_00-03-23.dat", config=gill_2, date_index=True)
stat_df, h_stat = pp.toa5_to_df(in_dir+'TOA5_Stat_2026-03-26_00-02-24.dat', config=stat_info, date_index=True)

print(slow_df)
print(sonic_df)
print(stat_df)

############# 999.99 as NAN in df
sonic_df = pp.filter_df_toa5(sonic_df)
slow_df = pp.filter_df_toa5(slow_df)

############# check NAN and gaps
gaps_sonic, nan_sonic, nan_dt_sonic = pp.check_df(sonic_df, sampling_rate_ms=50)
gaps_slow, nan_slow, nan_dt_slow = pp.check_df(slow_df, sampling_rate_ms=1000)
print(gaps_sonic)
print(nan_sonic)
print(nan_dt_sonic)

############# Despike
sonic_despiked = {}
for c in sonic_df.columns:
    sonic_despiked[c], sonic_despiked['n_spike_'+c] = pp.despiking_series_robust(sonic_df[c], robust_std_dev=4, n_window_points=9, show_plot=False)

#print(sonic_despiked)

slow_despiked = {}
for c in slow_df.columns:
    slow_despiked[c], slow_despiked['n_spike_'+c] = pp.despiking_series_robust(slow_df[c], robust_std_dev=4, n_window_points=9, show_plot=False)

#print(slow_despiked)