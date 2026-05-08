"""
Script to convert all TOB3 files from a directory to TOA5 files.
TOA5 will be saved in the same folder, adding "TOA5py_" suffix in the name.
"""

from pathlib import Path
from src.tob3_to_toa5 import tob3toa5
from src.utils import setup_logging

# create a .log file with all the errors
setup_logging(__file__)

# input directory and files
working_dir = Path("")
pattern = "*2026-04-1*"

# get files list
files = sorted(working_dir.glob(pattern)) #.rglob if you want a recursively search

find_files = False
for file in files:
    # if is a file convert it!
    if file.is_file():
        print(f"Find: {file}")
        find_files = True

        tob3toa5(file_path = file,
                 out_dir = working_dir,
                 prefix = "TOA5py_",
                 suffix = "",
                 decimals = 3)

if not find_files:
    print("Files not found")