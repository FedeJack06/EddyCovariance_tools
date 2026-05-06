import logging
from pathlib import Path
import csv
from datetime import datetime
from .campbell import read_cs_files as cp

logger = logging.getLogger(__name__)

def tob3toa5(file_path, out_dir, prefix="TOA5py_", suffix="", decimals=3):
    """
    Reads a Campbell Scientific TOB3 file and converts it to a TOA5 format file.
    Works for both Slow (low frequency) and Sonic (high frequency) data.
    
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
    try:
        data, meta = cp.read_cs_files(file_path, quiet=False, bycol=False)
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}.")
        return None

    # Safety check: ensure file was read correctly
    if not data or not meta:
        logger.warning(f"File {file_path} with no data or metadata.")
        return None

    # Change the file type declaration in the first header
    if len(meta) > 0 and len(meta[0]) > 0:
        meta[0][0] = "TOA5py"

    # Remove useless rows in header to match CardConvert standard TOA5 output
    if len(meta) >= 5:
        meta[0].extend(meta[1]) #merge two row into one
        meta[0][7], meta[0][8] = meta[0][8], meta[0][7] #switch two element position to match Card Converter output
        del meta[1] 
        del meta[4] # Wait, if you delete index 1 first, the old index 5 becomes index 4. 
                    # Assuming this logic is correct for your specific use case.

    logger.info(f"Writing TOA5 file to: {out_path}")

    # Write data to the new file
    with open(out_path, mode='w', newline='', encoding='ascii') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        # Write the metadata headers
        for header_line in meta:
            writer.writerow(header_line)

        # Write the data rows
        for row in data:
            formatted_row = []
            for item in row:
                if isinstance(item, datetime):
                    # Check if timestamp has sub-second resolution (for Sonic data)
                    if item.microsecond > 0:
                        # %f prints microseconds (e.g., .050000). rstrip('0') removes trailing zeros.
                        time_str = item.strftime('%Y-%m-%d %H:%M:%S.%f').rstrip('0')
                        formatted_row.append(time_str)
                    else:
                        # Standard Slow data timestamp (no decimals)
                        formatted_row.append(item.strftime('%Y-%m-%d %H:%M:%S'))
                        
                elif isinstance(item, str):
                    # 1. Togli i null bytes
                    clean_str = item.replace('\x00', '')
                    # 2. Forza la conversione in ASCII ignorando/eliminando i caratteri strani
                    clean_str = clean_str.encode('ascii', errors='ignore').decode('ascii')
                    # 3. Togli gli spazi bianchi rimasti
                    clean_str = clean_str.strip()
                    
                    formatted_row.append(clean_str)

                elif isinstance(item, float):
                    # Round floats to clean up IEEE 754 precision artifacts.
                    # By keeping it as a float, the CSV writer will NOT add quotes around it.
                    formatted_row.append(round(item, decimals))
                    
                else:
                    # Catch-all for integers (like RECORD or BOOL flags)
                    formatted_row.append(item)
                    
            writer.writerow(formatted_row)

    logger.info("End convertion\n")

    return out_path