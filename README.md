# Financial Database & Analysis System

A complete Python + MySQL system for downloading financial data, building a professional database, and performing quantitative financial analysis.

## 📂 Project Structure

```
financial-database/
├── src/                          # Python source code
│   ├── db_config.py             # MySQL connection & pooling
│   ├── schema.py                # Database schema creation
│   ├── data_download.py         # Yahoo Finance data download
│   ├── data_pipeline.py         # ETL (CSV → MySQL)
│   ├── analysis.py              # Financial analysis engine
│   └── utilities.py             # Helper functions
├── data/                         # Downloaded CSV files
├── output/                       # Generated reports (JSON)
├── .env                         # MySQL credentials (ignored in git)
├── .env.example                 # Example .env template
├── main.py                      # Main pipeline orchestrator
├── requirements.txt             # Python dependencies
└── step*.py                     # Individual step scripts
```

## 💾 Database Location

**MySQL Database:** `financial_analysis_db`

**Stored at:** Wherever MySQL is installed on your system (typically `/usr/local/var/mysql` on macOS)

**Database Host:** localhost (from `.env`)

**Connection:** `mysql -u root -p financial_analysis_db`

## 🚀 Quick Start

### 1. Setup
```bash
cd /Users/yz/github/financial-database
source myenv/bin/activate
pip install -r requirements.txt
```

### 2. Configure MySQL Credentials
Update `.env` with your MySQL credentials:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=financial_analysis_db
MYSQL_PORT=3306
```

### 3. Run Pipeline

**Option A: Run all steps at once**
```bash
python3 main.py
```

**Option B: Run steps individually**
```bash
python3 step1_create_schema.py      # Create database & schema (1 min)
python3 step2_download_data.py      # Download stock data (3-5 min)
python3 step3_load_database.py      # Load into MySQL (2-3 min)
python3 step4_run_analysis.py       # Run analysis (2-3 min)
python3 step5_export_results.py     # Export results (1 min)
```

**Total time:** 10-15 minutes

## 📊 What Gets Created

### 6 Database Tables

| Table | Purpose | Records |
|-------|---------|---------|
| `companies` | Stock metadata (name, sector, exchange) | 5-10 |
| `stock_prices` | Daily OHLCV data | 1000+ |
| `financial_statements` | Income/balance/cash flow | 50+ |
| `financial_ratios` | Calculated metrics | 100+ |
| `market_analysis` | Analysis results (JSON) | 1 per run |
| `market_indices` | S&P 500, Dow Jones, Nasdaq | 500+ |

### 6 Financial Metrics

1. **Volatility** - Daily, annual, rolling 30-day
2. **Sharpe Ratio** - Risk-adjusted returns
3. **Correlation Matrix** - Multi-stock correlations
4. **Price Momentum** - Trend analysis
5. **Moving Averages** - MA20, MA50, MA200
6. **RSI** - Relative Strength Index (14-day)

## 📋 Documentation

| File | Purpose |
|------|---------|
| `SIMPLE_STEPS.md` | Copy-paste commands for each step ⭐ |
| `SQL_QUERIES.md` | Useful queries to explore the database |

## 📁 Key Files

### Main Application
- `main.py` - Orchestrates all 5 steps
- `src/db_config.py` - MySQL connection management
- `src/schema.py` - Database initialization
- `src/data_download.py` - Yahoo Finance downloader
- `src/data_pipeline.py` - ETL pipeline
- `src/analysis.py` - Financial analysis engine
- `src/utilities.py` - Helper functions

### Configuration
- `.env` - MySQL credentials (create from `.env.example`)
- `requirements.txt` - Python dependencies
- `myenv/` - Virtual environment

### Results
- `data/` - Downloaded CSV files
- `output/` - Generated analysis reports (JSON)

## 🔍 Explore Results

### In Python
```python
import json
with open('output/analysis_report_*.json') as f:
    report = json.load(f)
    print(report)
```

### In MySQL
```bash
mysql -u root -p financial_analysis_db
SELECT * FROM companies;
SELECT ticker, AVG(closing_price) FROM stock_prices GROUP BY ticker;
SELECT * FROM market_analysis ORDER BY analysis_date DESC LIMIT 1;
```

### In VS Code
1. Install MySQL extension (Jun Han)
2. Connect to localhost:3306
3. Browse tables and run queries

## ⚙️ Troubleshooting

### MySQL Connection Error
Update `.env` with correct credentials. Test with:
```bash
python3 mysql_helper.py test_connection
```

### No Data Downloaded
- Check internet connection
- Verify ticker symbols (AAPL, MSFT, etc.)
- Try fewer tickers

### Database Already Exists
- Normal! `CREATE TABLE IF NOT EXISTS` prevents errors
- Tables are preserved across runs

## 📈 Next Steps

1. ✅ Run the pipeline (Steps 1-5)
2. ✅ Review data in MySQL
3. Customize stock tickers in `step2_download_data.py`
4. Adjust date ranges in `.env`
5. Add more financial metrics to `src/analysis.py`

## � Portfolio & Visualizations

### Create Professional Charts
After running the pipeline:

```bash
python3 create_portfolio_visuals.py
```

This generates 5 professional visualizations perfect for GitHub portfolios:
- 📈 Stock Performance Comparison
- 📊 Risk vs Return Analysis
- 📉 Price Trends Over Time
- 💰 Trading Volume Analysis
- 🔥 Monthly Returns Heatmap

### Impressive SQL Queries
See `PORTFOLIO_QUERIES.md` for 9 portfolio-ready SQL queries:
1. Stock performance ranking
2. Monthly performance trends
3. Volatility analysis
4. Trading volume analysis
5. Best & worst trading days
6. Correlation analysis
7. Performance vs market index
8. Year-to-date performance
9. Analysis metadata

## �💡 Need Help?

- See `SIMPLE_STEPS.md` for copy-paste commands
- See `PORTFOLIO_QUERIES.md` for impressive SQL queries & analysis
- See `MYSQL_FIX.md` for database connection troubleshooting

---

