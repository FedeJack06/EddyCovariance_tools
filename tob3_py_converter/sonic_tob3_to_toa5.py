from src import tob3_to_toa5 as tt

file_path = 'data-example/Sonic_2026-03-26_00-03-23.dat'

result = tt.tob3toa5(file_path=file_path, out_dir="data-example/")
print(result)