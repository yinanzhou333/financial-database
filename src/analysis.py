"""
Financial analysis module.
Performs sophisticated financial analysis on the data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
from src.db_config import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialAnalyzer:
    """Performs financial analysis on stock and market data."""
    
    def __init__(self, risk_free_rate: float = 0.05):
        """
        Initialize analyzer.
        
        Args:
            risk_free_rate: Risk-free rate for Sharpe ratio calculations
        """
        self.risk_free_rate = risk_free_rate
    
    def get_price_data(self, ticker: str, days: int = 252) -> pd.DataFrame:
        """
        Fetch price data for a ticker safely.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to fetch
            
        Returns:
            DataFrame with price_date and price columns
        """
        # Try to get adjusted_close, fallback to closing_price
        query = f"""
        SELECT price_date, 
               COALESCE(adjusted_close, closing_price) as price
        FROM stock_prices
        WHERE ticker = %s AND (adjusted_close IS NOT NULL OR closing_price IS NOT NULL)
        ORDER BY price_date DESC
        LIMIT {days}
        """
        
        results = DatabaseManager.execute_query(query, (ticker,))
        
        if not results:
            logger.warning(f"No price data found for {ticker}")
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        df['price_date'] = pd.to_datetime(df['price_date'])
        df = df.sort_values('price_date')
        df = df.dropna(subset=['price'])
        
        # Convert price to numeric, coercing errors to NaN
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])
        
        return df
    
    def calculate_returns(self, ticker: str, days: int = 252) -> pd.DataFrame:
        """
        Calculate daily and periodic returns for a stock.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to include
            
        Returns:
            DataFrame with returns
        """
        logger.info(f"Calculating returns for {ticker}...")
        
        df = self.get_price_data(ticker, days)
        
        if df.empty:
            return df
        
        # Calculate returns
        df['daily_return'] = df['price'].pct_change()
        
        # Calculate log returns safely
        with np.errstate(divide='ignore', invalid='ignore'):
            df['log_return'] = np.log(df['price'] / df['price'].shift(1))
            df['log_return'] = df['log_return'].replace([np.inf, -np.inf], np.nan)
        
        return df
    
    def calculate_volatility(self, ticker: str, window: int = 30) -> dict:
        """
        Calculate volatility metrics for a stock.
        
        Args:
            ticker: Stock ticker symbol
            window: Rolling window in days
            
        Returns:
            Dictionary with volatility metrics
        """
        logger.info(f"Calculating volatility for {ticker}...")
        
        returns = self.calculate_returns(ticker)
        
        if returns.empty:
            return {}
        
        daily_volatility = returns['daily_return'].std()
        annual_volatility = daily_volatility * np.sqrt(252)
        
        rolling_volatility = returns['daily_return'].rolling(window).std()
        current_volatility = rolling_volatility.iloc[-1]
        
        return {
            'ticker': ticker,
            'daily_volatility': float(daily_volatility),
            'annual_volatility': float(annual_volatility),
            'current_rolling_volatility': float(current_volatility),
            'calculation_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def calculate_correlation_matrix(self, tickers: list) -> dict:
        """
        Calculate correlation matrix between multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            Dictionary with correlation matrix
        """
        logger.info(f"Calculating correlation matrix for {len(tickers)} tickers...")
        
        returns_dict = {}
        
        for ticker in tickers:
            returns = self.calculate_returns(ticker)
            if not returns.empty:
                returns_dict[ticker] = returns.set_index('price_date')['daily_return']
        
        if not returns_dict:
            logger.warning("No return data available for correlation calculation")
            return {}
        
        df = pd.DataFrame(returns_dict)
        correlation_matrix = df.corr()
        
        return {
            'tickers': tickers,
            'correlation_matrix': correlation_matrix.to_dict(),
            'calculation_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def calculate_sharpe_ratio(self, ticker: str) -> dict:
        """
        Calculate Sharpe ratio for a stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with Sharpe ratio metrics
        """
        logger.info(f"Calculating Sharpe ratio for {ticker}...")
        
        returns = self.calculate_returns(ticker, days=252)
        
        if returns.empty:
            return {}
        
        excess_returns = returns['daily_return'] - (self.risk_free_rate / 252)
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
        
        return {
            'ticker': ticker,
            'sharpe_ratio': float(sharpe_ratio),
            'annual_return': float(returns['daily_return'].mean() * 252),
            'annual_volatility': float(returns['daily_return'].std() * np.sqrt(252)),
            'calculation_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def calculate_price_momentum(self, ticker: str, periods: list = [20, 50, 200]) -> dict:
        """
        Calculate price momentum over different periods.
        
        Args:
            ticker: Stock ticker symbol
            periods: List of periods (in days)
            
        Returns:
            Dictionary with momentum metrics
        """
        logger.info(f"Calculating momentum for {ticker}...")
        
        df = self.get_price_data(ticker, days=250)
        
        if df.empty:
            return {}
        
        momentum = {'ticker': ticker}
        
        for period in periods:
            if len(df) >= period:
                momentum_return = (df['price'].iloc[-1] / df['price'].iloc[-period] - 1) * 100
                momentum[f'{period}d_momentum_pct'] = float(momentum_return)
        
        momentum['calculation_date'] = datetime.now().strftime('%Y-%m-%d')
        
        return momentum
    
    def calculate_moving_averages(self, ticker: str) -> dict:
        """
        Calculate moving averages.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with moving average metrics
        """
        logger.info(f"Calculating moving averages for {ticker}...")
        
        df = self.get_price_data(ticker, days=250)
        
        if df.empty:
            return {}
        
        current_price = df['price'].iloc[-1]
        ma_20 = df['price'].tail(20).mean()
        ma_50 = df['price'].tail(50).mean()
        ma_200 = df['price'].tail(200).mean()
        
        return {
            'ticker': ticker,
            'current_price': float(current_price),
            'ma_20': float(ma_20),
            'ma_50': float(ma_50),
            'ma_200': float(ma_200),
            'price_vs_ma20_pct': float((current_price / ma_20 - 1) * 100),
            'price_vs_ma50_pct': float((current_price / ma_50 - 1) * 100),
            'price_vs_ma200_pct': float((current_price / ma_200 - 1) * 100),
            'calculation_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def calculate_rsi(self, ticker: str, period: int = 14) -> dict:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            ticker: Stock ticker symbol
            period: RSI period
            
        Returns:
            Dictionary with RSI metrics
        """
        logger.info(f"Calculating RSI for {ticker}...")
        
        df = self.get_price_data(ticker, days=100)
        
        if df.empty:
            return {}
        
        # Calculate price changes
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # Determine signal
        if current_rsi > 70:
            signal = 'Overbought'
        elif current_rsi < 30:
            signal = 'Oversold'
        else:
            signal = 'Neutral'
        
        return {
            'ticker': ticker,
            'rsi': float(current_rsi),
            'signal': signal,
            'period': period,
            'calculation_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def generate_comprehensive_report(self, tickers: list) -> dict:
        """
        Generate comprehensive analysis report for multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            Dictionary with complete analysis
        """
        logger.info(f"Generating comprehensive report for {len(tickers)} tickers...")
        
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'tickers': tickers,
            'individual_analysis': {},
            'portfolio_analysis': {}
        }
        
        # Individual analysis
        for ticker in tickers:
            report['individual_analysis'][ticker] = {
                'volatility': self.calculate_volatility(ticker),
                'sharpe_ratio': self.calculate_sharpe_ratio(ticker),
                'momentum': self.calculate_price_momentum(ticker),
                'moving_averages': self.calculate_moving_averages(ticker),
                'rsi': self.calculate_rsi(ticker)
            }
        
        # Portfolio analysis
        report['portfolio_analysis']['correlation_matrix'] = self.calculate_correlation_matrix(tickers)
        
        return report
    
    def save_analysis_to_db(self, tickers: list, report: dict):
        """
        Save analysis results to database.
        
        Args:
            tickers: List of ticker symbols
            report: Analysis report dictionary
        """
        logger.info("Saving analysis to database...")
        
        insert_query = """
        INSERT INTO market_analysis 
        (analysis_date, tickers, analysis_type, result)
        VALUES (%s, %s, %s, %s)
        """
        
        tickers_str = ','.join(tickers)
        result_json = json.dumps(report, default=str)
        
        try:
            DatabaseManager.execute_update(
                insert_query,
                (datetime.now().strftime('%Y-%m-%d'), tickers_str, 'comprehensive', result_json)
            )
            logger.info("Analysis saved successfully")
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    from src.db_config import DatabaseConfig
    
    # Initialize database
    config = DatabaseConfig()
    DatabaseManager.init_pool(config)
    
    # Run analysis
    analyzer = FinancialAnalyzer()
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    report = analyzer.generate_comprehensive_report(tickers)
    analyzer.save_analysis_to_db(tickers, report)
    
    print(json.dumps(report, indent=2, default=str))
