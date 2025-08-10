#!/usr/bin/env python3
"""
Simple Backtesting Example

This example demonstrates basic usage of the backtesting engine
with a simple moving average strategy.
"""

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Import the backtesting engine
try:
    import backtesting_engine as bt
except ImportError:
    print("Error: backtesting_engine module not found.")
    print("Please build and install the Python bindings first:")
    print("  cd python_bindings")
    print("  pip install .")
    sys.exit(1)

def generate_sample_data(n_days=100, initial_price=100.0, volatility=0.02):
    """
    Generate sample price data using geometric Brownian motion.
    
    Args:
        n_days (int): Number of days to simulate
        initial_price (float): Starting price
        volatility (float): Daily volatility
        
    Returns:
        pd.DataFrame: DataFrame with columns ['timestamp', 'price', 'volume']
    """
    np.random.seed(42)  # For reproducible results
    
    # Generate random price movements
    returns = np.random.normal(0.001, volatility, n_days)  # Slight positive drift
    prices = [initial_price]
    
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    
    # Generate timestamps (daily)
    start_timestamp = 1640995200  # Jan 1, 2022
    timestamps = [start_timestamp + i * 86400 for i in range(len(prices))]
    
    # Generate random volumes
    volumes = np.random.randint(1000, 10000, len(prices))
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'price': prices,
        'volume': volumes
    })

def run_simple_backtest():
    """Run a simple backtest with SMA strategy."""
    print("=== Simple Backtesting Example ===\n")
    
    # Generate sample data
    print("Generating sample market data...")
    data = generate_sample_data(n_days=50, initial_price=100.0)
    print(f"Generated {len(data)} data points")
    print(f"Price range: ${data['price'].min():.2f} - ${data['price'].max():.2f}\n")
    
    # Create backtesting engine
    print("Creating backtesting engine...")
    engine = bt.BacktestingEngine()
    
    # Create and add SMA strategy
    sma_window = 10
    print(f"Adding SMA strategy (window={sma_window})...")
    strategy = bt.SMAStrategy(sma_window)
    engine.add_strategy(strategy)
    
    # Add market data to engine
    print("Loading market data into engine...")
    symbol = "SAMPLE"
    
    for _, row in data.iterrows():
        engine.add_market_data(
            symbol, 
            row['price'], 
            int(row['timestamp']), 
            int(row['volume'])
        )
    
    # Run backtest
    print("\nRunning backtest...")
    print("-" * 50)
    start_time = time.time()
    
    engine.run()
    
    end_time = time.time()
    print("-" * 50)
    print(f"Backtest completed in {end_time - start_time:.3f} seconds\n")
    
    # Plot results
    plot_results(data)

def plot_results(data):
    """Plot the price data and moving average."""
    print("Plotting results...")
    
    # Calculate SMA for visualization
    sma_window = 10
    data['sma'] = data['price'].rolling(window=sma_window).mean()
    
    plt.figure(figsize=(12, 8))
    
    # Price and SMA
    plt.subplot(2, 1, 1)
    plt.plot(data.index, data['price'], label='Price', color='blue', alpha=0.7)
    plt.plot(data.index, data['sma'], label=f'SMA({sma_window})', color='red', alpha=0.8)
    plt.title('Price vs Simple Moving Average')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Volume
    plt.subplot(2, 1, 2)
    plt.bar(data.index, data['volume'], alpha=0.6, color='green')
    plt.title('Trading Volume')
    plt.xlabel('Days')
    plt.ylabel('Volume')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def demonstrate_event_types():
    """Demonstrate creating different event types."""
    print("\n=== Event Types Demo ===")
    
    # Create different types of events
    market_event = bt.create_market_event("AAPL", 150.50, 1640995200, 1000)
    signal_event = bt.create_signal_event("AAPL", bt.OrderDirection.BUY, 0.8, "SMA")
    
    print("Created events:")
    print(f"  Market: {market_event.to_string()}")
    print(f"  Signal: {signal_event.to_string()}")
    
    # Show enum values
    print(f"\nEnum values:")
    print(f"  Order directions: BUY={bt.OrderDirection.BUY}, SELL={bt.OrderDirection.SELL}")
    print(f"  Order types: MARKET={bt.OrderType.MARKET}, LIMIT={bt.OrderType.LIMIT}")
    print(f"  Event types: MARKET={bt.EventType.MARKET}, SIGNAL={bt.EventType.SIGNAL}")

if __name__ == "__main__":
    try:
        # Run the main example
        run_simple_backtest()
        
        # Show additional features
        demonstrate_event_types()
        
        print(f"\nBacktesting engine version: {bt.get_version()}")
        print("Example completed successfully!")
        
    except Exception as e:
        print(f"Error running example: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)