"""
Calculate financial metrics from cleaned Nike financial statement data.

This module is a placeholder for growth, margin, and earnings calculations.
It does not include any hardcoded Nike values and should only be used after
validated financial data has been collected.
"""

import pandas as pd


def calculate_revenue_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Add a revenue growth column to a cleaned financial dataset."""
    result_df = df.copy()

    # Expected future logic:
    # - Filter to revenue rows or revenue columns.
    # - Sort by fiscal period.
    # - Calculate period-over-period or year-over-year growth.
    # - Store the result in a clearly named column.

    return result_df


def calculate_margins(df: pd.DataFrame) -> pd.DataFrame:
    """Add planned margin calculations to the dataset."""
    result_df = df.copy()

    # Expected future logic:
    # - Gross Margin = Gross Profit / Revenue
    # - Operating Margin = Operating Income / Revenue
    # - Net Profit Margin = Net Income / Revenue
    # Make sure required columns are validated before calculation.

    return result_df


def calculate_eps_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Add EPS growth calculations to the dataset."""
    result_df = df.copy()

    # Expected future logic:
    # - Confirm EPS values are present and numeric.
    # - Sort by fiscal period.
    # - Calculate growth over the chosen comparison period.

    return result_df
