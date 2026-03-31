import sys
from pathlib import Path
import csv
from datetime import datetime

# find tob3-py-converter folder absolute path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from campbell import read_cs_files as cp

def tob3toa5(file_path, out_dir, prefix="TOA5py_", suffix="_converted", decimals=6):
    """
    Reads a Campbell Scientific TOB3 file and converts it to a TOA5 format file.
    
    Args:
        file_path (str or Path): The path to the input TOB3 file.
        out_dir (str or Path): The directory where the new file will be saved.
        prefix (str): Text to prepend to the original filename.
        suffix (str): Text to append to the original filename.
        decimals (int): Number of decimal places to round floating-point numbers to.
        
    Returns:
        Path: The full path to the newly created TOA5 file.
    """
    # Convert inputs to Path objects for robust path manipulation
    file_path = Path(file_path)
    out_dir = Path(out_dir)
    
    # Create the output directory if it doesn't exist yet
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Construct the new filename
    out_filename = f"{prefix}{file_path.stem}{suffix}{file_path.suffix}"
    out_path = out_dir / out_filename

    # Read file raw from campbell datalogger
    data, meta = cp.read_cs_files(str(file_path), quiet=False, bycol=False)
    
    # Safety check: ensure file was read correctly
    if not data or not meta:
        print(f"Error reading data from {file_path}")
        return None

    # Change the file type declaration in the first header
    if len(meta) > 0 and len(meta[0]) > 0:
        meta[0][0] = "TOA5py"

    del meta[1] #remove useless row in header
    del meta[4]

    print(f"Writing TOA5 file to: {out_path}")

    # Write data to the new file
    with open(out_path, mode='w', newline='', encoding='ascii') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        # Write the 4 metadata headers
        for header_line in meta:
            writer.writerow(header_line)

        # Write the data rows
        for row in data:
            formatted_row = []
            for item in row:
                if isinstance(item, datetime):
                    # Timestamps must be strings so they get quotes
                    formatted_row.append(item.strftime('%Y-%m-%d %H:%M:%S'))
                elif isinstance(item, float):
                    # Round floats to clean up IEEE 754 precision artifacts.
                    # By keeping it as a float, the CSV writer will NOT add quotes around it.
                    formatted_row.append(round(item, decimals))
                else:
                    # Catch-all for integers or other types
                    formatted_row.append(item)
                    
            writer.writerow(formatted_row)

    return out_path