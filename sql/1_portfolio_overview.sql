-- ============================================================================
-- PORTFOLIO OVERVIEW QUERIES
-- Professional SQL queries for financial analysis and reporting
-- ============================================================================

-- 1. PORTFOLIO PERFORMANCE SUMMARY
-- Shows overall portfolio health with key metrics
SELECT 
    DATE_FORMAT(MAX(price_date), '%Y-%m-%d') as 'Last Updated',
    COUNT(DISTINCT ticker) as 'Total Stocks',
    COUNT(DISTINCT price_date) as 'Trading Days',
    ROUND(MIN(closing_price), 2) as 'Min Price',
    ROUND(MAX(closing_price), 2) as 'Max Price',
    ROUND(AVG(closing_price), 2) as 'Avg Price',
    ROUND(SUM(volume) / 1000000, 2) as 'Total Volume (M)'
FROM stock_prices;

-- 2. STOCK PERFORMANCE RANKING
-- Top performers by total return percentage
SELECT 
    sp.ticker,
    c.company_name,
    c.sector,
    ROUND(((last_price.closing_price - first_price.closing_price) / first_price.closing_price * 100), 2) as 'Total Return %',
    ROUND(last_price.closing_price, 2) as 'Current Price',
    ROUND(first_price.closing_price, 2) as 'Starting Price',
    ROUND(AVG(sp.volume), 0) as 'Avg Daily Volume',
    COUNT(*) as 'Days Traded'
FROM stock_prices sp
JOIN companies c ON sp.ticker = c.ticker
JOIN (
    SELECT ticker, closing_price 
    FROM stock_prices 
    WHERE price_date = (SELECT MAX(price_date) FROM stock_prices)
) last_price ON sp.ticker = last_price.ticker
JOIN (
    SELECT ticker, closing_price 
    FROM stock_prices 
    WHERE price_date = (SELECT MIN(price_date) FROM stock_prices)
) first_price ON sp.ticker = first_price.ticker
GROUP BY sp.ticker
ORDER BY 'Total Return %' DESC;

-- 3. DAILY VOLATILITY ANALYSIS
-- Shows recent volatility trends
SELECT 
    ticker,
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    ROUND(closing_price, 2) as 'Close',
    ROUND(((closing_price - opening_price) / opening_price * 100), 2) as 'Daily %',
    ROUND((highest_price - lowest_price) / lowest_price * 100, 2) as 'Range %',
    ROUND(volume / 1000000, 1) as 'Volume (M)'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY price_date DESC, ticker
LIMIT 100;

-- 4. PRICE MOMENTUM (30-DAY, 90-DAY, 1-YEAR)
-- Multi-period momentum analysis
SELECT 
    sp.ticker,
    c.company_name,
    ROUND(((d1.closing_price - d30.closing_price) / d30.closing_price * 100), 2) as '30d Momentum %',
    ROUND(((d1.closing_price - d90.closing_price) / d90.closing_price * 100), 2) as '90d Momentum %',
    ROUND(((d1.closing_price - d252.closing_price) / d252.closing_price * 100), 2) as '1Y Momentum %',
    ROUND(d1.closing_price, 2) as 'Current Price'
FROM stock_prices sp
JOIN companies c ON sp.ticker = c.ticker
JOIN (SELECT ticker, closing_price FROM stock_prices WHERE price_date = (SELECT MAX(price_date) FROM stock_prices)) d1 
    ON sp.ticker = d1.ticker
LEFT JOIN (SELECT ticker, closing_price FROM stock_prices WHERE price_date >= DATE_SUB((SELECT MAX(price_date) FROM stock_prices), INTERVAL 30 DAY) AND price_date < (SELECT MAX(price_date) FROM stock_prices) GROUP BY ticker ORDER BY price_date LIMIT 1) d30
    ON sp.ticker = d30.ticker
LEFT JOIN (SELECT ticker, closing_price FROM stock_prices WHERE price_date >= DATE_SUB((SELECT MAX(price_date) FROM stock_prices), INTERVAL 90 DAY) AND price_date < (SELECT MAX(price_date) FROM stock_prices) GROUP BY ticker ORDER BY price_date LIMIT 1) d90
    ON sp.ticker = d90.ticker
LEFT JOIN (SELECT ticker, closing_price FROM stock_prices WHERE price_date >= DATE_SUB((SELECT MAX(price_date) FROM stock_prices), INTERVAL 365 DAY) AND price_date < (SELECT MAX(price_date) FROM stock_prices) GROUP BY ticker ORDER BY price_date LIMIT 1) d252
    ON sp.ticker = d252.ticker
GROUP BY sp.ticker
ORDER BY '1Y Momentum %' DESC;

