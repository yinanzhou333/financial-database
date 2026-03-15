#!/usr/bin/env python3
"""Step 5: Export & View Results"""

from dotenv import load_dotenv
from src.db_config import DatabaseConfig, DatabaseManager
import json
from datetime import datetime
import os

load_dotenv()

# Initialize database
config = DatabaseConfig()
DatabaseManager.init_pool(config)

# Get latest analysis from database
results = DatabaseManager.execute_query(
    "SELECT result FROM market_analysis ORDER BY analysis_date DESC LIMIT 1"
)

if results:
    report = json.loads(results[0]['result'])
    
    # Save to file
    os.makedirs('output', exist_ok=True)
    filename = f"output/analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"✅ Report saved to: {filename}")
    print("\nReport contents:")
    print(json.dumps(report, indent=2, default=str)[:1000] + "\n...")
else:
    print("No analysis results found in database")
