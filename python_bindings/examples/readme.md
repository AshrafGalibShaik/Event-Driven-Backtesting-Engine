# Python Bindings for Event-Driven Backtesting Engine

High-performance C++ backtesting engine with easy-to-use Python bindings. Combine the speed of C++ with the convenience and rich ecosystem of Python for quantitative trading strategy development.

## Quick Start

### Prerequisites

- Python 3.6 or later
- C++ compiler supporting C++14 (GCC 5.0+, Clang 3.8+, MSVC 2015+)
- CMake (optional, for advanced builds)

### Installation

#### Option 1: Install from source (recommended)

```bash
# Clone the repository (if not already done)
git clone https://github.com/yourusername/backtesting-engine.git
cd backtesting-engine/python_bindings

# Install dependencies
pip install -r requirements.txt

# Build and install the package
pip install .
```

#### Option 2: Development installation

```bash
cd python_bindings
pip install -e .  # Editable installation for development
```

### Verify Installation

```python
import backtesting_engine as bt
print(f"Backtesting Engine version: {bt.get_version()}")
```

## Basic Usage

### Simple Example

```python
import backtesting_engine as bt
import numpy as np

# Create backtesting engine
engine = bt.BacktestingEngine()

# Add a Simple Moving Average strategy
strategy = bt.SMAStrategy(window_size=20)
engine.add_strategy(strategy)

# Add some market data
symbol = "AAPL"
base_timestamp = 1640995200  # Jan 1, 2022

for i, price in enumerate([100, 102, 98, 105, 103, 107]):
    timestamp = base_timestamp + i * 86400  # Daily data
    engine.add_market_data(symbol, price, timestamp, volume=1000)

# Run the backtest
engine.run()
```

### Working with Real Data

```python
import pandas as pd
import backtesting_engine as bt

# Load your data
df = pd.read_csv('your_data.csv')  # columns: symbol, timestamp, price, volume

# Create and configure engine
engine = bt.BacktestingEngine()
engine.add_strategy(bt.SMAStrategy(10))  # Fast SMA
engine.add_strategy(bt.SMAStrategy(30))  # Slow SMA

# Feed data to engine
for _, row in df.iterrows():
    engine.add_market_data(
        row['symbol'], 
        row['price'], 
        int(row['timestamp']), 
        int(row['volume'])
    )

# Run backtest
engine.run()
```

## Examples

The `examples/` directory contains comprehensive examples:

### Run Simple Example
```bash
python examples/simple_backtest.py
```

Features demonstrated:
- Basic engine setup
- SMA strategy usage
- Sample data generation
- Result visualization

### Run Advanced Example
```bash
python examples/advanced_example.py [optional_csv_file.csv]
```

Features demonstrated:
- Multiple strategies simultaneously
- Multi-symbol backtesting
- Custom Python strategy development
- Performance analysis and risk metrics
- CSV data loading
- Comprehensive visualizations

## API Reference

### Core Classes

#### BacktestingEngine
Main engine for running backtests.

```python
engine = bt.BacktestingEngine()
engine.add_strategy(strategy)                    # Add a strategy
engine.add_market_data(symbol, price, timestamp, volume=0)  # Add market data
engine.run()                                     # Run the backtest
```

#### Strategies

**SMAStrategy** - Simple Moving Average
```python
strategy = bt.SMAStrategy(window_size=20)
print(strategy.get_name())  # Returns "SMA_20"
```

**Custom Strategy** - Inherit from Strategy base class
```python
class MyStrategy(bt.Strategy):
    def calculate_signals(self, market_event):
        symbol = market_event.get_symbol()
        price = market_event.get_price()
        # Your strategy logic here
        
    def get_name(self):
        return "MyCustomStrategy"
```

### Event Types

#### MarketEvent
```python
event = bt.create_market_event("AAPL", 150.0, timestamp, volume=1000)
print(event.get_symbol())     # "AAPL"
print(event.get_price())      # 150.0
print(event.get_timestamp())  # timestamp
print(event.get_volume())     # 1000
```

#### SignalEvent
```python
signal = bt.create_signal_event("AAPL", bt.OrderDirection.BUY, strength=0.8)
print(signal.get_direction())  # OrderDirection.BUY
print(signal.get_strength())   # 0.8
```

### Enums

