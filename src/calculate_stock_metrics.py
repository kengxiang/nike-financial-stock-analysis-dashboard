"""
Calculate stock performance metrics from validated Nike price data.

This module contains beginner-friendly placeholders for common stock analysis
tasks such as returns, moving averages, volatility, and drawdown.
"""

from pathlib import Path

import pandas as pd


def load_stock_data(filepath: str | Path) -> pd.DataFrame:
    """Load raw or cleaned stock price data from a CSV file."""
    return pd.read_csv(filepath)


def calculate_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily percentage returns from stock price data."""
    result_df = df.copy()

    # Expected future logic:
    # - Sort by date.
    # - Use adjusted close if available.
    # - Calculate day-to-day percentage change.

    return result_df


def calculate_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate moving average columns for trend analysis."""
    result_df = df.copy()

    # Expected future logic:
    # - Confirm a price column exists.
    # - Calculate 50-day and 200-day moving averages.
    # - Store the results in columns such as `ma_50` and `ma_200`.

    return result_df


def calculate_volatility(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate rolling volatility using daily returns."""
    result_df = df.copy()

    # Expected future logic:
    # - Ensure daily returns have already been calculated.
    # - Use a rolling window such as 20, 30, or 252 trading days.
    # - Annualise the result if appropriate for the analysis.

    return result_df


def calculate_max_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate maximum drawdown from a price series."""
    result_df = df.copy()

    # Expected future logic:
    # - Track the running peak price.
    # - Measure the decline from each peak.
    # - Identify the largest peak-to-trough drop.

    return result_df
