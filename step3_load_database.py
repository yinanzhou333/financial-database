#!/usr/bin/env python3
"""Step 3: Load Data into MySQL"""

from dotenv import load_dotenv
from src.db_config import DatabaseConfig, DatabaseManager
from src.data_pipeline import DataPipeline

load_dotenv()

print("Loading data into MySQL...")

# Initialize connection pool
config = DatabaseConfig()
DatabaseManager.init_pool(config)

# Run pipeline
pipeline = DataPipeline()
pipeline.run()

print("✅ Data loaded successfully!")
print("Check your MySQL database to verify:")
print("  - companies table: should have 5+ records")
print("  - stock_prices table: should have 1000+ records")
print("  - market_indices table: should have 500+ records")
