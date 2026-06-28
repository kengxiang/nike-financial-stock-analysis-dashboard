"""
Validate financial and stock datasets before analysis.

This module contains reusable checks to help catch missing columns, missing
values, and duplicate periods or dates before calculations begin.
"""

import pandas as pd


def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    """Raise an error if any required columns are missing."""
    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def validate_no_missing_values(df: pd.DataFrame, columns: list[str]) -> None:
    """Raise an error if specified columns contain missing values."""
    missing_value_columns = [column for column in columns if df[column].isna().any()]

    if missing_value_columns:
        raise ValueError(f"Missing values found in columns: {missing_value_columns}")


def validate_no_duplicate_periods(df: pd.DataFrame) -> None:
    """Raise an error if duplicate financial periods are found."""
    # Update the subset later if your cleaned financial dataset uses different
    # period fields such as `fiscal_year` and `fiscal_quarter`.
    if "period" in df.columns and df["period"].duplicated().any():
        raise ValueError("Duplicate financial periods found in the dataset.")


def validate_no_duplicate_dates(df: pd.DataFrame) -> None:
    """Raise an error if duplicate stock price dates are found."""
    if "date" in df.columns and df["date"].duplicated().any():
        raise ValueError("Duplicate stock price dates found in the dataset.")
