import pandas as pd
import csv

def average_toa5(input_file, output_file, freq='10min'):
    """
    Reads a Campbell Scientific TOA5 file, averages the data based on a defined 
    time interval (freq), and exports it matching the original file structure.
    
    :param input_file: str, path to the input TOA5 file
    :param output_file: str, path for the output TOA5 file
    :param freq: str, pandas time frequency string (e.g., '1min', '30S', '1H')
    """
    #read the 4-line TOA5 header
    with open(input_file, 'r') as f:
        headers = [next(f) for _ in range(4)]
        
    #extract column names from the 2nd header line
    col_names = next(csv.reader([headers[1]]))

    #read data skipping the 4 header lines
    df = pd.read_csv(input_file, skiprows=4, header=None, names=col_names, na_values=["NAN", "INF"])

    #setup datetime index
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
    df.set_index('TIMESTAMP', inplace=True)

    # Use 'mean' for numeric data (u, v, T, RH) and 'first' for strings/flags (like "00" in SS_1)
    agg_rules = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            agg_rules[col] = 'mean'
        else:
            agg_rules[col] = 'first'

    #resample and aggregate
    df_avg = df.resample(freq).agg(agg_rules)

    # (Optional) Rebuild the RECORD column as a clean sequential integer series
    if 'RECORD' in df_avg.columns:
        df_avg['RECORD'] = range(len(df_avg))

    # 6. Write output preserving TOA5 exact structure
    with open(output_file, 'w', newline='') as f:
        for line in headers:
            f.write(line)

    # Append data. QUOTE_NONNUMERIC ensures TIMESTAMP and strings (e.g. "00") are quoted,
    # while numbers remain unquoted, perfectly matching the TOA5 standard.
    df_avg.to_csv(output_file, mode='a', header=False, index=True, 
                  date_format='%Y-%m-%d %H:%M:%S', 
                  quoting=csv.QUOTE_NONNUMERIC)

# --- EXAMPLE USAGE ---
# average_toa5('slow_data.dat', 'slow_data_avg.dat', freq='1min')
# average_toa5('fast_data.dat', 'fast_data_avg.dat', freq='10min')