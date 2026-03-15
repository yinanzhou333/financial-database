# SQL Query Examples

This document contains ready-to-use SQL queries for financial analysis.

## Basic Data Retrieval

### Get Latest Price for All Stocks

```sql
SELECT 
    sp.ticker,
    c.company_name,
    sp.price_date,
    sp.closing_price,
    sp.volume
FROM stock_prices sp
JOIN companies c ON sp.ticker = c.ticker
WHERE sp.price_date = (
    SELECT MAX(price_date) 
    FROM stock_prices 
    WHERE ticker = sp.ticker
)
ORDER BY sp.ticker;
```

### Get Stock Price History for Specific Period

```sql
SELECT 
    ticker,
    price_date,
    opening_price,
    highest_price,
    lowest_price,
    closing_price,
    adjusted_close,
    volume
FROM stock_prices
WHERE ticker = 'AAPL'
    AND price_date BETWEEN '2024-01-01' AND '2024-03-15'
ORDER BY price_date;
```

---

## Performance Analysis

### Calculate Daily Returns

```sql
SELECT 
    ticker,
    price_date,
    closing_price,
    LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) as prev_close,
    ((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) 
     / LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) * 100 as daily_return_pct
FROM stock_prices
WHERE ticker IN ('AAPL', 'MSFT', 'GOOGL')
ORDER BY ticker, price_date DESC
LIMIT 100;
```

### Calculate YTD Return (Year-to-Date)

```sql
SELECT 
    ticker,
    YEAR(price_date) as year,
    MIN(closing_price) as opening_price,
    MAX(closing_price) as year_high,
    MIN(closing_price) as year_low,
    (SELECT closing_price FROM stock_prices sp2 
     WHERE sp2.ticker = sp.ticker 
     ORDER BY sp2.price_date DESC LIMIT 1) as current_price,
    ROUND(
        ((SELECT closing_price FROM stock_prices sp2 
          WHERE sp2.ticker = sp.ticker 
          ORDER BY sp2.price_date DESC LIMIT 1) - 
         (SELECT closing_price FROM stock_prices sp2 
          WHERE sp2.ticker = sp.ticker 
          AND YEAR(sp2.price_date) = YEAR(sp.price_date)
          ORDER BY sp2.price_date ASC LIMIT 1)) 
        / (SELECT closing_price FROM stock_prices sp2 
           WHERE sp2.ticker = sp.ticker 
           AND YEAR(sp2.price_date) = YEAR(sp.price_date)
           ORDER BY sp2.price_date ASC LIMIT 1) * 100, 2
    ) as ytd_return_pct
FROM stock_prices sp
WHERE YEAR(price_date) = YEAR(CURDATE())
GROUP BY ticker, YEAR(price_date)
ORDER BY ytd_return_pct DESC;
```

### Find Best Performers in Last 30 Days

```sql
SELECT 
    sp.ticker,
    c.company_name,
    c.sector,
    MAX(sp.closing_price) as current_price,
    MIN(sp.closing_price) as low_30d,
    MAX(sp.closing_price) as high_30d,
    ROUND(
        ((MAX(sp.closing_price) - MIN(sp.closing_price)) / MIN(sp.closing_price)) * 100, 2
    ) as return_pct,
    AVG(sp.volume) as avg_volume
FROM stock_prices sp
JOIN companies c ON sp.ticker = c.ticker
WHERE sp.price_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY sp.ticker, c.company_name, c.sector
ORDER BY return_pct DESC
LIMIT 20;
```

---

## Volatility Analysis

### Calculate Historical Volatility (30-day)

```sql
SELECT 
    ticker,
    DATE_FORMAT(price_date, '%Y-%m-%d') as date,
    ROUND(
        STDDEV_POP(
            (closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date))
            / LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)
        ) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) * 100,
        2
    ) as volatility_30d
FROM stock_prices
WHERE ticker IN ('AAPL', 'MSFT', 'TSLA')
    AND price_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
ORDER BY ticker, price_date DESC;
```

### Compare Volatility Across Tickers

```sql
SELECT 
    ticker,
    ROUND(
        STDDEV(
            ((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date))
             / LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) * 100
        ),
        2
    ) as volatility_pct,
    ROUND(
        STDDEV(
            ((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date))
             / LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) * 100
        ) * SQRT(252),
        2
    ) as annualized_volatility_pct,
    COUNT(*) as trading_days
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
GROUP BY ticker
ORDER BY annualized_volatility_pct DESC;
```

---

## Volume Analysis

### Find Days with Highest Volume

