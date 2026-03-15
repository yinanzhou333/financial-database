# Financial Database & Analysis System

A professional Python + MySQL system for downloading financial data, building a normalized database, and performing sophisticated quantitative financial analysis.

## 🎯 Highlights

This project demonstrates:
- ✅ **Professional Data Engineering**: Complete ETL pipeline with MySQL integration
- ✅ **Financial Analysis**: 6+ sophisticated metrics (Sharpe, Volatility, RSI, Moving Averages, Momentum, Correlation)
- ✅ **Advanced SQL**: Window functions, correlations, technical indicators, aggregations
- ✅ **Data Visualization**: 8+ professional charts for comprehensive analysis
- ✅ **Database Design**: Normalized schema with 6 interconnected tables and proper indexing
- ✅ **Clean Code**: Modular architecture with logging, error handling, and best practices
- ✅ **Professional Documentation**: Comprehensive guides, SQL queries, and setup instructions

## 📂 Project Structure

```
financial-database/
├── src/                              # Python modules
│   ├── db_config.py                 # MySQL connection pooling
│   ├── schema.py                    # Database schema (6 tables)
│   ├── data_download.py             # Yahoo Finance integration
│   ├── data_pipeline.py             # ETL pipeline
│   ├── analysis.py                  # 6 financial metrics
│   └── utilities.py                 # Formatting & exports
├── sql/                              # Professional SQL queries
│   ├── 1_portfolio_overview.sql     # Portfolio analytics (12 queries)
│   └── 2_advanced_analytics.sql     # Technical indicators (8 queries)
├── data/                             # Downloaded CSV files
├── output/
│   ├── visualizations/              # Generated charts (PNG)
│   └── analysis_reports/            # JSON reports
├── step1_create_schema.py           # Database initialization
├── step2_download_data.py           # Data download
├── step3_load_database.py           # ETL process
├── step4_run_analysis.py            # Analysis engine
├── step5_export_results.py          # Export results
├── requirements.txt                  # Dependencies
├── .env                             # Configuration
├── SIMPLE_STEPS.md                  # Quick start guide
├── SQL_QUERIES.md                   # SQL reference
└── README.md                         # This file
```

## 💾 Database Architecture

**Database:** `financial_analysis_db`

**6 Normalized Tables:**

| Table | Purpose | Records |
|-------|---------|---------|
| `companies` | Stock metadata | 5-10 |
| `stock_prices` | Daily OHLCV data | 1000+ |
| `financial_statements` | Fundamentals | 50+ |
| `financial_ratios` | Calculated metrics | 100+ |
| `market_analysis` | Analysis results (JSON) | 1 per run |
| `market_indices` | S&P 500, Dow, Nasdaq | 500+ |

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /Users/yz/github/financial-database
source myenv/bin/activate
pip install -r requirements.txt
```

### 2. Configure MySQL
Update `.env` with your credentials:
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=financial_analysis_db
MYSQL_PORT=3306
```

### 3. Run Complete Pipeline
```bash
python3 main.py
```

**Or run step-by-step:**
```bash
python3 step1_create_schema.py      # 1 min  - Create database
python3 step2_download_data.py      # 3-5 min - Download data
python3 step3_load_database.py      # 2-3 min - ETL to MySQL
python3 step4_run_analysis.py       # 2-3 min - Financial analysis
python3 step5_export_results.py     # 1 min  - Export results
```

## 📊 Professional Visualizations

### Generate Charts
```bash
python3 create_visuals.py
```

### Generated Charts

```
📈 01_price_trends.png              - 90-day price movements
📊 02_performance_comparison.png     - Normalized returns comparison
📉 03_volatility_analysis.png        - 20-day rolling volatility
💹 04_trading_volume.png             - Daily volume patterns
🔗 05_correlation_heatmap.png        - Stock return correlations
📐 06_returns_distribution.png       - Histogram of daily returns
💰 07_cumulative_returns.png         - Total return tracking
🏭 08_sector_analysis.png            - Performance by sector
```

## 🔍 Advanced SQL Analytics

### Overview (12 queries)
```bash
cat sql/1_portfolio_overview.sql
```

**Professional Queries:**
- Performance summary
- Stock performance ranking by return %
- Daily volatility analysis
- Multi-period momentum (30d, 90d, 1Y)
- Sector comparison analysis
- Trading volume trends
- Support/resistance levels (52-week high/low, quartiles)
- Recent trading activity
- Historical analysis records
- Best/worst days
- Volatility rankings

### Advanced Technical Analysis (8 queries)
```bash
cat sql/2_advanced_analytics.sql
```

