# Nike Financial & Stock Analysis Dashboard

## Project Overview
This project analyses Nike's financial performance, stock price movement, valuation metrics, and investment outlook using verified public data. The goal is to build a professional, reproducible portfolio project that demonstrates financial analysis, data cleaning, SQL analysis, and dashboard storytelling without relying on unsupported assumptions.

## Business Question
"Is Nike financially healthy, fairly valued, and attractive from an investment perspective?"

## Project Objectives
- Analyse Nike's revenue, profitability, and margin trends.
- Analyse stock price performance and market momentum.
- Calculate financial ratios and stock performance metrics.
- Build a Tableau dashboard for visual storytelling.
- Produce an evidence-based Buy / Watch / Avoid framework.
- Document all data sources to avoid unsupported claims.

## Tools Used
- Python: data cleaning, financial calculations, stock metrics
- Pandas / NumPy: data transformation and analysis
- SQL: querying financial and stock datasets
- Tableau: dashboard visualisation
- Excel: manual data checking and validation
- GitHub: documentation and version control

## Data Sources
This project will only use verified sources such as:
- Nike Investor Relations
- SEC 10-K / 10-Q filings
- SEC EDGAR / CompanyFacts data
- Verified historical stock price source

All source information will be documented in `data/source_log.csv`.

## Project Structure
- `data/raw`: original downloaded or exported source files kept in their raw form for traceability
- `data/processed`: cleaned analysis-ready datasets created from validated raw files
- `notebooks`: Jupyter notebooks used for exploratory analysis, validation checks, and metric development
- `sql`: SQL scripts for table creation and analytical queries
- `src`: reusable Python scripts for cleaning, validation, and metric calculations
- `dashboard`: Tableau files, exported visuals, or dashboard-related assets
- `reports`: written analysis outputs, summary reports, and final portfolio deliverables

## Analysis Workflow
1. Collect verified official financial and stock data.
2. Record every source in `data/source_log.csv`.
3. Store original files in `data/raw`.
4. Clean and validate data using Python.
5. Export clean datasets to `data/processed`.
6. Use SQL to analyse financial and stock trends.
7. Build a Tableau dashboard.
8. Write final evidence-based insights and limitations.

## Key Metrics Planned
- Revenue
- Gross Profit
- Operating Income
- Net Income
- EPS
- Revenue Growth
- Gross Margin
- Operating Margin
- Net Profit Margin
- Stock Return
- 50-day Moving Average
- 200-day Moving Average
- Volatility
- Maximum Drawdown
- P/E Ratio
- P/S Ratio

## Current Status
Project structure setup in progress. Data collection and analysis have not started yet.

## Disclaimer
This project is for educational and portfolio purposes only. It does not provide financial advice.