```sql
SELECT 
    ticker,
    price_date,
    volume,
    closing_price,
    AVG(volume) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as volume_ma20
FROM stock_prices
WHERE ticker IN ('AAPL', 'MSFT', 'GOOGL')
    AND volume > (
        SELECT AVG(volume) * 1.5
        FROM stock_prices sp2
        WHERE sp2.ticker = stock_prices.ticker
            AND sp2.price_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
    )
ORDER BY price_date DESC
LIMIT 50;
```

### Average Volume by Stock

```sql
SELECT 
    ticker,
    ROUND(AVG(volume), 0) as avg_volume,
    ROUND(AVG(volume * closing_price), 0) as avg_dollar_volume,
    MAX(volume) as max_volume,
    MIN(volume) as min_volume,
    ROUND(STDDEV(volume), 0) as volume_stddev
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY ticker
ORDER BY avg_dollar_volume DESC;
```

---

## Price Pattern Analysis

### Identify Support/Resistance Levels

```sql
SELECT 
    ticker,
    ROUND(closing_price, 2) as price_level,
    COUNT(*) as touches,
    MIN(price_date) as first_touch,
    MAX(price_date) as last_touch
FROM stock_prices
WHERE ticker = 'AAPL'
    AND price_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
GROUP BY ticker, ROUND(closing_price, 0)
HAVING COUNT(*) >= 3
ORDER BY touches DESC, price_level DESC;
```

### Find Breakouts (New 52-Week Highs)

```sql
SELECT 
    sp.ticker,
    c.company_name,
    sp.price_date,
    sp.closing_price,
    MAX(sp2.closing_price) as high_52w,
    ROUND(
        ((sp.closing_price - MAX(sp2.closing_price)) / MAX(sp2.closing_price)) * 100, 2
    ) as percent_above_52w_high
FROM stock_prices sp
JOIN companies c ON sp.ticker = c.ticker
JOIN stock_prices sp2 ON sp.ticker = sp2.ticker
    AND sp2.price_date >= DATE_SUB(sp.price_date, INTERVAL 52 WEEK)
    AND sp2.price_date < sp.price_date
WHERE sp.price_date = (
    SELECT MAX(price_date)
    FROM stock_prices
    WHERE ticker = sp.ticker
)
GROUP BY sp.ticker, c.company_name, sp.price_date, sp.closing_price
HAVING sp.closing_price > MAX(sp2.closing_price)
ORDER BY percent_above_52w_high DESC;
```

---

## Market Index Analysis

### Compare Stock to Market Index

```sql
SELECT 
    sp.price_date,
    sp.ticker,
    sp.closing_price,
    sp.closing_price / LAG(sp.closing_price) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date) - 1 as stock_return,
    mi.index_value,
    mi.index_value / LAG(mi.index_value) OVER (PARTITION BY mi.index_symbol ORDER BY mi.index_date) - 1 as market_return
FROM stock_prices sp
JOIN market_indices mi ON sp.price_date = mi.index_date
WHERE sp.ticker = 'AAPL'
    AND mi.index_symbol = '^GSPC'
    AND sp.price_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY sp.price_date DESC;
```

### Beta Calculation (Stock vs Market)

```sql
SELECT 
    sp.ticker,
    ROUND(
        COVARIANCE_POP(
            (sp.closing_price - LAG(sp.closing_price) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date))
            / LAG(sp.closing_price) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date),
            (mi.index_value - LAG(mi.index_value) OVER (PARTITION BY mi.index_symbol ORDER BY mi.index_date))
            / LAG(mi.index_value) OVER (PARTITION BY mi.index_symbol ORDER BY mi.index_date)
        ) /
        VARIANCE_POP(
            (mi.index_value - LAG(mi.index_value) OVER (PARTITION BY mi.index_symbol ORDER BY mi.index_date))
            / LAG(mi.index_value) OVER (PARTITION BY mi.index_symbol ORDER BY mi.index_date)
        ),
        4
    ) as beta
FROM stock_prices sp
JOIN market_indices mi ON sp.price_date = mi.index_date
WHERE mi.index_symbol = '^GSPC'
    AND sp.price_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
GROUP BY sp.ticker
ORDER BY beta DESC;
```

---

## Portfolio Analysis

### Current Portfolio Allocation (by sector)

```sql
SELECT 
    c.sector,
    COUNT(*) as stock_count,
    ROUND(AVG(c.market_cap), 0) as avg_market_cap,
    GROUP_CONCAT(c.ticker) as tickers
FROM companies c
WHERE c.ticker IN ('AAPL', 'MSFT', 'JPM', 'XOM', 'NVDA')
GROUP BY c.sector
ORDER BY COUNT(*) DESC;
```

