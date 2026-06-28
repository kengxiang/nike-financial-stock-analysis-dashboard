# Data Dictionary

This document describes the planned datasets for the Nike Financial & Stock Analysis Dashboard. It is a template for project setup only and does not contain real Nike financial values.

## 1. `nike_financials_raw.csv`

**Purpose**

Store original financial statement data collected from verified public sources before any cleaning or transformation.

**Expected columns**

- `period`
- `fiscal_year`
- `fiscal_quarter`
- `statement_type`
- `metric_name`
- `metric_value`
- `unit`
- `currency`
- `source_name`
- `source_date`
- `source_link`
- `load_date`

**Notes**

- This dataset should preserve the original structure as closely as possible.
- It can include annual and quarterly values if clearly labelled.
- Avoid manually overwriting original values after ingestion.

**Source requirement**

Must come from a verified source such as Nike Investor Relations, SEC filings, or SEC EDGAR / CompanyFacts data, and must be logged in `data/source_log.csv`.

## 2. `nike_financials_clean.csv`

**Purpose**

Store cleaned and standardised financial statement data ready for analysis, SQL queries, and dashboard use.

**Expected columns**

- `period`
- `fiscal_year`
- `fiscal_quarter`
- `metric_name`
- `metric_value`
- `unit`
- `currency`
- `statement_type`
- `period_type`
- `source_name`
- `last_validated_date`

**Notes**

- Use consistent naming conventions for metrics.
- Ensure time periods are formatted consistently.
- Any cleaning decisions should be reproducible in Python scripts or notebooks.

**Source requirement**

Must be derived from validated raw financial data stored in `data/raw` and linked back to verified entries in `data/source_log.csv`.

## 3. `nike_stock_prices_raw.csv`

**Purpose**

Store original historical stock price data before calculations such as returns, moving averages, or volatility.

**Expected columns**

- `date`
- `ticker`
- `open`
- `high`
- `low`
- `close`
- `adjusted_close`
- `volume`
- `source_name`
- `source_date`
- `source_link`
- `load_date`

**Notes**

- Keep the raw export unchanged after collection.
- If adjusted prices are available, keep both close and adjusted close where possible.
- Confirm the exact ticker and exchange used by the source.

**Source requirement**

Must come from a verified historical stock price source and must be documented in `data/source_log.csv`.

## 4. `nike_stock_prices_clean.csv`

**Purpose**

Store cleaned stock price data prepared for time-series analysis and dashboard visualisation.

**Expected columns**

- `date`
- `ticker`
- `close`
- `adjusted_close`
- `volume`
- `daily_return`
- `ma_50`
- `ma_200`
- `volatility_window`
- `source_name`
- `last_validated_date`

**Notes**

- Derived metric columns should be added only after validation of the raw price data.
- Date formatting should be consistent and analysis-ready.
- Keep calculation logic documented in `src/`.

**Source requirement**

Must be derived from validated raw stock data stored in `data/raw` and tied back to verified source entries in `data/source_log.csv`.

## 5. `source_log.csv`

**Purpose**

Provide an audit trail for every dataset, metric, and external source used in the project.

**Expected columns**

- `metric`
- `period`
- `value`
- `unit`
- `source_type`
- `source_name`
- `source_date`
- `access_date`
- `source_link`
- `notes`

**Notes**

- This file should be updated whenever a new source is used.
- Values should only be entered after source verification.
- Notes can explain extraction decisions, caveats, or missing context.

**Source requirement**

Every financial, stock, and valuation data point used in the project should be traceable through this log.
