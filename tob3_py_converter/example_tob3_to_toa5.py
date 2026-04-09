from src import tob3_to_toa5 as tt

slow = 'data-example/Slow_2026-03-26_00-01-34.dat'
slow_path = tt.tob3toa5(file_path=slow, out_dir="data-example/")

sonic = 'data-example/Sonic_2026-03-26_00-03-23.dat'
sonic_path = tt.tob3toa5(file_path=sonic, out_dir="data-example/")

stat = 'data-example/Stat_2026-03-26_00-02-24.dat'
stat_path = tt.tob3toa5(file_path=stat, out_dir="data-example/")