### Portfolio Performance Summary

```sql
SELECT 
    sp.ticker,
    c.company_name,
    c.sector,
    MAX(CASE WHEN sp.price_date = CURDATE() THEN sp.closing_price END) as current_price,
    MAX(CASE WHEN DATE_ADD(sp.price_date, INTERVAL 30 DAY) >= CURDATE() AND DATE_SUB(sp.price_date, INTERVAL 30 DAY) <= CURDATE() THEN sp.closing_price END) as price_30d_ago,
    ROUND(
        (MAX(CASE WHEN sp.price_date = CURDATE() THEN sp.closing_price END) - 
         MAX(CASE WHEN DATE_ADD(sp.price_date, INTERVAL 30 DAY) >= CURDATE() THEN sp.closing_price END)) /
        MAX(CASE WHEN DATE_ADD(sp.price_date, INTERVAL 30 DAY) >= CURDATE() THEN sp.closing_price END) * 100,
        2
    ) as return_30d_pct
FROM stock_prices sp
JOIN companies c ON sp.ticker = c.ticker
WHERE sp.ticker IN ('AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN')
GROUP BY sp.ticker, c.company_name, c.sector
ORDER BY return_30d_pct DESC;
```

---

## Advanced Queries

### Moving Average Crossover Detection

```sql
WITH ma_data AS (
    SELECT 
        ticker,
        price_date,
        closing_price,
        AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) as ma50,
        AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) as ma200
    FROM stock_prices
    WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
)
SELECT 
    ticker,
    price_date,
    closing_price,
    ROUND(ma50, 2) as ma50,
    ROUND(ma200, 2) as ma200,
    CASE 
        WHEN ma50 > ma200 THEN 'GOLDEN CROSS'
        WHEN ma50 < ma200 THEN 'DEATH CROSS'
        ELSE 'NO CROSS'
    END as signal
FROM ma_data
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY ticker, price_date DESC;
```

### Momentum Divergence Detection

```sql
SELECT 
    sp.ticker,
    sp.price_date,
    sp.closing_price,
    LAG(sp.closing_price, 20) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date) as price_20d_ago,
    ROUND(
        (sp.closing_price - LAG(sp.closing_price, 20) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date)) /
        LAG(sp.closing_price, 20) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date) * 100,
        2
    ) as momentum_20d,
    CASE 
        WHEN sp.closing_price > LAG(sp.closing_price, 20) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date)
             AND momentum_20d < LAG(momentum_20d, 1) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date)
        THEN 'BEARISH DIVERGENCE'
        WHEN sp.closing_price < LAG(sp.closing_price, 20) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date)
             AND momentum_20d > LAG(momentum_20d, 1) OVER (PARTITION BY sp.ticker ORDER BY sp.price_date)
        THEN 'BULLISH DIVERGENCE'
        ELSE 'NO DIVERGENCE'
    END as divergence_signal
FROM stock_prices sp
WHERE sp.price_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
ORDER BY sp.ticker, sp.price_date DESC;
```

---

## Performance Optimization Tips

1. **Use Indexes**: Queries on indexed columns are much faster
   ```sql
   -- This is automatically created but verify:
   SHOW INDEX FROM stock_prices;
   ```

2. **Limit Result Sets**: Don't select more data than needed
   ```sql
   -- Good
   WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
   
   -- Bad
   WHERE price_date IS NOT NULL  -- Too broad
   ```

3. **Use Joins Instead of Subqueries**: Usually faster
   ```sql
   -- Good
   SELECT * FROM stock_prices sp
   JOIN companies c ON sp.ticker = c.ticker
   
   -- Slower
   SELECT * FROM stock_prices
   WHERE ticker IN (SELECT ticker FROM companies)
   ```

4. **Partition Analysis**: Use window functions wisely
   ```sql
   -- Calculate moving average efficiently
   AVG(price) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
   ```

---

## Exporting Results

### Export to CSV

```sql
SELECT * FROM stock_prices
WHERE ticker = 'AAPL'
INTO OUTFILE '/tmp/aapl_prices.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

### Use with Python

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://user:password@localhost/financial_analysis_db')

df = pd.read_sql("""
    SELECT * FROM stock_prices 
    WHERE ticker = 'AAPL'
""", engine)

df.to_csv('aapl_data.csv', index=False)
```

---

