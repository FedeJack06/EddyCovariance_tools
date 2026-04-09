from src import pre_processing as pp

out_dir = "./data/"
in_dir = "./data/"

slow_df, h_slow = pp.import_file(in_dir+"TOA5_Slow_2026-03-26_00-01-34.dat")
sonic_df, h_sonic = pp.import_file(in_dir+"TOA5_Sonic_2026-03-26_00-03-23.dat")
stat_df, h_stat = pp.import_file(in_dir+'TOA5_Stat_2026-03-26_00-02-24.dat')

print(slow_df)
print(sonic_df)
print(stat_df)