**Institutional-Grade Techniques:**
- Moving Averages (MA20, MA50, MA200) with trend signals
- Relative Strength Index (RSI-14) with overbought/oversold detection
- Bollinger Bands (20-day) with position detection
- Volume Weighted Average Price (VWAP-20d)
- Daily & cumulative returns
- Intraday range analysis
- Correlation matrices between stocks
- Sharpe Ratio calculations

## 💻 Query Examples

### In MySQL CLI
```bash
mysql -u root -p financial_analysis_db
```

**Top Performers (30-day momentum):**
```sql
SELECT ticker, company_name, sector,
  ROUND(((last_price - first_price) / first_price * 100), 2) as 'Return %'
FROM companies c
ORDER BY 'Return %' DESC;
```

**Volatility Rankings (90-day):**
```sql
SELECT ticker, 
  ROUND(STDDEV((closing_price - LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) /
        LAG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date)) * SQRT(252) * 100, 2) as 'Annual Volatility %'
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY ticker
ORDER BY 'Annual Volatility %' DESC;
```

**Moving Averages Crossover Signal:**
```sql
SELECT ticker, price_date, closing_price,
  AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as MA20,
  AVG(closing_price) OVER (PARTITION BY ticker ORDER BY price_date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) as MA50,
  CASE WHEN MA20 > MA50 THEN 'Bullish' ELSE 'Bearish' END as Signal
FROM stock_prices
WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 100 DAY)
ORDER BY ticker, price_date DESC
LIMIT 50;
```

### In VS Code
1. Install **MySQL** extension (Jun Han)
2. Connect to localhost:3306
3. Browse tables with autocomplete
4. Execute queries with syntax highlighting
5. View results in beautiful tables

## 📈 Financial Metrics Calculated

### 6 Core Metrics

| Metric | Purpose | Formula |
|--------|---------|---------|
| **Volatility** | Risk measurement | STDEV(returns) × √252 |
| **Sharpe Ratio** | Risk-adjusted returns | (Mean Return - Risk Free Rate) / Volatility |
| **Correlation** | Relationship strength | Covariance(Stock_A, Stock_B) / (σ_A × σ_B) |
| **Momentum** | Trend strength | (Price_T / Price_T-N - 1) × 100% |
| **Moving Averages** | Trend direction | SMA(20), SMA(50), SMA(200) |
| **RSI** | Overbought/oversold | 100 - (100 / (1 + RS)) where RS = gain/loss |

## 🎓 Data Engineering Highlights

### ETL Pipeline
- **Extract**: Yahoo Finance API via yfinance
- **Transform**: Data cleaning, type conversion, normalization
- **Load**: Batch inserts with ON DUPLICATE KEY UPDATE

### Database Optimization
- Connection pooling for performance
- Proper indexing on all queries
- Normalized schema preventing data redundancy
- Foreign keys ensuring referential integrity

### Data Quality
- NULL handling and validation
- Type conversion with error coercion
- Duplicate prevention with UNIQUE constraints
- Date validation and sorting

## 📚 Documentation

| File | Purpose |
|------|---------|
| `SIMPLE_STEPS.md` | Copy-paste commands for each step |
| `STEP_BY_STEP.md` | Detailed walkthrough with output |
| `MYSQL_FIX.md` | MySQL setup & troubleshooting |
| `SQL_QUERIES.md` | Comprehensive SQL reference |

## 🔧 Troubleshooting

### MySQL Connection Error
```bash
# Test connection
python3 mysql_helper.py test_connection

# Update .env with correct password
cat .env.example > .env
# Edit .env with your credentials
```

### No Data Downloaded
- Check internet connection
- Verify ticker symbols (AAPL, MSFT, GOOGL, TSLA, AMZN)
- Check date range in `.env`

### Database Already Exists
- Normal! Safe to re-run
- Existing data is preserved
- Uses `CREATE TABLE IF NOT EXISTS`

## 💡 Customization

### Change Stocks
Edit `step2_download_data.py`:
```python
tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']  # Modify this list
```

### Change Date Range
Edit `.env`:
```env
START_DATE=2022-01-01
END_DATE=2024-12-31
```

### Add Metrics
Edit `src/analysis.py` to add new financial metrics or indicators.

## 📊 Results

After running the pipeline, check:
- **Database**: `mysql -u root -p financial_analysis_db`
- **Visualizations**: `ls output/visualizations/`
- **JSON Report**: `cat output/analysis_report_*.json`
- **CSV Data**: `ls -lh data/`


## 📦 Dependencies

- **Python 3.9+**: Programming language
- **MySQL 8.0+**: Relational database
- **pandas**: Data manipulation
- **NumPy**: Numerical computing
- **matplotlib/seaborn**: Data visualization
- **yfinance**: Yahoo Finance API
- **mysql-connector-python**: MySQL driver
- **python-dotenv**: Environment variables


