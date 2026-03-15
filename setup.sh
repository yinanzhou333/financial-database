#!/bin/bash

# Financial Database Setup Script
# This script automates the setup process

set -e  # Exit on any error

echo "======================================"
echo "Financial Analysis Database Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo -e "\n${YELLOW}Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install requirements
echo -e "\n${YELLOW}Installing Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Packages installed${NC}"

# Setup environment file
echo -e "\n${YELLOW}Setting up environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠ .env file created. Please edit it with your MySQL credentials:${NC}"
    echo "   - MYSQL_HOST"
    echo "   - MYSQL_USER"
    echo "   - MYSQL_PASSWORD"
    echo "   - MYSQL_DATABASE"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Check MySQL connection
echo -e "\n${YELLOW}Checking MySQL connection...${NC}"
python3 << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import mysql.connector
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'port': int(os.getenv('MYSQL_PORT', '3306'))
    }
    
    connection = mysql.connector.connect(**config)
    print("\033[0;32m✓ MySQL connection successful\033[0m")
    connection.close()
except Exception as e:
    print(f"\033[0;31m✗ MySQL connection failed: {e}\033[0m")
    print("\033[1;33mPlease ensure MySQL is running and .env credentials are correct\033[0m")
    exit(1)
EOF

# Initialize database
echo -e "\n${YELLOW}Initializing database schema...${NC}"
python3 << 'EOF'
from dotenv import load_dotenv
load_dotenv()

from src.schema import init_database
try:
    init_database()
    print("\033[0;32m✓ Database schema initialized\033[0m")
except Exception as e:
    print(f"\033[0;31m✗ Failed to initialize database: {e}\033[0m")
    exit(1)
EOF

echo -e "\n${GREEN}======================================"
echo "Setup Complete!"
echo "======================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your MySQL credentials"
echo "2. Run: python main.py"
echo ""
echo "Or step-by-step:"
echo "   python -c \"from src.data_download import download_all_data; download_all_data(['AAPL', 'MSFT'])\""
echo "   python -c \"from src.data_pipeline import DataPipeline; from src.db_config import DatabaseManager, DatabaseConfig; config = DatabaseConfig(); DatabaseManager.init_pool(config); DataPipeline().run()\""
echo ""
echo "Documentation:"
echo "   - README.md: Comprehensive documentation"
echo "   - QUICKSTART.md: Quick setup guide"
echo "   - CONFIG.md: Configuration guide"
echo "   - ANALYSIS_GUIDE.md: Analysis metrics explained"
echo "   - SQL_QUERIES.md: Ready-to-use SQL queries"
echo ""
