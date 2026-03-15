"""
Database connection and configuration module.
Handles MySQL connection pooling and cursor management.
"""

import mysql.connector
from mysql.connector import pooling, Error
import os
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Configuration class for MySQL database connection."""
    
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DATABASE', 'financial_analysis_db')
        self.port = int(os.getenv('MYSQL_PORT', '3306'))
    
    def to_dict(self):
        return {
            'host': self.host,
            'user': self.user,
            'password': self.password,
            'port': self.port,
            'database': self.database
        }


class DatabaseManager:
    """Manages MySQL database connections and operations."""
    
    _pool: Optional[pooling.MySQLConnectionPool] = None
    
    @classmethod
    def init_pool(cls, config: DatabaseConfig, pool_size: int = 5):
        """Initialize connection pool."""
        try:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name='financial_pool',
                pool_size=pool_size,
                pool_reset_session=True,
                **config.to_dict()
            )
            logger.info("Connection pool initialized successfully")
        except Error as err:
            logger.error(f"Error initializing pool: {err}")
            raise
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool."""
        if cls._pool is None:
            raise Exception("Connection pool not initialized. Call init_pool first.")
        return cls._pool.get_connection()
    
    @classmethod
    def execute_query(cls, query: str, params: tuple = None) -> list:
        """Execute a SELECT query and return results."""
        connection = cls.get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as err:
            logger.error(f"Query execution error: {err}")
            raise
        finally:
            connection.close()
    
    @classmethod
    def execute_update(cls, query: str, params: tuple = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query."""
        connection = cls.get_connection()
        try:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Error as err:
            connection.rollback()
            logger.error(f"Update execution error: {err}")
            raise
        finally:
            connection.close()
    
    @classmethod
    def execute_batch(cls, query: str, params_list: list) -> int:
        """Execute multiple INSERT/UPDATE operations in batch."""
        connection = cls.get_connection()
        try:
            cursor = connection.cursor()
            cursor.executemany(query, params_list)
            connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Error as err:
            connection.rollback()
            logger.error(f"Batch execution error: {err}")
            raise
        finally:
            connection.close()
