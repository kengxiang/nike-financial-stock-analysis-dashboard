-- Placeholder analytical queries for the Nike Financial & Stock Analysis Dashboard.
-- These templates are intentionally generic and should be updated after the
-- final dataset structure has been validated.

-- Annual revenue and net income trend
SELECT
    fiscal_year,
    metric_name,
    metric_value
FROM financials
WHERE metric_name IN ('Revenue', 'Net Income')
ORDER BY fiscal_year, metric_name;

-- Margin trend
SELECT
    fiscal_year,
    metric_name,
    metric_value
FROM financials
WHERE metric_name IN ('Gross Margin', 'Operating Margin', 'Net Profit Margin')
ORDER BY fiscal_year, metric_name;

-- Quarterly performance trend
SELECT
    fiscal_year,
    fiscal_quarter,
    metric_name,
    metric_value
FROM financials
WHERE fiscal_quarter IS NOT NULL
ORDER BY fiscal_year, fiscal_quarter, metric_name;

-- Stock price moving average trend
SELECT
    trade_date,
    close_price,
    adjusted_close
FROM stock_prices
ORDER BY trade_date;

-- Note:
-- Moving average calculations may be done in SQL with window functions or in
-- Python before loading clean datasets into the database.
