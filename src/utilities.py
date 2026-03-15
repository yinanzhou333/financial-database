"""
Utility functions for financial analysis.
"""

import pandas as pd
import json
from tabulate import tabulate


def print_analysis_summary(report: dict, tickers: list):
    """
    Print a formatted summary of the analysis.
    
    Args:
        report: Analysis report dictionary
        tickers: List of ticker symbols
    """
    print("\n" + "=" * 80)
    print("FINANCIAL ANALYSIS SUMMARY")
    print("=" * 80)
    
    # Volatility Summary
    print("\n### VOLATILITY ANALYSIS ###\n")
    volatility_data = []
    for ticker in tickers:
        vol = report['individual_analysis'][ticker].get('volatility', {})
        if vol:
            volatility_data.append({
                'Ticker': ticker,
                'Daily Vol (%)': f"{vol.get('daily_volatility', 0)*100:.2f}",
                'Annual Vol (%)': f"{vol.get('annual_volatility', 0)*100:.2f}",
                'Current Vol (%)': f"{vol.get('current_rolling_volatility', 0)*100:.2f}"
            })
    
    if volatility_data:
        print(tabulate(volatility_data, headers='keys', tablefmt='grid'))
    
    # Sharpe Ratio Summary
    print("\n### SHARPE RATIO ANALYSIS ###\n")
    sharpe_data = []
    for ticker in tickers:
        sharpe = report['individual_analysis'][ticker].get('sharpe_ratio', {})
        if sharpe:
            sharpe_data.append({
                'Ticker': ticker,
                'Sharpe Ratio': f"{sharpe.get('sharpe_ratio', 0):.4f}",
                'Annual Return (%)': f"{sharpe.get('annual_return', 0)*100:.2f}",
                'Annual Vol (%)': f"{sharpe.get('annual_volatility', 0)*100:.2f}"
            })
    
    if sharpe_data:
        print(tabulate(sharpe_data, headers='keys', tablefmt='grid'))
    
    # Momentum Summary
    print("\n### MOMENTUM ANALYSIS ###\n")
    momentum_data = []
    for ticker in tickers:
        mom = report['individual_analysis'][ticker].get('momentum', {})
        if mom:
            momentum_data.append({
                'Ticker': ticker,
                '20D Momentum (%)': f"{mom.get('20d_momentum_pct', 0):.2f}",
                '50D Momentum (%)': f"{mom.get('50d_momentum_pct', 0):.2f}",
                '200D Momentum (%)': f"{mom.get('200d_momentum_pct', 0):.2f}"
            })
    
    if momentum_data:
        print(tabulate(momentum_data, headers='keys', tablefmt='grid'))
    
    # Moving Averages Summary
    print("\n### MOVING AVERAGES & PRICE LEVELS ###\n")
    ma_data = []
    for ticker in tickers:
        ma = report['individual_analysis'][ticker].get('moving_averages', {})
        if ma:
            ma_data.append({
                'Ticker': ticker,
                'Current Price': f"${ma.get('current_price', 0):.2f}",
                'vs MA20 (%)': f"{ma.get('price_vs_ma20_pct', 0):.2f}",
                'vs MA50 (%)': f"{ma.get('price_vs_ma50_pct', 0):.2f}",
                'vs MA200 (%)': f"{ma.get('price_vs_ma200_pct', 0):.2f}"
            })
    
    if ma_data:
        print(tabulate(ma_data, headers='keys', tablefmt='grid'))
    
    # RSI Summary
    print("\n### RELATIVE STRENGTH INDEX (RSI) ###\n")
    rsi_data = []
    for ticker in tickers:
        rsi = report['individual_analysis'][ticker].get('rsi', {})
        if rsi:
            rsi_data.append({
                'Ticker': ticker,
                'RSI (14)': f"{rsi.get('rsi', 0):.2f}",
                'Signal': rsi.get('signal', 'N/A')
            })
    
    if rsi_data:
        print(tabulate(rsi_data, headers='keys', tablefmt='grid'))
    
    # Correlation Matrix
    print("\n### CORRELATION MATRIX ###\n")
    corr_matrix = report['portfolio_analysis'].get('correlation_matrix', {})
    if corr_matrix and 'correlation_matrix' in corr_matrix:
        corr_df = pd.DataFrame(corr_matrix['correlation_matrix'])
        print(corr_df.round(4))
    
    print("\n" + "=" * 80)


def export_to_csv(data: list, filename: str):
    """
    Export data to CSV file.
    
    Args:
        data: List of dictionaries
        filename: Output filename
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data exported to {filename}")


def export_to_excel(data: dict, filename: str):
    """
    Export data to Excel file with multiple sheets.
    
    Args:
        data: Dictionary with sheet names as keys and DataFrames as values
        filename: Output filename
    """
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for sheet_name, df in data.items():
                if isinstance(df, dict):
                    df = pd.DataFrame(df)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Data exported to {filename}")
    except ImportError:
        print("openpyxl not installed. Please install it to use Excel export.")


def create_performance_report(tickers: list, analysis: dict) -> str:
    """
    Create a formatted performance report.
    
    Args:
        tickers: List of ticker symbols
        analysis: Analysis dictionary
        
    Returns:
        Formatted report string
    """
    report = "PORTFOLIO PERFORMANCE REPORT\n"
    report += "=" * 60 + "\n\n"
    
    for ticker in tickers:
        ticker_analysis = analysis.get('individual_analysis', {}).get(ticker, {})
        
        report += f"### {ticker} ###\n"
        report += "-" * 30 + "\n"
        
        sharpe = ticker_analysis.get('sharpe_ratio', {})
        if sharpe:
            report += f"Sharpe Ratio: {sharpe.get('sharpe_ratio', 'N/A')}\n"
            report += f"Annual Return: {sharpe.get('annual_return', 0)*100:.2f}%\n"
            report += f"Annual Volatility: {sharpe.get('annual_volatility', 0)*100:.2f}%\n"
        
        report += "\n"
    
    return report


if __name__ == "__main__":
    # Example usage
    print("Utilities module loaded successfully")
