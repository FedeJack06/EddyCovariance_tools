import csv
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, List

def import_file(input_file: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Work with TOA5 file data from Sonic Anemometer and Termoigrometers with N vertical levels

    Parameters
    ----------
    input_file: str
        path to file in TOA5

    Returns
    -------
    Tuple[pd.DataFrame, List[str]]
        - Pandas Dataframe with TIMESTAMP and numerical and validation data.
        - List of strings containing the original 4 header lines of the TOA5 file.
    """

    #extract header
    raw_header = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for _ in range(4):
            raw_header.append(f.readline())

    df = pd.read_csv(input_file, sep=",", header=0, skiprows=[0,2,3], dtype="string")
    type_list = [str]*1 + [int]*1 + [float]*4 + [str]*1 + [bool]*1
    dictionary = dict( zip(df.columns, type_list) )
    df = df.astype(dictionary)

    first_column = df.columns[0]
    # Converte la colonna in datetime
    df[first_column] = pd.to_datetime(
        df[first_column], 
        format='mixed', 
        errors='coerce'
    )

    df.set_index('TIMESTAMP', inplace=True)
    df.drop(columns=['TIMESTAMP'], inplace=True, errors='ignore')
    df.drop(columns=['RECORD'], inplace=True)

    return df, raw_header

def despiking_series_robust(input_series: pd.Series, 
                            robust_std_dev: float, 
                            n_window_points: int, 
                            show_plot: bool = False) -> Tuple[pd.Series, int]:
    """
    Applies a moving-window robust despiking algorithm directly to a pandas Series.
    If a record exceeds N times the robust standard deviation, it's marked as spike.
    
    Detected spikes are replaced with the local running median. 

    Parameters
    ----------
    input_series : pd.Series
        Input time series data with a DatetimeIndex.
    robust_std_dev : float
        Threshold multiplier for the robust standard deviation.
    n_window_points : int
        Number of periods for the rolling window.
    show_plot : bool, optional
        If True, displays a plot showing the original series, the dynamic bounds, 
        and the identified spikes. Default is False.

    Returns
    -------
    pd.Series
        The despiked series.
    int
        The number of spikes removed.
    """
    # check
    if not isinstance(input_series, pd.Series):
        raise TypeError("Input must be a pandas Series.")
    if robust_std_dev <= 0:
        raise ValueError("Number of standard dev must be a positive number.")
    if not isinstance(n_window_points, int) or n_window_points <= 0:
        raise ValueError("Window_length must be a positive integer.")
    if n_window_points % 2 == 0:
        warnings.warn("It is recommended to use odd number of point in window.")

    timeseries = input_series.copy()

    # --- Rolling Statistics using Pandas ---
    roll = timeseries.rolling(window=n_window_points, center=True, min_periods=1)
    
    running_median = roll.median()
    p84 = roll.quantile(0.84)
    p16 = roll.quantile(0.16)
    
    # definition of robust standard deviation
    running_std_robust = 0.5 * (p84 - p16)

    # --- Spike Detection and Replacement ---
    delta = np.maximum(robust_std_dev * running_std_robust, 0.5)

    upper_bound = running_median + delta
    lower_bound = running_median - delta

    # Create boolean mask for spikes 
    spike_mask = (timeseries > upper_bound) | (timeseries < lower_bound)
    count_spike = int(spike_mask.sum())

    # Visualize spikes and temporal series
    if show_plot:
        plt.figure(figsize=(14, 6))
        
        # input series in grey
        plt.plot(input_series.index, input_series, label='Input series', color='gray', alpha=0.5, linewidth=1)
        
        # tolerance band
        plt.fill_between(input_series.index, lower_bound, upper_bound, color='blue', alpha=0.1, label='Tolerance band')
        
        # despiked series in blue
        plt.plot(timeseries.index, timeseries.where(~spike_mask, running_median), label='Despiked series', color='blue', linewidth=1.5)
        
        # spikes red dot
        spikes_only = input_series[spike_mask]
        plt.scatter(spikes_only.index, spikes_only, color='red', label='Spike value', zorder=5, s=20)
        
        plt.title(f'Robust despike (Spike removed: {count_spike})', fontsize=14)
        plt.xlabel('Timestamp', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.legend(loc='best')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

    # Replace bad data with the local median using .loc
    timeseries.loc[spike_mask] = running_median.loc[spike_mask]

    return timeseries, count_spike

def despiking_TOA5_robust(file_path: str,
                          out_path: str, 
                          robust_std_dev: float, 
                          n_window_points: int, 
                          show_plot: bool = False) -> str:
    """
    Despike data directly from a TOA5 format file.
    Put despiked data into a similar TOA5 format: the first header row info is manteined.
    Info on the measurmemts units is lost in the new header.
    Applies a moving-window robust despiking algorithm.
    If a record exceeds N times the robust standard deviation, it's marked as spike.
    
    Detected spikes are replaced with the local running median. 

    Parameters
    ----------
    file_path : str
        Path to TOA5 data file from campbell datalogger
    out_path : str
        Output dir where put despiked file
    robust_std_dev : float
        Threshold multiplier for the robust standard deviation.
    n_window_points : int
        Number of periods for the rolling window.
    show_plot : bool, optional
        If True, displays a plot showing the original series, the dynamic bounds, 
        and the identified spikes. Default is False.

    Returns
    -------
    pd.Series
        The despiked series.
    int
        The number of spikes removed.
    """
    #import file
    df, meta = import_file(file_path)

    print(f"Despiking {file_path}")

    # select relevant column and mask row with error (from Gill Windmaster instrument) 
    columns_meas = ['u_1', 'v_1', 'w_1', 'Ts_1']
    condition = (df['SS_1'] != "0B") & (df['SS_1'] != "00") 
    df[columns_meas] = df[columns_meas].mask(condition)

    # despiking on measurments column
    for c in columns_meas:
        despiked_series, n_spikes = despiking_series_robust(
            df[c], 
            robust_std_dev=robust_std_dev, 
            n_window_points=n_window_points, 
            show_plot=show_plot
        )
        
        # replace column with despiked column
        df[c] = despiked_series
        
        print(f"Column {c}: {n_spikes} spike replaced.")
        
    #output file info
    print(f"Number of records in output file: {len(df)}.")
    print(f"First timestamp: {df.index.min()}")
    print(f"Lasr timestamp: {df.index.max()}")

    # output path
    in_path = Path(file_path)
    out_path = Path(out_path)
    # new filename
    out_path = out_path.parent / f"desp_{in_path.stem}{in_path.suffix}"

    # Save to file header info and data despiked
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(meta[0])

    df.to_csv(out_path, mode='a', sep=",")

    return str(out_path)

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