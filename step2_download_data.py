#!/usr/bin/env python3
"""Step 2: Download Raw Data"""

from dotenv import load_dotenv
from src.data_download import download_all_data

load_dotenv()

tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
print(f"Downloading data for: {', '.join(tickers)}")
print("This may take 3-5 minutes...")

download_all_data(tickers, start_date='2022-01-01', end_date='2024-12-31')

print("✅ Data downloaded successfully!")
print("Check data/ folder for CSV files:")
print("  - company_info.csv")
print("  - stock_prices.csv")
print("  - financials_quarterly.csv")
print("  - market_indices.csv")
