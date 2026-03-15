#!/usr/bin/env python3
"""Step 4: Run Financial Analysis"""

from dotenv import load_dotenv
from src.db_config import DatabaseConfig, DatabaseManager
from src.analysis import FinancialAnalyzer
import json

load_dotenv()

print("Running financial analysis...")

# Initialize database
config = DatabaseConfig()
DatabaseManager.init_pool(config)

# Run analysis
analyzer = FinancialAnalyzer(risk_free_rate=0.05)
tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

report = analyzer.generate_comprehensive_report(tickers)
analyzer.save_analysis_to_db(tickers, report)

# Print sample results
print("✅ Analysis complete!")
print("\nSample results for AAPL:")
aapl_analysis = report.get('individual_analysis', {}).get('AAPL', {})
if aapl_analysis:
    sharpe = aapl_analysis.get('sharpe_ratio', {})
    print(f"  Sharpe Ratio: {sharpe.get('sharpe_ratio', 'N/A')}")
    print(f"  Annual Return: {sharpe.get('annual_return', 0)*100:.2f}%")
    print(f"  Annual Volatility: {sharpe.get('annual_volatility', 0)*100:.2f}%")

print("\nFull report saved to database (market_analysis table)")
