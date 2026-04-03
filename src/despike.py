import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
from typing import Tuple

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