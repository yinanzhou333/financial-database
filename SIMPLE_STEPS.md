# Step-by-Step Execution - Simple Commands

Run each step one at a time. Just copy and paste ONE command at a time:

---

## Step 1: Create Database & Schema

```bash
python3 step1_create_schema.py
```

Expected output:
```
Creating database and schema...
✅ Database and schema created successfully!
```

---

## Step 2: Download Raw Data

```bash
python3 step2_download_data.py
```

Expected output:
```
Downloading data for: AAPL, MSFT, GOOGL, TSLA, AMZN
This may take 3-5 minutes...
✅ Data downloaded successfully!
Check data/ folder for CSV files:
  - company_info.csv
  - stock_prices.csv
  - financials_quarterly.csv
  - market_indices.csv
```

Time: **3-5 minutes**

---

## Step 3: Load Data into MySQL

```bash
python3 step3_load_database.py
```

Expected output:
```
Loading data into MySQL...
✅ Data loaded successfully!
Check your MySQL database to verify:
  - companies table: should have 5+ records
  - stock_prices table: should have 1000+ records
  - market_indices table: should have 500+ records
```

Time: **2-3 minutes**

---

## Step 4: Run Financial Analysis

```bash
python3 step4_run_analysis.py
```

Expected output:
```
Running financial analysis...
✅ Analysis complete!

Sample results for AAPL:
  Sharpe Ratio: 0.87
  Annual Return: 15.23%
  Annual Volatility: 28.50%

Full report saved to database (market_analysis table)
```

Time: **2-3 minutes**

---

## Step 5: Export & View Results

```bash
python3 step5_export_results.py
```

Expected output:
```
✅ Report saved to: output/analysis_report_20260315_111030.json

Report contents:
{
  "report_date": "2026-03-15",
  "tickers": ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"],
  ...
```

Time: **1 minute**

---

## Summary

| Command | What It Does | Time |
|---------|-------------|------|
| `python3 step1_create_schema.py` | Create database & 6 tables | 1 min |
| `python3 step2_download_data.py` | Download stock data from Yahoo Finance | 3-5 min |
| `python3 step3_load_database.py` | Load data into MySQL | 2-3 min |
| `python3 step4_run_analysis.py` | Calculate financial metrics | 2-3 min |
| `python3 step5_export_results.py` | Save results to JSON file | 1 min |
| **Total** | Complete pipeline | **10-15 min** |

---