```python
# Order directions
bt.OrderDirection.BUY
bt.OrderDirection.SELL

# Order types  
bt.OrderType.MARKET
bt.OrderType.LIMIT
bt.OrderType.STOP

# Event types
bt.EventType.MARKET
bt.EventType.SIGNAL
bt.EventType.ORDER
bt.EventType.FILL
```

## Data Format

### Expected CSV Format

Your CSV files should have these columns:

```csv
symbol,timestamp,price,volume
AAPL,1640995200,150.50,12500
AAPL,1641081600,151.20,11200
MSFT,1640995200,330.25,8500
MSFT,1641081600,332.10,9100
```

- **symbol**: Stock/asset symbol (string)
- **timestamp**: Unix timestamp (integer)
- **price**: Asset price (float)
- **volume**: Trading volume (integer)

### Timestamp Handling

Timestamps should be Unix timestamps (seconds since epoch):

```python
from datetime import datetime

# Convert datetime to timestamp
dt = datetime(2022, 1, 1, 9, 30, 0)  # Market open
timestamp = int(dt.timestamp())

# Or use existing timestamp
timestamp = 1640995200  # Jan 1, 2022
```

## Performance Optimization

### Best Practices

1. **Batch Data Loading**: Load all data before calling `run()` for best performance
2. **Strategy Efficiency**: Keep strategy calculations lightweight
3. **Memory Management**: The engine automatically manages memory for events

### Benchmarking

```python
import time
import backtesting_engine as bt

# Time your backtest
start_time = time.time()
engine.run()
end_time = time.time()

print(f"Backtest completed in {end_time - start_time:.3f} seconds")
```

## Integration with Python Ecosystem

### Pandas Integration

```python
import pandas as pd
import backtesting_engine as bt

# Load data with pandas
df = pd.read_csv('data.csv', parse_dates=['date'])
df['timestamp'] = df['date'].astype(int) // 10**9

# Use pandas for data analysis
returns = df.groupby('symbol')['price'].pct_change()
volatility = returns.groupby('symbol').std()
```

### Visualization with Matplotlib

```python
import matplotlib.pyplot as plt

# Plot results
plt.figure(figsize=(12, 6))
plt.plot(timestamps, prices, label='Price')
plt.plot(timestamps, sma_values, label='SMA(20)')
plt.legend()
plt.show()
```

### NumPy for Mathematical Operations

```python
import numpy as np

# Generate synthetic data
prices = 100 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 252)))
timestamps = np.arange(1640995200, 1640995200 + 252 * 86400, 86400)
```

## Troubleshooting

### Common Issues

**Import Error**: `ImportError: No module named 'backtesting_engine'`
```bash
# Make sure you installed the package
pip install .

# Or check if it's in development mode
pip install -e .
```

**Compilation Error**: Missing C++ compiler
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS (install Xcode command line tools)
xcode-select --install

# Windows (install Visual Studio Build Tools)
```

**Performance Issues**: Slow backtests
- Ensure you're using the C++ engine, not pure Python implementations
- Batch load all data before calling `run()`
- Profile your custom strategies for bottlenecks

### Getting Help

1. Check the main project README for C++ engine details
2. Look at example files for usage patterns
3. Open an issue on GitHub for bugs or feature requests

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/yourusername/backtesting-engine.git
cd backtesting-engine

# Install development dependencies  
pip install -r python_bindings/requirements.txt

# Build in development mode
cd python_bindings
pip install -e .
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-benchmark

# Run tests
pytest tests/

# Run benchmarks
pytest tests/ --benchmark-only
```

### Adding Custom Strategies

Create a new Python strategy:

```python
import backtesting_engine as bt

class RSIStrategy(bt.Strategy):
    def __init__(self, period=14, overbought=70, oversold=30):
        super().__init__()
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.price_history = {}
        
    def calculate_signals(self, market_event):
        # Implement RSI calculation and signal generation
        symbol = market_event.get_symbol()
        price = market_event.get_price()
        
        # Your RSI logic here
        rsi = self.calculate_rsi(symbol, price)
        
        if rsi > self.overbought:
            # Generate sell signal
            pass
        elif rsi < self.oversold:
            # Generate buy signal  
            pass
    
    def get_name(self):
        return f"RSI_{self.period}_{self.overbought}_{self.oversold}"
```

## License

This Python binding is released under the same license as the main project (MIT License).

## Contributing

Contributions are welcome! Areas where help is needed:

- Additional built-in strategies
- Performance optimizations
- Better error handling
- More comprehensive examples
- Documentation improvements

Please see the main project README for contribution guidelines.