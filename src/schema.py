"""
Database schema initialization script.
Creates all necessary tables for financial analysis.
"""

from src.db_config import DatabaseConfig, DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database(db_name: str):
    """Create the main database if it doesn't exist."""
    config = DatabaseConfig()
    connection = None
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            port=config.port
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        connection.commit()
        cursor.close()
        logger.info(f"Database '{db_name}' created or already exists")
    except Exception as err:
        logger.error(f"Error creating database: {err}")
        raise
    finally:
        if connection:
            connection.close()


def create_schema():
    """Create all tables in the database."""
    
    # First, select the database
    config = DatabaseConfig()
    connection = None
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            port=config.port,
            database=config.database
        )
        connection.close()
    except Exception:
        # Database might not exist yet, that's okay
        pass
    
    # Companies table
    companies_table = """
    CREATE TABLE IF NOT EXISTS companies (
        ticker VARCHAR(20) PRIMARY KEY,
        company_name VARCHAR(255) NOT NULL,
        sector VARCHAR(100),
        industry VARCHAR(100),
        country VARCHAR(50),
        currency VARCHAR(10),
        market_cap BIGINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    # Stock prices table
    stock_prices_table = """
    CREATE TABLE IF NOT EXISTS stock_prices (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ticker VARCHAR(20) NOT NULL,
        price_date DATE NOT NULL,
        opening_price DECIMAL(15, 2),
        closing_price DECIMAL(15, 2),
        highest_price DECIMAL(15, 2),
        lowest_price DECIMAL(15, 2),
        adjusted_close DECIMAL(15, 2),
        volume BIGINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_ticker_date (ticker, price_date),
        FOREIGN KEY (ticker) REFERENCES companies(ticker),
        INDEX idx_date (price_date),
        INDEX idx_ticker (ticker)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    # Financial statements table
    financials_table = """
    CREATE TABLE IF NOT EXISTS financial_statements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ticker VARCHAR(20) NOT NULL,
        statement_type ENUM('income', 'balance_sheet', 'cash_flow') NOT NULL,
        fiscal_date DATE NOT NULL,
        metric_name VARCHAR(100) NOT NULL,
        metric_value DECIMAL(20, 2),
        currency VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_statement (ticker, statement_type, fiscal_date, metric_name),
        FOREIGN KEY (ticker) REFERENCES companies(ticker),
        INDEX idx_ticker_date (ticker, fiscal_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    # Financial ratios table
    ratios_table = """
    CREATE TABLE IF NOT EXISTS financial_ratios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ticker VARCHAR(20) NOT NULL,
        ratio_date DATE NOT NULL,
        ratio_name VARCHAR(50) NOT NULL,
        ratio_value DECIMAL(15, 4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_ratio (ticker, ratio_date, ratio_name),
        FOREIGN KEY (ticker) REFERENCES companies(ticker),
        INDEX idx_ticker_date (ticker, ratio_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    # Market analysis table
    market_analysis_table = """
    CREATE TABLE IF NOT EXISTS market_analysis (
        id INT AUTO_INCREMENT PRIMARY KEY,
        analysis_date DATE NOT NULL,
        tickers VARCHAR(500),
        analysis_type VARCHAR(100) NOT NULL,
        result JSON NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_date (analysis_date),
        INDEX idx_type (analysis_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    # Indices table for market benchmarks
    indices_table = """
    CREATE TABLE IF NOT EXISTS market_indices (
        id INT AUTO_INCREMENT PRIMARY KEY,
        index_symbol VARCHAR(50) NOT NULL,
        index_name VARCHAR(255),
        index_date DATE NOT NULL,
        index_value DECIMAL(15, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_index (index_symbol, index_date),
        INDEX idx_date (index_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    tables = [
        ('companies', companies_table),
        ('stock_prices', stock_prices_table),
        ('financial_statements', financials_table),
        ('financial_ratios', ratios_table),
        ('market_analysis', market_analysis_table),
        ('market_indices', indices_table)
    ]
    
    for table_name, create_statement in tables:
        try:
            DatabaseManager.execute_update(create_statement)
            logger.info(f"Table '{table_name}' created successfully")
        except Exception as err:
            logger.error(f"Error creating table '{table_name}': {err}")
            raise


def init_database():
    """Initialize the complete database schema."""
    try:
        # Create database
        db_name = DatabaseConfig().database
        create_database(db_name)
        
        # Initialize connection pool
        config = DatabaseConfig()
        DatabaseManager.init_pool(config)
        
        # Create schema
        create_schema()
        
        logger.info("Database schema initialized successfully!")
        
    except Exception as err:
        logger.error(f"Failed to initialize database: {err}")
        raise


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    init_database()
