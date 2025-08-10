#!/usr/bin/env python3
"""
Test Suite for Backtesting Engine Python Bindings

This file contains comprehensive tests for the Python bindings
to ensure all functionality works correctly.
"""

import pytest
import sys
import os
import tempfile
import numpy as np
import pandas as pd

# Import the backtesting engine
try:
    import backtesting_engine as bt
except ImportError:
    pytest.skip("backtesting_engine module not available", allow_module_level=True)

class TestEventCreation:
    """Test event creation and basic functionality."""
    
    def test_market_event_creation(self):
        """Test MarketEvent creation and getters."""
        symbol = "TEST"
        price = 100.50
        timestamp = 1640995200
        volume = 1000
        
        event = bt.create_market_event(symbol, price, timestamp, volume)
        
        assert event.get_symbol() == symbol
        assert event.get_price() == price
        assert event.get_timestamp() == timestamp
        assert event.get_volume() == volume
        assert event.get_type() == bt.EventType.MARKET
        assert "TEST" in event.to_string()
    
    def test_signal_event_creation(self):
        """Test SignalEvent creation and getters."""
        symbol = "TEST"
        direction = bt.OrderDirection.BUY
        strength = 0.8
        strategy_id = "SMA"
        
        event = bt.create_signal_event(symbol, direction, strength, strategy_id)
        
        assert event.get_symbol() == symbol
        assert event.get_direction() == direction
        assert event.get_strength() == strength
        assert event.get_strategy_id() == strategy_id
        assert event.get_type() == bt.EventType.SIGNAL

class TestEnums:
    """Test enum values and comparisons."""
    
    def test_event_types(self):
        """Test EventType enum values."""
        assert bt.EventType.MARKET != bt.EventType.SIGNAL
        assert bt.EventType.ORDER != bt.EventType.FILL
    
    def test_order_directions(self):
        """Test OrderDirection enum values."""
        assert bt.OrderDirection.BUY != bt.OrderDirection.SELL
        
    def test_order_types(self):
        """Test OrderType enum values."""
        assert bt.OrderType.MARKET != bt.OrderType.LIMIT
        assert bt.OrderType.LIMIT != bt.OrderType.STOP

class TestSMAStrategy:
    """Test the SMA strategy implementation."""
    
    def test_sma_strategy_creation(self):
        """Test SMA strategy creation with different window sizes."""
        strategy = bt.SMAStrategy(20)
        assert strategy.get_name() == "SMA_20"
        
        strategy_fast = bt.SMAStrategy(10)
        assert strategy_fast.get_name() == "SMA_10"
    
    def test_sma_strategy_signals(self):
        """Test that SMA strategy generates signals with enough data."""
        strategy = bt.SMAStrategy(5)  # Small window for testing
        
        # Create sample market events
        symbol = "TEST"
        base_timestamp = 1640995200
        
        # Price series that should generate signals
        prices = [100, 101, 102, 103, 104, 110, 112]  # Rising trend
        
        for i, price in enumerate(prices):
            timestamp = base_timestamp + i * 86400
            market_event = bt.create_market_event(symbol, price, timestamp)
            
            # This would generate signals in the real implementation
            # For now, just test that the method can be called
            strategy.calculate_signals(market_event)

class TestBacktestingEngine:
    """Test the main backtesting engine functionality."""
    
    def test_engine_creation(self):
        """Test basic engine creation."""
        engine = bt.BacktestingEngine()
        assert engine is not None
    
    def test_add_strategy(self):
        """Test adding strategies to the engine."""
        engine = bt.BacktestingEngine()
        strategy = bt.SMAStrategy(20)
        
        # This should not raise an exception
        engine.add_strategy(strategy)
    
    def test_add_market_data(self):
        """Test adding market data to the engine."""
        engine = bt.BacktestingEngine()
        
        # Add sample data points
        engine.add_market_data("TEST", 100.0, 1640995200, 1000)
        engine.add_market_data("TEST", 101.0, 1640995200 + 86400, 1200)
    
    def test_simple_backtest(self):
        """Test running a simple backtest."""
        engine = bt.BacktestingEngine()
        
        # Add strategy
        strategy = bt.SMAStrategy(5)
        engine.add_strategy(strategy)
        
        # Add sample data
        symbol = "TEST"
        base_timestamp = 1640995200
        prices = [100, 102, 99, 105, 103, 107, 101, 108]
        
        for i, price in enumerate(prices):
            timestamp = base_timestamp + i * 86400
            engine.add_market_data(symbol, price, timestamp, 1000)
        
        # Run backtest - should not raise exception
        engine.run()

