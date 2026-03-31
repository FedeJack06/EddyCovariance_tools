from src import tob3_to_toa5 as tt
from campbell import read_cs_files as cp

file_path = 'data-example/Slow_2026-03-26_00-01-34.dat'

# read file raw from campbell datalogger
data, meta = cp.read_cs_files(file_path, quiet= False, bycol=True)

# print META data, file header
for i in meta:
    print(i) 

# print data
print(data[0])