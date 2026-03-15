#!/usr/bin/env python3
"""Step 1: Create Database & Schema"""

from dotenv import load_dotenv
from src.schema import init_database

load_dotenv()
print("Creating database and schema...")
init_database()
print("✅ Database and schema created successfully!")
