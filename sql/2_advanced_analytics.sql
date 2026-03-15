-- ============================================================================
-- ADVANCED FINANCIAL ANALYTICS QUERIES
-- Complex calculations for institutional-grade analysis
-- ============================================================================

-- 1. MOVING AVERAGES & TREND ANALYSIS
-- 20-day, 50-day, and 200-day moving averages
SELECT 
    ticker,
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    ROUND(closing_price, 2) as 'Close',
    ROUND(AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2) as 'MA20',
    ROUND(AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2) as 'MA50',
    ROUND(AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW), 2) as 'MA200',
    CASE 
        WHEN closing_price > AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) THEN 'Bullish'
        ELSE 'Bearish'
    END as 'Trend'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 200 DAY)
ORDER BY ticker, price_date DESC
LIMIT 50;

-- 2. RELATIVE STRENGTH INDEX (RSI) CALCULATION
-- 14-period RSI for momentum identification
SELECT 
    ticker,
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    ROUND(closing_price, 2) as 'Close',
    ROUND(
        100 - (100 / (1 + (
            AVG(CASE WHEN closing_price > LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) 
                     THEN closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) 
                     ELSE 0 END) 
            OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
        ) / (
            AVG(CASE WHEN closing_price < LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) 
                     THEN LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) - closing_price
                     ELSE 0 END)
            OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
        ))), 2) as 'RSI_14',
    CASE
        WHEN 100 - (100 / (1 + (
            AVG(CASE WHEN closing_price > LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) 
                     THEN closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) 
                     ELSE 0 END) 
            OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
        ) / (
            AVG(CASE WHEN closing_price < LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) 
                     THEN LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) - closing_price
                     ELSE 0 END)
            OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
        ))) > 70 THEN 'OVERBOUGHT'
        WHEN 100 - (100 / (1 + (
            AVG(CASE WHEN closing_price > LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) 
                     THEN closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) 
                     ELSE 0 END) 
            OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
        ) / (
            AVG(CASE WHEN closing_price < LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) 
                     THEN LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) - closing_price
                     ELSE 0 END)
            OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
        ))) < 30 THEN 'OVERSOLD'
        ELSE 'NEUTRAL'
    END as 'Signal'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 100 DAY)
ORDER BY ticker, price_date DESC
LIMIT 50;

-- 3. BOLLINGER BANDS
-- 20-day Bollinger Bands for volatility
SELECT 
    ticker,
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    ROUND(closing_price, 2) as 'Close',
    ROUND(AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2) as 'BB_Middle',
    ROUND(
        AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) + 
        2 * STDDEV(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        2
    ) as 'BB_Upper',
    ROUND(
        AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) - 
        2 * STDDEV(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        2
    ) as 'BB_Lower',
    CASE 
        WHEN closing_price > 
            AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) + 
            2 * STDDEV(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
        THEN 'Above Upper Band'
        WHEN closing_price < 
            AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) - 
            2 * STDDEV(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
        THEN 'Below Lower Band'
        ELSE 'Within Band'
    END as 'Position'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 50 DAY)
ORDER BY ticker, price_date DESC
LIMIT 50;

-- 4. VOLUME WEIGHTED AVERAGE PRICE (VWAP)
-- VWAP for each stock
SELECT 
    ticker,
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    ROUND(closing_price, 2) as 'Close',
    ROUND(
        SUM(closing_price * volume) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) /
        SUM(volume) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        2
    ) as 'VWAP_20d',
    ROUND(volume / 1000000, 2) as 'Volume (M)',
    CASE
        WHEN closing_price > ROUND(
            SUM(closing_price * volume) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) /
            SUM(volume) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
        THEN 'Above VWAP'
        ELSE 'Below VWAP'
    END as 'Price_vs_VWAP'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 50 DAY)
ORDER BY ticker, price_date DESC
LIMIT 50;

-- 5. DAILY RETURNS & LOG RETURNS
-- Calculate daily and cumulative returns
SELECT 
    ticker,
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    ROUND(closing_price, 2) as 'Close',
    ROUND((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) / 
          LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date) * 100, 3) as 'Daily_Return %',
    ROUND(
        SUM((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) / 
            LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) 
        OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) * 100,
        2
    ) as 'Cumulative_Return %'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY ticker, price_date DESC
LIMIT 50;

-- 6. INTRADAY RANGE & VOLATILITY
-- High-Low range as percentage of close
SELECT 
    ticker,
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    ROUND(opening_price, 2) as 'Open',
    ROUND(highest_price, 2) as 'High',
    ROUND(lowest_price, 2) as 'Low',
    ROUND(closing_price, 2) as 'Close',
    ROUND((highest_price - lowest_price) / closing_price * 100, 2) as 'Daily_Range %',
    ROUND(((closing_price - opening_price) / opening_price) * 100, 2) as 'Open_to_Close %',
    ROUND(volume / 1000000, 1) as 'Volume (M)'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 20 DAY)
ORDER BY ticker, price_date DESC;

-- 7. CORRELATION ANALYSIS
-- Pairwise correlation between stocks
SELECT 
    a.ticker as 'Stock_1',
    b.ticker as 'Stock_2',
    ROUND(
        (SUM((a_close - a_avg) * (b_close - b_avg)) / SQRT(SUM(POW(a_close - a_avg, 2)) * SUM(POW(b_close - b_avg, 2)))),
        4
    ) as 'Correlation'
FROM (
    SELECT 
        ticker,
        closing_price as a_close,
        AVG(closing_price) OVER (PARTITION BY ticker) as a_avg
    FROM stock_prices
    WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 252 DAY)
) a
CROSS JOIN (
    SELECT 
        ticker,
        closing_price as b_close,
        AVG(closing_price) OVER (PARTITION BY ticker) as b_avg
    FROM stock_prices
    WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 252 DAY)
) b
WHERE a.ticker < b.ticker
GROUP BY a.ticker, b.ticker
ORDER BY 'Correlation' DESC;

-- 8. SHARPE RATIO CALCULATION
-- Risk-adjusted returns (assuming 5% risk-free rate)
SELECT 
    ticker,
    ROUND(
        (AVG((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) / 
             LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) * 252 - 0.05) /
        (STDDEV((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) / 
                LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) * SQRT(252)),
        4
    ) as 'Sharpe_Ratio',
    ROUND(AVG((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) / 
             LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) * 252, 4) as 'Annual_Return',
    ROUND(STDDEV((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) / 
                LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) * SQRT(252), 4) as 'Annual_Volatility'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 252 DAY)
GROUP BY ticker
ORDER BY 'Sharpe_Ratio' DESC;

-- ============================================================================
-- END OF ADVANCED ANALYTICS
-- ============================================================================
