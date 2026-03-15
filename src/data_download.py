"""
Data download module.
Downloads financial data from various sources (yfinance, Yahoo Finance, etc.)
and saves to CSV files for processing.
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataDownloader:
    """Handles downloading financial data from online sources."""
    
    def __init__(self, start_date: str = None, end_date: str = None, output_dir: str = 'data'):
        """
        Initialize the downloader.
        
        Args:
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            output_dir: Directory to save downloaded data
        """
        self.start_date = start_date or '2020-01-01'
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def download_stock_prices(self, tickers: list, progress: bool = True) -> pd.DataFrame:
        """
        Download historical stock prices for given tickers.
        
        Args:
            tickers: List of stock ticker symbols
            progress: Show progress bar
            
        Returns:
            DataFrame with stock prices
        """
        logger.info(f"Downloading stock prices for {len(tickers)} tickers...")
        
        data = yf.download(
            tickers,
            start=self.start_date,
            end=self.end_date,
            progress=progress,
            auto_adjust=False  # Keep original OHLC values
        )
        
        # Flatten multi-index for single ticker
        if isinstance(data.columns, pd.MultiIndex):
            data = data.stack()
            data.index.names = ['Date', 'Ticker']
            data = data.reset_index()
        else:
            data['Ticker'] = tickers[0] if len(tickers) == 1 else 'MULTI'
            data = data.reset_index()
        
        # Save to CSV
        csv_path = os.path.join(self.output_dir, 'stock_prices.csv')
        data.to_csv(csv_path, index=False)
        logger.info(f"Stock prices saved to {csv_path}")
        
        return data
    
    def download_company_info(self, tickers: list) -> pd.DataFrame:
        """
        Download company information for given tickers.
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            DataFrame with company info
        """
        logger.info(f"Downloading company information for {len(tickers)} tickers...")
        
        company_data = []
        for ticker in tickers:
            try:
                info = yf.Ticker(ticker).info
                company_data.append({
                    'ticker': ticker,
                    'company_name': info.get('longName', ''),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'country': info.get('country', ''),
                    'currency': info.get('currency', 'USD'),
                    'market_cap': info.get('marketCap', None),
                })
                logger.info(f"Downloaded info for {ticker}")
            except Exception as e:
                logger.warning(f"Could not download info for {ticker}: {e}")
        
        df = pd.DataFrame(company_data)
        
        # Save to CSV
        csv_path = os.path.join(self.output_dir, 'company_info.csv')
        df.to_csv(csv_path, index=False)
        logger.info(f"Company info saved to {csv_path}")
        
        return df
    
    def download_financials(self, tickers: list, frequency: str = 'quarterly') -> pd.DataFrame:
        """
        Download financial statements (Income Statement, Balance Sheet, Cash Flow).
        
        Args:
            tickers: List of stock ticker symbols
            frequency: 'quarterly' or 'yearly'
            
        Returns:
            DataFrame with financial data
        """
        logger.info(f"Downloading {frequency} financials for {len(tickers)} tickers...")
        
        all_financials = []
        
        for ticker in tickers:
            try:
                ticker_obj = yf.Ticker(ticker)
                
                # Income Statement
                if frequency == 'quarterly':
                    income_stmt = ticker_obj.quarterly_financials
                else:
                    income_stmt = ticker_obj.financials
                
                if income_stmt is not None and not income_stmt.empty:
                    income_stmt = income_stmt.T.reset_index()
                    income_stmt.columns.name = None
                    income_stmt.rename(columns={'index': 'Date'}, inplace=True)
                    income_stmt['Ticker'] = ticker
                    income_stmt['Statement_Type'] = 'Income'
                    all_financials.append(income_stmt)
                
                # Balance Sheet
                if frequency == 'quarterly':
                    balance_sheet = ticker_obj.quarterly_balance_sheet
                else:
                    balance_sheet = ticker_obj.balance_sheet
                
                if balance_sheet is not None and not balance_sheet.empty:
                    balance_sheet = balance_sheet.T.reset_index()
                    balance_sheet.columns.name = None
                    balance_sheet.rename(columns={'index': 'Date'}, inplace=True)
                    balance_sheet['Ticker'] = ticker
                    balance_sheet['Statement_Type'] = 'Balance Sheet'
                    all_financials.append(balance_sheet)
                
                # Cash Flow Statement
                if frequency == 'quarterly':
                    cash_flow = ticker_obj.quarterly_cashflow
                else:
                    cash_flow = ticker_obj.cashflow
                
                if cash_flow is not None and not cash_flow.empty:
                    cash_flow = cash_flow.T.reset_index()
                    cash_flow.columns.name = None
                    cash_flow.rename(columns={'index': 'Date'}, inplace=True)
                    cash_flow['Ticker'] = ticker
                    cash_flow['Statement_Type'] = 'Cash Flow'
                    all_financials.append(cash_flow)
                
                logger.info(f"Downloaded financials for {ticker}")
                
            except Exception as e:
                logger.warning(f"Could not download financials for {ticker}: {e}")
        
        if all_financials:
            df = pd.concat(all_financials, ignore_index=True)
            csv_path = os.path.join(self.output_dir, f'financials_{frequency}.csv')
            df.to_csv(csv_path, index=False)
            logger.info(f"Financials saved to {csv_path}")
            return df
        else:
            logger.warning("No financial data downloaded")
            return pd.DataFrame()
    
    def download_market_indices(self, indices: list = None) -> pd.DataFrame:
        """
        Download market indices data.
        
        Args:
            indices: List of index symbols (e.g., ['^GSPC', '^DJI', '^IXIC'])
            
        Returns:
            DataFrame with market indices
        """
        if indices is None:
            indices = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, Nasdaq
        
        logger.info(f"Downloading market indices: {indices}")
        
        indices_data = yf.download(
            indices,
            start=self.start_date,
            end=self.end_date,
            progress=True
        )
        
        # Flatten if needed
        if isinstance(indices_data.columns, pd.MultiIndex):
            indices_data = indices_data.stack()
            indices_data.index.names = ['Date', 'Index']
            indices_data = indices_data.reset_index()
        else:
            indices_data = indices_data.reset_index()
            indices_data['Index'] = indices[0] if len(indices) == 1 else 'MULTI'
        
        # Save to CSV
        csv_path = os.path.join(self.output_dir, 'market_indices.csv')
        indices_data.to_csv(csv_path, index=False)
        logger.info(f"Market indices saved to {csv_path}")
        
        return indices_data


def download_all_data(tickers: list, start_date: str = None, end_date: str = None):
    """
    Download all financial data for analysis.
    
    Args:
        tickers: List of stock tickers to download
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
    """
    downloader = DataDownloader(start_date=start_date, end_date=end_date)
    
    # Download all data types
    downloader.download_company_info(tickers)
    downloader.download_stock_prices(tickers)
    downloader.download_financials(tickers, frequency='quarterly')
    downloader.download_market_indices()
    
    logger.info("All data downloaded successfully!")


if __name__ == "__main__":
    # Example usage
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    download_all_data(tickers)