-- 5. SECTOR PERFORMANCE COMPARISON
-- Compare performance across sectors
SELECT 
    c.sector,
    COUNT(DISTINCT c.ticker) as 'Companies',
    ROUND(AVG(sp.closing_price), 2) as 'Avg Price',
    ROUND(MIN(sp.closing_price), 2) as 'Min Price',
    ROUND(MAX(sp.closing_price), 2) as 'Max Price',
    ROUND(STDDEV(sp.closing_price), 2) as 'Volatility',
    ROUND(AVG(sp.volume), 0) as 'Avg Volume'
FROM stock_prices sp
JOIN companies c ON sp.ticker = c.ticker
WHERE sp.price_date = (SELECT MAX(price_date) FROM stock_prices)
GROUP BY c.sector
ORDER BY 'Avg Price' DESC;

-- 6. TRADING VOLUME ANALYSIS
-- Identify high/low volume periods
SELECT 
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    COUNT(DISTINCT ticker) as 'Stocks Traded',
    ROUND(SUM(volume) / 1000000, 2) as 'Total Volume (M)',
    ROUND(AVG(volume), 0) as 'Avg Volume Per Stock',
    ROUND(MAX(volume), 0) as 'Peak Volume'
FROM stock_prices
GROUP BY DATE_FORMAT(price_date, '%Y-%m-%d')
ORDER BY 'Total Volume (M)' DESC
LIMIT 20;

-- 7. CORRELATION WITH MARKET INDICES
-- Compare stock performance vs S&P 500
SELECT 
    sp.ticker,
    c.company_name,
    ROUND((SELECT closing_price FROM stock_prices WHERE ticker = 'AAPL' AND price_date = (SELECT MAX(price_date) FROM stock_prices)) / 
          (SELECT closing_price FROM stock_prices WHERE ticker = 'AAPL' AND price_date = (SELECT MIN(price_date) FROM stock_prices)) - 1, 4) as 'SP500_Return',
    ROUND((SELECT closing_price FROM stock_prices WHERE ticker = sp.ticker AND price_date = (SELECT MAX(price_date) FROM stock_prices)) / 
          (SELECT closing_price FROM stock_prices WHERE ticker = sp.ticker AND price_date = (SELECT MIN(price_date) FROM stock_prices)) - 1, 4) as 'Stock_Return'
FROM companies c
JOIN stock_prices sp ON c.ticker = sp.ticker
GROUP BY sp.ticker;

-- 8. PRICE LEVEL ZONES (SUPPORT/RESISTANCE)
-- Identify key price levels
SELECT 
    ticker,
    ROUND(MIN(closing_price), 2) as '52W Low',
    ROUND(MAX(closing_price), 2) as '52W High',
    ROUND(AVG(closing_price), 2) as 'Average',
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY closing_price), 2) as 'Q1 (Support)',
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY closing_price), 2) as 'Median',
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY closing_price), 2) as 'Q3 (Resistance)'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
GROUP BY ticker
ORDER BY ticker;

-- 9. RECENT TRADING ACTIVITY
-- Last 10 days of data
SELECT 
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    ticker,
    ROUND(opening_price, 2) as 'Open',
    ROUND(closing_price, 2) as 'Close',
    ROUND(highest_price, 2) as 'High',
    ROUND(lowest_price, 2) as 'Low',
    ROUND(volume / 1000000, 1) as 'Volume (M)',
    ROUND((closing_price - opening_price) / opening_price * 100, 2) as 'Daily %'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 10 DAY)
ORDER BY price_date DESC, ticker;

-- 10. ANALYSIS HISTORY & INSIGHTS
-- View historical analysis results
SELECT 
    DATE_FORMAT(analysis_date, '%Y-%m-%d %H:%i') as 'Analysis Time',
    analysis_type,
    JSON_EXTRACT(result, '$.tickers') as 'Tickers Analyzed',
    JSON_EXTRACT(result, '$.report_date') as 'Report Date',
    ROUND(JSON_EXTRACT(result, '$.correlation_matrix."AAPL"."MSFT"'), 4) as 'AAPL-MSFT Correlation'
FROM market_analysis
ORDER BY analysis_date DESC
LIMIT 10;

-- ============================================================================
-- PERFORMANCE METRICS
-- ============================================================================

-- 11. BEST/WORST DAYS
SELECT 
    DATE_FORMAT(price_date, '%Y-%m-%d') as 'Date',
    ticker,
    ROUND(closing_price, 2) as 'Close',
    ROUND((closing_price - opening_price) / opening_price * 100, 2) as 'Daily Return %'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
ORDER BY 'Daily Return %' DESC
LIMIT 5;

-- 12. VOLATILITY RANKINGS
-- Which stocks are most/least volatile recently
SELECT 
    ticker,
    ROUND(STDDEV((closing_price - opening_price) / opening_price * 100), 2) as 'Volatility %',
    ROUND(AVG(closing_price), 2) as 'Avg Price',
    COUNT(*) as 'Days Traded'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY ticker
ORDER BY 'Volatility %' DESC;

-- ============================================================================
-- END OF PROFESSIONAL QUERIES
-- ============================================================================