class TestPosition:
    """Test position tracking functionality."""
    
    def test_position_creation(self):
        """Test position creation and basic methods."""
        symbol = "TEST"
        position = bt.Position(symbol)
        
        assert position.get_symbol() == symbol
        assert position.get_quantity() == 0
        assert position.get_avg_price() == 0.0
    
    def test_position_updates(self):
        """Test position updates with trades."""
        position = bt.Position("TEST")
        
        # First trade
        position.update_position(100, 50.0)
        assert position.get_quantity() == 100
        assert position.get_avg_price() == 50.0
        
        # Second trade at different price
        position.update_position(50, 60.0)
        expected_avg = (100 * 50.0 + 50 * 60.0) / 150
        assert position.get_quantity() == 150
        assert abs(position.get_avg_price() - expected_avg) < 0.01
        
        # Test market value calculation
        current_price = 55.0
        expected_value = 150 * current_price
        assert position.get_market_value(current_price) == expected_value

class TestDataIntegration:
    """Test integration with pandas and numpy."""
    
    def test_numpy_data_generation(self):
        """Test using numpy to generate market data."""
        np.random.seed(42)
        
        # Generate price series
        n_days = 50
        initial_price = 100.0
        returns = np.random.normal(0.001, 0.02, n_days)
        prices = [initial_price]
        
        for ret in returns:
            prices.append(prices[-1] * (1 + ret))
        
        # Test that we can feed this to the engine
        engine = bt.BacktestingEngine()
        strategy = bt.SMAStrategy(10)
        engine.add_strategy(strategy)
        
        base_timestamp = 1640995200
        for i, price in enumerate(prices):
            timestamp = base_timestamp + i * 86400
            engine.add_market_data("NUMPY_TEST", price, timestamp, 1000)
        
        # Should run without error
        engine.run()
    
    def test_pandas_data_handling(self):
        """Test using pandas DataFrame for data management."""
        # Create sample DataFrame
        n_days = 30
        dates = pd.date_range('2022-01-01', periods=n_days, freq='D')
        
        data = pd.DataFrame({
            'symbol': ['TEST'] * n_days,
            'date': dates,
            'price': 100 + np.random.randn(n_days).cumsum(),
            'volume': np.random.randint(1000, 5000, n_days)
        })
        
        # Convert dates to timestamps
        data['timestamp'] = data['date'].astype(int) // 10**9
        
        # Feed to engine
        engine = bt.BacktestingEngine()
        strategy = bt.SMAStrategy(10)
        engine.add_strategy(strategy)
        
        for _, row in data.iterrows():
            engine.add_market_data(
                row['symbol'],
                row['price'],
                int(row['timestamp']),
                int(row['volume'])
            )
        
        engine.run()

class TestUtilityFunctions:
    """Test utility functions and convenience methods."""
    
    def test_version_info(self):
        """Test version information."""
        version = bt.get_version()
        assert isinstance(version, str)
        assert len(version) > 0
    
    def test_convenience_functions(self):
        """Test convenience functions for creating objects."""
        # Test create_engine function
        engine = bt.create_engine(50000.0)  # Custom initial capital
        assert engine is not None
        
        # Test create_sma_strategy function
        strategy = bt.create_sma_strategy(15)
        assert strategy.get_name() == "SMA_15"

class TestPerformanceAndStress:
    """Performance and stress tests."""
    
    def test_large_dataset(self):
        """Test with larger dataset to check performance."""
        engine = bt.BacktestingEngine()
        strategy = bt.SMAStrategy(20)
        engine.add_strategy(strategy)
        
        # Generate larger dataset
        n_points = 1000
        base_timestamp = 1640995200
        
        for i in range(n_points):
            price = 100 + np.sin(i * 0.1) * 10 + np.random.randn() * 2
            timestamp = base_timestamp + i * 86400
            engine.add_market_data("STRESS_TEST", price, timestamp, 1000)
        
        import time
        start_time = time.time()
        engine.run()
        end_time = time.time()
        
        # Should complete in reasonable time (less than 5 seconds)
        assert end_time - start_time < 5.0
    
    @pytest.mark.benchmark
    def test_benchmark_back