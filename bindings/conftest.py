"""
Pytest configuration file for backtesting engine tests.

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
import os

# Try to import the backtesting engine
try:
    import backtesting_engine as bt
    BACKTESTING_ENGINE_AVAILABLE = True
except ImportError:
    BACKTESTING_ENGINE_AVAILABLE = False
    bt = None

# Skip all tests if backtesting engine is not available
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "benchmark: mark test as a benchmark test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip tests if engine not available."""
    if not BACKTESTING_ENGINE_AVAILABLE:
        skip_engine = pytest.mark.skip(reason="backtesting_engine not available")
        for item in items:
            item.add_marker(skip_engine)

@pytest.fixture(scope="session")
def engine_available():
    """Session-scoped fixture indicating if engine is available."""
    return BACKTESTING_ENGINE_AVAILABLE

@pytest.fixture
def clean_engine():
    """Provide a clean backtesting engine for each test."""
    if not BACKTESTING_ENGINE_AVAILABLE:
        pytest.skip("backtesting_engine not available")
    
    engine = bt.BacktestingEngine()
    return engine

@pytest.fixture
def sma_strategy():
    """Provide a standard SMA strategy."""
    if not BACKTESTING_ENGINE_AVAILABLE:
        pytest.skip("backtesting_engine not available")
    
    return bt.SMAStrategy(20)

@pytest.fixture
def sample_price_data():
    """Generate sample price data for testing."""
    np.random.seed(42)  # For reproducible tests
    
    n_days = 50
    initial_price = 100.0
    volatility = 0.02
    
    # Generate price series using geometric Brownian motion
    returns = np.random.normal(0.001, volatility, n_days)
    prices = [initial_price]
    
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    
    return prices

@pytest.fixture
def sample_market_data():
    """Generate complete market data with timestamps and volumes."""
    np.random.seed(42)
    
    n_days = 30
    base_timestamp = 1640995200  # Jan 1, 2022
    initial_price = 100.0
    
    data = []
    price = initial_price
    
    for i in range(n_days):
        # Generate realistic price movement
        daily_return = np.random.normal(0.0005, 0.02)
        price *= (1 + daily_return)
        
        # Generate volume (higher volume on bigger moves)
        volume = int(1000 + abs(daily_return) * 50000 + np.random.poisson(500))
        
        data.append({
            'symbol': 'TEST',
            'timestamp': base_timestamp + i * 86400,
            'price': price,
            'volume': volume
        })
    
    return data

@pytest.fixture
def multi_symbol_data():
    """Generate market data for multiple symbols."""
    np.random.seed(123)
    
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    all_data = []
    base_timestamp = 1640995200
    
    for symbol in symbols:
        initial_price = 50 + np.random.uniform(50, 200)
        price = initial_price
        
        for day in range(20):
            daily_return = np.random.normal(0.001, 0.025)
            price *= (1 + daily_return)
            volume = np.random.randint(1000, 10000)
            
            all_data.append({
                'symbol': symbol,
                'timestamp': base_timestamp + day * 86400,
                'price': price,
                'volume': volume
            })
    
    # Sort by timestamp to simulate realistic data feed
    return sorted(all_data, key=lambda x: x['timestamp'])

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file with sample data."""
    csv_content = """symbol,timestamp,price,volume
AAPL,1640995200,150.50,12500
AAPL,1641081600,151.20,11200
AAPL,1641168000,149.80,13100
MSFT,1640995200,330.25,8500
MSFT,1641081600,332.10,9100
MSFT,1641168000,328.75,9800
GOOGL,1640995200,2750.80,3200
GOOGL,1641081600,2765.40,2950
GOOGL,1641168000,2742.15,3100"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_filename = f.name
    
    yield temp_filename
    
    # Cleanup
    try:
        os.unlink(temp_filename)
    except OSError:
        pass

@pytest.fixture
def configured_engine():
    """Provide a fully configured engine with strategy and data."""
    if not BACKTESTING_ENGINE_AVAILABLE:
        pytest.skip("backtesting_engine not available")
    
    engine = bt.BacktestingEngine()
    
    # Add SMA strategy
    strategy = bt.SMAStrategy(10)
    engine.add_strategy(strategy)
    
    # Add sample data
    sample_data = [
        {'symbol': 'TEST', 'price': 100.0, 'timestamp': 1640995200, 'volume': 1000},
        {'symbol': 'TEST', 'price': 102.0, 'timestamp': 1641081600, 'volume': 1200},
        {'symbol': 'TEST', 'price': 98.5, 'timestamp': 1641168000, 'volume': 800},
        {'symbol': 'TEST', 'price': 105.2, 'timestamp': 1641254400, 'volume': 1500},
        {'symbol': 'TEST', 'price': 103.8, 'timestamp': 1641340800, 'volume': 1100},
    ]
    
    for data_point in sample_data:
        engine.add_market_data(
            data_point['symbol'],
            data_point['price'],
            data_point['timestamp'],
            data_point['volume']
        )
    
    return engine

# Benchmark configuration
@pytest.fixture
def benchmark_config():
    """Configuration for benchmark tests."""
    return {
        'iterations': 5,
        'min_rounds': 3,
        'max_time': 10.0,
        'warmup': True
    }

# Custom assertions and utilities
def assert_valid_market_event(event):
    """Assert that an event is a valid MarketEvent."""
    assert hasattr(event, 'get_symbol')
    assert hasattr(event, 'get_price')
    assert hasattr(event, 'get_timestamp')
    assert hasattr(event, 'get_volume')
    assert event.get_price() > 0
    assert event.get_volume() >= 0
    assert len(event.get_symbol()) > 0

def assert_valid_signal_event(event):
    """Assert that an event is a valid SignalEvent."""
    assert hasattr(event, 'get_symbol')
    assert hasattr(event, 'get_direction')
    assert hasattr(event, 'get_strength')
    assert event.get_strength() >= 0
    assert event.get_strength() <= 1
    assert len(event.get_symbol()) > 0

# Add utility functions to pytest namespace
pytest.assert_valid_market_event = assert_valid_market_event
pytest.assert_valid_signal_event = assert_valid_signal_event