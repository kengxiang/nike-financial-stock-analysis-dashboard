# Data Dictionary

This document describes the planned datasets for the Nike Financial & Stock Analysis Dashboard. It is a template for project setup only and does not contain real Nike financial values.

## 1. `nike_financials_raw.csv`

**Purpose**

Store original financial statement data collected from verified public sources before any cleaning or transformation.

**Expected columns**

- `source_id`
- `period`
- `fiscal_year`
- `fiscal_quarter`
- `period_type`
- `statement_type`
- `metric_name`
- `reported_value`
- `metric_value`
- `unit`
- `currency`
- `source_name`
- `source_date`
- `source_link`
- `load_date`
- `notes`

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

Provide the evidence audit trail for every dataset, metric, claim, and external source used in the project.

**Expected columns**

| Column | Description | Example value | Required? |
| --- | --- | --- | --- |
| `source_id` | Unique ID for each source log entry. | `S001` | Yes |
| `hypothesis_id` | Hypothesis linked to the source or claim. Multiple IDs can be separated with semicolons. | `H1` | Yes |
| `metric_or_claim` | Metric, claim, or research item being tracked. | `Revenue growth` | Yes |
| `period` | Time period covered by the source or claim. | `TBD` | Yes |
| `value` | Data value recorded from the source after verification. Use `TBD` until collected. | `TBD` | Yes |
| `unit` | Unit of measurement for the value, if applicable. | `TBD` | No |
| `source_type` | Category of source used for verification. | `Nike Investor Relations` | Yes |
| `source_name` | Name of the exact source document, page, filing, or provider. | `TBD` | Yes |
| `source_date` | Date the source was published or filed. | `TBD` | No |
| `access_date` | Date the source was accessed for the project. | `TBD` | Yes |
| `source_link` | Link to the source, added only after a source is selected. | `TBD` | No |
| `evidence_role` | How the source relates to the linked hypothesis. | `pending` | Yes |
| `verification_status` | Current verification state of the source or claim. | `not verified` | Yes |
| `notes` | Short explanation of context, limitations, or follow-up checks. | `Placeholder for future evidence` | No |

**Notes**

- This file should be updated whenever a new source is used.
- Screenshots and user notes are research leads only, not evidence.
- A claim should only be marked as verified after checking a reliable source.
- Values should only be entered after source verification.
- Notes can explain extraction decisions, caveats, or missing context.
- Every major metric or claim used in the final report should be traceable to `source_log.csv`.

**Source requirement**

Every financial, stock, and valuation data point used in the project should be traceable through this log.

## Source Log Controlled Values

**`hypothesis_id`**

- `H1`
- `H2`
- `H3`
- `H4`
- `H5`
- `H6`
- `H7`
- `H8`
- `H9`
- Multiple IDs can be separated with semicolons if one source relates to more than one hypothesis.

**`evidence_role`**

- `pending`
- `supports`
- `weakens`
- `mixed`
- `context`

**`verification_status`**

- `not verified`
- `verified`
- `needs review`
- `conflicting`
