#!/usr/bin/env python3
"""
Create visualizations from the financial database.
Run this after loading data into MySQL.
"""

import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import sys

# Set style for professional-looking charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# MySQL Configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yourpassword',  # Update with your MySQL password
    'database': 'financial_analysis_db'
}

def connect_db():
    """Connect to MySQL database."""
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        print("Make sure MySQL is running and credentials in config are correct.")
        sys.exit(1)

def create_visualizations():
    """Create visualizations."""
    conn = connect_db()
    
    # Create output directory
    os.makedirs('visuals', exist_ok=True)
    
    print("📊 Creating visualizations...\n")
    
    # ============ Chart 1: Stock Performance Comparison ============
    print("Creating Chart 1: Stock Performance...")
    try:
        query = """
        SELECT 
            ticker,
            DATE_FORMAT(MIN(price_date), '%Y-%m-%d') as period_start,
            ROUND((MAX(closing_price) - MIN(closing_price)) / MIN(closing_price) * 100, 2) as total_return_pct
        FROM stock_prices
        GROUP BY ticker
        ORDER BY total_return_pct DESC
        """
        
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print("⚠️  No stock price data found. Run step3_load_database.py first.")
            conn.close()
            return
        
        plt.figure(figsize=(12, 6))
        colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in df['total_return_pct']]
        bars = plt.barh(df['ticker'], df['total_return_pct'], color=colors, edgecolor='black', linewidth=1.5)
        plt.xlabel('Total Return (%)', fontsize=12, fontweight='bold')
        plt.title('📈 Stock Performance: Total Return\n2022-2024 Period', fontsize=14, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        
        for i, v in enumerate(df['total_return_pct']):
            plt.text(v + 2, i, f'{v}%', va='center', fontweight='bold', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('visuals/01_stock_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✅ Saved: 01_stock_performance.png")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # ============ Chart 2: Volatility vs Return ============
    print("Creating Chart 2: Risk vs Return...")
    try:
        query = """
        SELECT 
            ticker,
            ROUND(STDDEV(closing_price) / AVG(closing_price) * 100, 2) as volatility_pct,
            ROUND((MAX(closing_price) - MIN(closing_price)) / MIN(closing_price) * 100, 2) as total_return_pct
        FROM stock_prices
        GROUP BY ticker
        """
        
        df = pd.read_sql(query, conn)
        
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(df['volatility_pct'], df['total_return_pct'], 
                            s=400, alpha=0.6, c=range(len(df)), cmap='viridis', 
                            edgecolors='black', linewidth=2)
        
        for i, ticker in enumerate(df['ticker']):
            plt.annotate(ticker, 
                        (df['volatility_pct'].iloc[i], df['total_return_pct'].iloc[i]), 
                        fontsize=12, fontweight='bold', ha='center', va='center')
        
        plt.xlabel('Volatility (%)', fontsize=12, fontweight='bold')
        plt.ylabel('Total Return (%)', fontsize=12, fontweight='bold')
        plt.title('📊 Risk vs Return Analysis\nHigher Right = Better Risk/Reward Ratio', 
                 fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('visuals/02_risk_vs_return.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✅ Saved: 02_risk_vs_return.png")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # ============ Chart 3: Price Trends Over Time ============
    print("Creating Chart 3: Price Trends...")
    try:
        query = """
        SELECT 
            ticker,
            DATE_FORMAT(price_date, '%Y-%m') as month,
            ROUND(AVG(closing_price), 2) as avg_price
        FROM stock_prices
        GROUP BY ticker, DATE_FORMAT(price_date, '%Y-%m')
        ORDER BY ticker, month
        """
        
        df = pd.read_sql(query, conn)
        
        plt.figure(figsize=(14, 7))
        for ticker in sorted(df['ticker'].unique()):
            ticker_data = df[df['ticker'] == ticker].reset_index(drop=True)
            plt.plot(range(len(ticker_data)), ticker_data['avg_price'], 
                    marker='o', label=ticker, linewidth=2.5, markersize=6)
        
        plt.xlabel('Timeline (Months)', fontsize=12, fontweight='bold')
        plt.ylabel('Average Price ($)', fontsize=12, fontweight='bold')
        plt.title('📈 Monthly Price Trends Analysis\n2022-2024', fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=11, framealpha=0.9)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('visuals/03_price_trends.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✅ Saved: 03_price_trends.png")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # ============ Chart 4: Trading Volume ============
    print("Creating Chart 4: Trading Volume...")
    try:
        query = """
        SELECT 
            ticker,
            ROUND(SUM(volume) / 1000000, 0) as total_volume_millions,
            ROUND(AVG(volume) / 1000000, 2) as avg_daily_volume_millions
        FROM stock_prices
        GROUP BY ticker
        ORDER BY total_volume_millions DESC
        """
        
        df = pd.read_sql(query, conn)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        bars1 = ax1.bar(df['ticker'], df['total_volume_millions'], 
                       color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('Total Volume (Millions)', fontsize=11, fontweight='bold')
        ax1.set_title('Total Trading Volume', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(df['total_volume_millions']):
            ax1.text(i, v + 5, f'{int(v)}M', ha='center', fontweight='bold')
        
        bars2 = ax2.bar(df['ticker'], df['avg_daily_volume_millions'], 
                       color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax2.set_ylabel('Avg Daily Volume (Millions)', fontsize=11, fontweight='bold')
        ax2.set_title('Average Daily Trading Volume', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(df['avg_daily_volume_millions']):
            ax2.text(i, v + 0.5, f'{v}M', ha='center', fontweight='bold')
        
        fig.suptitle('💰 Trading Volume & Liquidity Analysis', 
                    fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig('visuals/04_trading_volume.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✅ Saved: 04_trading_volume.png")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # ============ Chart 5: Monthly Returns Heatmap ============
    print("Creating Chart 5: Monthly Returns Heatmap...")
    try:
        query = """
        SELECT 
            ticker,
            DATE_FORMAT(price_date, '%Y-%m') as month,
            ROUND((MAX(closing_price) - MIN(closing_price)) / MIN(closing_price) * 100, 2) as monthly_return_pct
        FROM stock_prices
        GROUP BY ticker, DATE_FORMAT(price_date, '%Y-%m')
        ORDER BY ticker, month
        """
        
        df = pd.read_sql(query, conn)
        pivot_df = df.pivot(index='ticker', columns='month', values='monthly_return_pct')
        
        plt.figure(figsize=(16, 6))
        sns.heatmap(pivot_df, annot=True, fmt='.1f', cmap='RdYlGn', center=0, 
                   cbar_kws={'label': 'Monthly Return (%)'}, linewidths=0.5)
        plt.title('🔥 Monthly Returns Heatmap\nGreen = Profit | Red = Loss', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Month', fontsize=12, fontweight='bold')
        plt.ylabel('Stock Ticker', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('visuals/05_monthly_returns_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✅ Saved: 05_monthly_returns_heatmap.png")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    conn.close()
    
    print("\n" + "="*50)
    print("✅ All visualizations created successfully!")
    print("="*50)
    print("\n📁 Files saved to: visuals/")
    print("   1. 01_stock_performance.png")
    print("   2. 02_risk_vs_return.png")
    print("   3. 03_price_trends.png")
    print("   4. 04_trading_volume.png")
    print("   5. 05_monthly_returns_heatmap.png")

if __name__ == '__main__':
    create_visualizations()
