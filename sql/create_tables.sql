-- SQL table templates for the Nike Financial & Stock Analysis Dashboard.
-- Replace data types or column names later if your validated datasets differ.

-- Financial statement data table
CREATE TABLE IF NOT EXISTS financials (
    period VARCHAR(50),
    fiscal_year INT,
    fiscal_quarter VARCHAR(20),
    statement_type VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value DECIMAL(18, 4),
    unit VARCHAR(50),
    currency VARCHAR(10),
    source_name VARCHAR(255),
    source_date DATE,
    source_link VARCHAR(500),
    load_date DATE
);

-- Historical stock price data table
CREATE TABLE IF NOT EXISTS stock_prices (
    trade_date DATE,
    ticker VARCHAR(20),
    open_price DECIMAL(18, 4),
    high_price DECIMAL(18, 4),
    low_price DECIMAL(18, 4),
    close_price DECIMAL(18, 4),
    adjusted_close DECIMAL(18, 4),
    volume BIGINT,
    source_name VARCHAR(255),
    source_date DATE,
    source_link VARCHAR(500),
    load_date DATE
);
