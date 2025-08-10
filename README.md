# Event-Driven Backtesting Engine

A comprehensive C++ implementation of an event-driven backtesting system for algorithmic trading strategies. This engine provides a realistic simulation environment that closely mimics the behavior of live trading systems through proper event sequencing and modular component architecture.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Creating Custom Strategies](#creating-custom-strategies)
- [Configuration](#configuration)
- [Examples](#examples)
- [Performance Considerations](#performance-considerations)
- [Contributing](#contributing)

## Features

- **Event-Driven Architecture**: Proper event sequencing that mirrors real trading systems
- **Modular Design**: Easy integration of custom strategies, execution handlers, and data sources
- **Realistic Simulation**: Includes slippage, commissions, and market impact modeling
- **Position Management**: Comprehensive position tracking with average cost basis
- **Multiple Strategy Support**: Run multiple strategies simultaneously
- **Extensible Framework**: Clean interfaces for adding new components
- **Performance Tracking**: Portfolio value and position monitoring

## Architecture

The system follows a clean event-driven architecture with four main event types:

```
Market Data → Strategy → Portfolio → Execution → Fill
     ↓           ↓          ↓           ↓        ↓
MarketEvent → SignalEvent → OrderEvent → ExecutionHandler → FillEvent
```

### Event Flow

1. **MarketEvent**: New market data arrives (price, volume, timestamp)
2. **SignalEvent**: Strategy generates buy/sell signals
3. **OrderEvent**: Portfolio converts signals to orders
4. **FillEvent**: Execution handler simulates order fills

## Quick Start

### Compilation

```bash
g++ -std=c++14 -O2 -o backtester backtesting_engine.cpp
```

### Basic Usage

```cpp
#include "backtesting_engine.hpp"

int main() {
    // Create engine
    BacktestingEngine engine;
    
    // Add strategy
    auto strategy = std::make_unique<SMAStrategy>(20);
    engine.addStrategy(std::move(strategy));
    
    // Add market data
    engine.addMarketData("AAPL", 150.0, timestamp, 1000);
    
    // Run backtest
    engine.run();
    
    return 0;
}
```

## Core Components

### 1. Event System

All events inherit from the base `Event` class:

- **MarketEvent**: Market data updates
- **SignalEvent**: Trading signals from strategies  
- **OrderEvent**: Orders to be executed
- **FillEvent**: Completed order executions

### 2. Strategy Interface

```cpp
class Strategy {
public:
    virtual void calculateSignals(const MarketEvent& market_event) = 0;
    virtual std::string getName() const = 0;
};
```

### 3. Portfolio Management

- Position tracking with average cost basis
- Capital allocation and risk management
- Signal-to-order conversion
- Real-time portfolio valuation

### 4. Execution Handler

- Order execution simulation
- Slippage modeling (configurable)
- Commission calculation
- Market impact simulation

### 5. Backtesting Engine

- Event queue management
- Component coordination
- Event processing and routing
- Performance tracking

## Creating Custom Strategies

### Step 1: Inherit from Strategy

```cpp
class MyCustomStrategy : public Strategy {
public:
    void calculateSignals(const MarketEvent& market_event) override {
        // Your strategy logic here
        std::string symbol = market_event.getSymbol();
        double price = market_event.getPrice();
        
        // Generate signals based on your logic
        if (shouldBuy(symbol, price)) {
            auto signal = std::make_shared<SignalEvent>(
                symbol, OrderDirection::BUY, 1.0, "MyStrategy"
            );
            if (signal_callback_) signal_callback_(signal);
        }
    }
    
    std::string getName() const override { 
        return "MyCustomStrategy"; 
    }
    
private:
    bool shouldBuy(const std::string& symbol, double price) {
        // Your buy logic
        return false;
    }
};
```

### Step 2: Register with Engine

```cpp
auto my_strategy = std::make_unique<MyCustomStrategy>();
engine.addStrategy(std::move(my_strategy));
```

## Configuration

### Portfolio Settings

```cpp
Portfolio portfolio(initial_capital);  // Default: $100,000
```

### Execution Parameters

The execution handler can be configured for:
- **Slippage**: Default 0.1% for market orders
- **Commission**: $1 base + 0.1% of trade value
- **Market Impact**: Configurable based on order size

### Strategy Parameters

Each strategy can be customized with its own parameters:

```cpp
SMAStrategy sma_fast(10);   // 10-period moving average
SMAStrategy sma_slow(50);   // 50-period moving average
```

## Examples

### Simple Moving Average Strategy

```cpp
BacktestingEngine engine;

// Add SMA crossover strategy
auto sma_strategy = std::make_unique<SMAStrategy>(20);
engine.addStrategy(std::move(sma_strategy));

// Load historical data
std::vector<double> prices = {100, 101, 99, 102, 105, 103};
int64_t timestamp = 1640995200;

for (size_t i = 0; i < prices.size(); ++i) {
    engine.addMarketData("AAPL", prices[i], timestamp + i * 86400);
}

engine.run();
```

### Multiple Strategies

```cpp
BacktestingEngine engine;

// Add multiple strategies
engine.addStrategy(std::make_unique<SMAStrategy>(10));
engine.addStrategy(std::make_unique<SMAStrategy>(30));
engine.addStrategy(std::make_unique<MyCustomStrategy>());

// Strategies will run simultaneously
engine.run();
```

### Custom Data Source

```cpp
// Read from CSV, database, or API
void loadMarketData(BacktestingEngine& engine, const std::string& filename) {
    // Your data loading logic
    // Call engine.addMarketData() for each data point
}
```

## Performance Considerations

### Memory Management

- Uses smart pointers for automatic memory management
- Event objects are efficiently managed through shared_ptr
- Minimal memory footprint for large datasets

### Processing Speed

- Event queue provides O(1) insertion and removal
- Hash maps for O(1) position and price lookups
- Optimized for high-frequency event processing

### Scalability

- Supports multiple symbols simultaneously
- Can handle large historical datasets
- Modular design allows for distributed processing

## Extending the Engine

### Adding New Event Types

1. Create new event class inheriting from `Event`
2. Add corresponding `EventType` enum value
3. Update event processing in `BacktestingEngine`

### Custom Execution Models

```cpp
class MyExecutionHandler : public ExecutionHandler {
    // Override execution logic
    void executeOrder(const OrderEvent& order) override {
        // Custom execution implementation
    }
};
```

### Risk Management

```cpp
class RiskManager {
public:
    bool validateOrder(const OrderEvent& order) {
        // Position limits, drawdown checks, etc.
        return true;
    }
};
```

## Output Format

The engine provides detailed logging of all events:

```
MarketEvent: AAPL @ 150.00 Vol: 1000
  -> SignalEvent: BUY AAPL Strength: 1.0
    -> OrderEvent: MARKET BUY 100 AAPL @ 0.0
      -> FillEvent: BUY 100 AAPL @ 150.15
Fill processed: BUY 100 AAPL @ 150.15 | Capital: $84985

Backtest completed!
Final Portfolio Value: $101500.75
```

## Requirements

- **C++ Standard**: C++14 or later
- **Compiler**: GCC 5.0+, Clang 3.8+, or MSVC 2015+
- **Dependencies**: Standard library only (no external dependencies)

## License

This project is released under the MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Areas for Contribution

- Additional strategy implementations
- Enhanced risk management
- Performance analytics and reporting
- Data source integrations
- Optimization algorithms
- Documentation improvements

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

## Roadmap

- [ ] Multi-threaded event processing
- [ ] Real-time data integration
- [ ] Advanced order types (stop-loss, take-profit)
- [ ] Portfolio optimization tools
- [ ] Risk analytics dashboard
- [ ] Database integration
- [ ] REST API interface
- [ ] Python bindings
