"""
Script to convert all TOB3 files from a directory to TOA5 files.
TOA5 will be saved in the same folder, adding "TOA5py_" suffix in the name.
"""
from EddyCovTools.tob3_to_toa5 import tob3toa5
from EddyCovTools.utils import setup_logging
from EddyCovTools.file_manager import get_files_pattern

# create a .log file with all the errors
setup_logging(__file__)

# input directory and files
working_dir = "./data/station_26458"
pattern = "S*"

files = get_files_pattern(folder_path=working_dir, pattern=pattern)
for file in files:
    if file.is_file():
        print(f"Find: {file}")
        tob3toa5(file_path = file,
                 out_dir = working_dir,
                 prefix = "TOA5py_",
                 suffix = "",
                 decimals = 3)