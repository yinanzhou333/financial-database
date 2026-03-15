"""
Data ingestion pipeline.
Transforms raw CSV data and loads it into MySQL database.
"""

import pandas as pd
import os
from datetime import datetime
import logging
from src.db_config import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPipeline:
    """ETL pipeline for loading financial data into database."""
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize pipeline.
        
        Args:
            data_dir: Directory containing raw CSV files
        """
        self.data_dir = data_dir
    
    def load_companies(self):
        """Load company information into database."""
        logger.info("Loading company information...")
        
        csv_path = os.path.join(self.data_dir, 'company_info.csv')
        if not os.path.exists(csv_path):
            logger.warning(f"Company info file not found: {csv_path}")
            return
        
        df = pd.read_csv(csv_path)
        
        # Clean data
        df['ticker'] = df['ticker'].str.upper()
        df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce')
        df['currency'] = df['currency'].fillna('USD')
        
        # Prepare batch insert
        insert_query = """
        INSERT INTO companies 
        (ticker, company_name, sector, industry, country, currency, market_cap)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            company_name=VALUES(company_name),
            sector=VALUES(sector),
            industry=VALUES(industry),
            market_cap=VALUES(market_cap),
            updated_at=CURRENT_TIMESTAMP
        """
        
        params_list = [
            (
                row['ticker'],
                row['company_name'],
                row['sector'] if pd.notna(row['sector']) else None,
                row['industry'] if pd.notna(row['industry']) else None,
                row['country'] if pd.notna(row['country']) else None,
                row['currency'],
                int(row['market_cap']) if pd.notna(row['market_cap']) else None
            )
            for _, row in df.iterrows()
        ]
        
        try:
            affected_rows = DatabaseManager.execute_batch(insert_query, params_list)
            logger.info(f"Loaded {affected_rows} company records")
        except Exception as e:
            logger.error(f"Error loading companies: {e}")
            raise
    
    def load_stock_prices(self):
        """Load stock price data into database."""
        logger.info("Loading stock prices...")
        
        csv_path = os.path.join(self.data_dir, 'stock_prices.csv')
        if not os.path.exists(csv_path):
            logger.warning(f"Stock prices file not found: {csv_path}")
            return
        
        df = pd.read_csv(csv_path)
        
        # Standardize column names: lowercase and replace spaces with underscores
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Convert date column to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Convert ticker to uppercase
        if 'ticker' in df.columns:
            df['ticker'] = df['ticker'].str.upper()
        
        # Rename columns to match database schema
        rename_map = {
            'date': 'price_date',
            'ticker': 'ticker',
            'open': 'opening_price',
            'high': 'highest_price',
            'low': 'lowest_price',
            'close': 'closing_price',
            'adj_close': 'adjusted_close',
            'volume': 'volume'
        }
        
        df = df.rename(columns=rename_map)
        
        # Select only needed columns
        needed_cols = ['ticker', 'price_date', 'opening_price', 'closing_price', 
                      'highest_price', 'lowest_price', 'adjusted_close', 'volume']
        available_cols = [col for col in needed_cols if col in df.columns]
        df = df[available_cols]
        
        # Convert types
        for col in ['opening_price', 'closing_price', 'highest_price', 'lowest_price', 'adjusted_close']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').astype('Int64')
        
        # Remove rows with missing ticker
        df = df.dropna(subset=['ticker'])
        
        # Prepare batch insert
        insert_query = """
        INSERT INTO stock_prices 
        (ticker, price_date, opening_price, closing_price, highest_price, lowest_price, adjusted_close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            opening_price=VALUES(opening_price),
            closing_price=VALUES(closing_price),
            highest_price=VALUES(highest_price),
            lowest_price=VALUES(lowest_price),
            adjusted_close=VALUES(adjusted_close),
            volume=VALUES(volume)
        """
        
        params_list = [
            (
                row['ticker'],
                row['price_date'],
                float(row['opening_price']) if pd.notna(row['opening_price']) else None,
                float(row['closing_price']) if pd.notna(row['closing_price']) else None,
                float(row['highest_price']) if pd.notna(row['highest_price']) else None,
                float(row['lowest_price']) if pd.notna(row['lowest_price']) else None,
                float(row['adjusted_close']) if pd.notna(row['adjusted_close']) else None,
                int(row['volume']) if pd.notna(row['volume']) else None
            )
            for _, row in df.iterrows()
        ]
        
        try:
            affected_rows = DatabaseManager.execute_batch(insert_query, params_list)
            logger.info(f"Loaded {affected_rows} stock price records")
        except Exception as e:
            logger.error(f"Error loading stock prices: {e}")
            raise
    
    def load_market_indices(self):
        """Load market indices data into database."""
        logger.info("Loading market indices...")
        
        csv_path = os.path.join(self.data_dir, 'market_indices.csv')
        if not os.path.exists(csv_path):
            logger.warning(f"Market indices file not found: {csv_path}")
            return
        
        df = pd.read_csv(csv_path)
        
        # Standardize
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        date_col = 'date' if 'date' in df.columns else next((col for col in df.columns if 'date' in col.lower()), None)
        index_col = 'index' if 'index' in df.columns else 'ticker'
        
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col])
        
        # Rename columns
        rename_map = {
            date_col: 'index_date',
            index_col: 'index_symbol',
            'close': 'index_value',
            'adj close': 'index_value'
        }
        
        df = df.rename(columns=rename_map)
        
        # Select needed columns
        needed_cols = ['index_symbol', 'index_date', 'index_value']
        available_cols = [col for col in needed_cols if col in df.columns]
        
        if not available_cols:
            logger.warning("No valid columns found in market indices file")
            return
        
        df = df[available_cols]
        df['index_value'] = pd.to_numeric(df['index_value'], errors='coerce')
        df = df.dropna(subset=['index_symbol', 'index_date', 'index_value'])
        
        # Prepare batch insert
        insert_query = """
        INSERT INTO market_indices 
        (index_symbol, index_date, index_value)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            index_value=VALUES(index_value)
        """
        
        params_list = [
            (
                row['index_symbol'],
                row['index_date'],
                float(row['index_value'])
            )
            for _, row in df.iterrows()
        ]
        
        try:
            affected_rows = DatabaseManager.execute_batch(insert_query, params_list)
            logger.info(f"Loaded {affected_rows} market index records")
        except Exception as e:
            logger.error(f"Error loading market indices: {e}")
            raise
    
    def run(self):
        """Run the complete pipeline."""
        try:
            logger.info("Starting data ingestion pipeline...")
            self.load_companies()
            self.load_stock_prices()
            self.load_market_indices()
            logger.info("Data ingestion completed successfully!")
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    from src.db_config import DatabaseConfig
    
    # Initialize database connection
    config = DatabaseConfig()
    DatabaseManager.init_pool(config)
    
    # Run pipeline
    pipeline = DataPipeline()
    pipeline.run()
