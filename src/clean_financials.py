"""
Clean raw Nike financial statement data for analysis.

This module is a placeholder for the future financial data cleaning workflow.
It is designed to keep the project reproducible by separating raw data loading,
cleaning rules, and file export steps.
"""

from pathlib import Path

import pandas as pd


def load_financial_data(filepath: str | Path) -> pd.DataFrame:
    """Load raw financial data from a CSV file."""
    # In the future, this function can be extended to support Excel files
    # or multiple input formats if your source files change.
    return pd.read_csv(filepath)


def clean_financial_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply standard cleaning steps to raw financial data."""
    cleaned_df = df.copy()

    # Example placeholder cleaning steps:
    # 1. Standardise column names.
    # 2. Trim whitespace from text fields.
    # 3. Convert date or period columns to a consistent format.
    # 4. Convert numeric columns to numeric data types.
    # 5. Keep a record of any rows removed during validation.

    cleaned_df.columns = [column.strip().lower() for column in cleaned_df.columns]

    return cleaned_df


def save_clean_financial_data(df: pd.DataFrame, output_path: str | Path) -> None:
    """Save cleaned financial data to a CSV file."""
    # `index=False` keeps the exported file tidy for later SQL and Tableau use.
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    # Replace these example paths only after verified source files are added.
    input_file = Path("data/raw/nike_financials_raw.csv")
    output_file = Path("data/processed/nike_financials_clean.csv")

    # This guard makes the script safe to run before the raw file exists.
    if input_file.exists():
        raw_df = load_financial_data(input_file)
        cleaned_df = clean_financial_data(raw_df)
        save_clean_financial_data(cleaned_df, output_file)
        print(f"Saved cleaned financial data to: {output_file}")
    else:
        print("Raw financial data file not found. Add verified source data first.")
