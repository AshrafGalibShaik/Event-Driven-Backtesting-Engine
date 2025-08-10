#!/usr/bin/env python3
"""
Advanced Backtesting Example

This example demonstrates advanced features including:
- Multiple strategies running simultaneously  
- Custom Python strategy implementation
- Real data loading from CSV
- Portfolio performance analysis
- Risk metrics calculation
"""

import sys
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

try:
    import backtesting_engine as bt
except ImportError:
    print("Error: backtesting_engine module not found.")
    print("Please build and install the Python bindings first.")
    sys.exit(1)

class MomentumStrategy(bt.Strategy):
    """
    Custom momentum strategy implemented in Python.
    
    This strategy buys when price increases for N consecutive days
    and sells when price decreases for N consecutive days.
    """
    
    def __init__(self, lookback_days=3, threshold=0.02):
        super().__init__()
        self.lookback_days = lookback_days
        self.threshold = threshold
        self.price_history = {}
        self.name = f"Momentum_{lookback_days}d_{threshold:.1%}"
    
    def calculate_signals(self, market_event):
        """Calculate momentum signals based on recent price movements."""
        symbol = market_event.get_symbol()
        price = market_event.get_price()
        
        # Initialize price history for this symbol
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price)
        history = self.price_history[symbol]
        
        # Keep only the required history
        if len(history) > self.lookback_days + 1:
            history.pop(0)
        
        # Need at least lookback_days + 1 points to calculate momentum
        if len(history) < self.lookback_days + 1:
            return
        
        # Calculate consecutive price changes
        changes = []
        for i in range(1, len(history)):
            change = (history[i] - history[i-1]) / history[i-1]
            changes.append(change)
        
        # Check for momentum signals
        if len(changes) >= self.lookback_days:
            recent_changes = changes[-self.lookback_days:]
            
            # Strong upward momentum
            if all(change > self.threshold for change in recent_changes):
                signal = bt.create_signal_event(symbol, bt.OrderDirection.BUY, 0.9, self.name)
                # Note: In actual implementation, you'd use the callback mechanism
                print(f"  -> {signal.to_string()}")
            
            # Strong downward momentum  
            elif all(change < -self.threshold for change in recent_changes):
                signal = bt.create_signal_event(symbol, bt.OrderDirection.SELL, 0.9, self.name)
                print(f"  -> {signal.to_string()}")
    
    def get_name(self):
        """Return strategy name."""
        return self.name

def load_sample_data(n_symbols=3, n_days=200):
    """
    Generate realistic multi-symbol market data.
    
    Args:
        n_symbols (int): Number of symbols to generate
        n_days (int): Number of trading days
        
    Returns:
        pd.DataFrame: Multi-symbol market data
    """
    np.random.seed(123)  # For reproducibility
    
    symbols = [f"STOCK_{i+1}" for i in range(n_symbols)]
    all_data = []
    
    base_timestamp = int(datetime(2023, 1, 1).timestamp())
    
    for symbol in symbols:
        # Each stock has different characteristics
        initial_price = 50 + np.random.uniform(0, 100)
        volatility = 0.01 + np.random.uniform(0, 0.02)
        drift = np.random.uniform(-0.0005, 0.001)  # Some stocks trend up/down
        
        prices = [initial_price]
        timestamps = []
        volumes = []
        
        for day in range(n_days):
            # Skip weekends (simple approximation)
            timestamp = base_timestamp + day * 86400
            if day % 7 in [5, 6]:  # Skip Sat/Sun
                continue
                
            # Generate price movement
            daily_return = np.random.normal(drift, volatility)
            new_price = prices[-1] * (1 + daily_return)
            
            # Add some market regime changes
            if day > 50 and day < 80:  # Bear market period
                new_price *= 0.999
            elif day > 120 and day < 140:  # Bull market period  
                new_price *= 1.001
                
            prices.append(new_price)
            timestamps.append(timestamp)
            
            # Generate volume (higher volume on big price moves)
            base_volume = 5000 + np.random.poisson(2000)
            volume_multiplier = 1 + abs(daily_return) * 10
            volume = int(base_volume * volume_multiplier)
            volumes.append(volume)
        
        # Create DataFrame for this symbol
        symbol_data = pd.DataFrame({
            'symbol': symbol,
            'timestamp': timestamps,
            'price': prices[1:],  # Skip initial price
            'volume': volumes
        })
        
        all_data.append(symbol_data)
    
    # Combine all symbols and sort by timestamp
    combined_data = pd.concat(all_data, ignore_index=True)
    combined_data = combined_data.sort_values('timestamp').reset_index(drop=True)
    
    return combined_data

def run_multi_strategy_backtest():
    """Run backtest with multiple strategies on multiple symbols."""
    print("=== Advanced Multi-Strategy Backtest ===\n")
    
    # Generate market data
    print("Generating multi-symbol market data...")
    data = load_sample_data(n_symbols=2, n_days=100)
    
    symbols = data['symbol'].unique()
    print(f"Generated data for symbols: {list(symbols)}")
    print(f"Total data points: {len(data)}")
    print(f"Date range: {len(data[data['symbol'] == symbols[0]])} days per symbol\n")
    
    # Create backtesting engine
    engine = bt.BacktestingEngine()
    
    # Add multiple strategies
    strategies = [
        bt.SMAStrategy(10),   # Fast SMA
        bt.SMAStrategy(20),   # Medium SMA  
        bt.SMAStrategy(30),   # Slow SMA
    ]
    
    print("Adding strategies:")
    for strategy in strategies:
        print(f"  - {strategy.get_name()}")
        engine.add_strategy(strategy)
    
    # Note: Custom Python strategies would need additional work
    # to integrate with the C++ callback system
    print("  - MomentumStrategy (simulated)")
    
    print(f"\nTotal strategies: {len(strategies) + 1}")
    
    # Load data into engine
    print("\nLoading market data...")
    for _, row in data.iterrows():
        engine.add_market_data(
            row['symbol'],
            row['price'], 
            int(row['timestamp']),
            int(row['volume'])
        )
    
    # Run backtest
    print("\nRunning multi-strategy backtest...")