#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <memory>

// Include the main backtesting engine header
// Note: In practice, you'd split the main .cpp into .h and .cpp files
// For now, we'll assume the classes are available

// Forward declarations - these would come from your header file
class Event;
class MarketEvent;
class SignalEvent;
class OrderEvent;
class FillEvent;
class Strategy;
class SMAStrategy;
class Portfolio;
class ExecutionHandler;
class BacktestingEngine;
class Position;

enum class EventType;
enum class OrderType;
enum class OrderDirection;

namespace py = pybind11;

// Custom strategy wrapper to allow Python inheritance
class PyStrategy : public Strategy {
public:
    using Strategy::Strategy;
    
    void calculateSignals(const MarketEvent& market_event) override {
        PYBIND11_OVERRIDE_PURE(
            void,
            Strategy,
            calculateSignals,
            market_event
        );
    }
    
    std::string getName() const override {
        PYBIND11_OVERRIDE_PURE(
            std::string,
            Strategy,
            getName
        );
    }
};

PYBIND11_MODULE(backtesting_engine, m) {
    m.doc() = "Event-Driven Backtesting Engine - Python Bindings";
    
    // Enums
    py::enum_<EventType>(m, "EventType")
        .value("MARKET", EventType::MARKET)
        .value("SIGNAL", EventType::SIGNAL)
        .value("ORDER", EventType::ORDER)
        .value("FILL", EventType::FILL)
        .export_values();
    
    py::enum_<OrderType>(m, "OrderType")
        .value("MARKET", OrderType::MARKET)
        .value("LIMIT", OrderType::LIMIT)
        .value("STOP", OrderType::STOP)
        .export_values();
    
    py::enum_<OrderDirection>(m, "OrderDirection")
        .value("BUY", OrderDirection::BUY)
        .value("SELL", OrderDirection::SELL)
        .export_values();
    
    // Base Event class
    py::class_<Event, std::shared_ptr<Event>>(m, "Event")
        .def("get_type", &Event::getType)
        .def("to_string", &Event::toString);
    
    // MarketEvent
    py::class_<MarketEvent, Event, std::shared_ptr<MarketEvent>>(m, "MarketEvent")
        .def(py::init<const std::string&, double, int64_t, int>(),
             py::arg("symbol"), py::arg("price"), py::arg("timestamp"), py::arg("volume") = 0)
        .def("get_symbol", &MarketEvent::getSymbol)
        .def("get_price", &MarketEvent::getPrice)
        .def("get_timestamp", &MarketEvent::getTimestamp)
        .def("get_volume", &MarketEvent::getVolume)
        .def("to_string", &MarketEvent::toString);
    
    // SignalEvent
    py::class_<SignalEvent, Event, std::shared_ptr<SignalEvent>>(m, "SignalEvent")
        .def(py::init<const std::string&, OrderDirection, double, const std::string&>(),
             py::arg("symbol"), py::arg("direction"), py::arg("strength") = 1.0, py::arg("strategy_id") = "")
        .def("get_symbol", &SignalEvent::getSymbol)
        .def("get_direction", &SignalEvent::getDirection)
        .def("get_strength", &SignalEvent::getStrength)
        .def("get_strategy_id", &SignalEvent::getStrategyId)
        .def("to_string", &SignalEvent::toString);
    
    // OrderEvent
    py::class_<OrderEvent, Event, std::shared_ptr<OrderEvent>>(m, "OrderEvent")
        .def(py::init<const std::string&, OrderType, int, OrderDirection, double>(),
             py::arg("symbol"), py::arg("order_type"), py::arg("quantity"), 
             py::arg("direction"), py::arg("price") = 0.0)
        .def("get_symbol", &OrderEvent::getSymbol)
        .def("get_order_type", &OrderEvent::getOrderType)
        .def("get_quantity", &OrderEvent::getQuantity)
        .def("get_direction", &OrderEvent::getDirection)
        .def("get_price", &OrderEvent::getPrice)
        .def("to_string", &OrderEvent::toString);
    
    // FillEvent
    py::class_<FillEvent, Event, std::shared_ptr<FillEvent>>(m, "FillEvent")
        .def(py::init<const std::string&, int, OrderDirection, double, double, int64_t>(),
             py::arg("symbol"), py::arg("quantity"), py::arg("direction"),
             py::arg("fill_price"), py::arg("commission") = 0.0, py::arg("timestamp") = 0)
        .def("get_symbol", &FillEvent::getSymbol)
        .def("get_quantity", &FillEvent::getQuantity)
        .def("get_direction", &FillEvent::getDirection)
        .def("get_fill_price", &FillEvent::getFillPrice)
        .def("get_commission", &FillEvent::getCommission)
        .def("get_timestamp", &FillEvent::getTimestamp)
        .def("to_string", &FillEvent::toString);
    
    // Position
    py::class_<Position>(m, "Position")
        .def(py::init<const std::string&>())
        .def("update_position", &Position::updatePosition)
        .def("get_symbol", &Position::getSymbol)
        .def("get_quantity", &Position::getQuantity)
        .def("get_avg_price", &Position::getAvgPrice)
        .def("get_market_value", &Position::getMarketValue);
    
    // Strategy base class (with Python inheritance support)
    py::class_<Strategy, PyStrategy, std::shared_ptr<Strategy>>(m, "Strategy")
        .def(py::init<>())
        .def("calculate_signals", &Strategy::calculateSignals)
        .def("get_name", &Strategy::getName);
    
    // SMAStrategy
    py::class_<SMAStrategy, Strategy, std::shared_ptr<SMAStrategy>>(m, "SMAStrategy")
        .def(py::init<int>(), py::arg("window_size") = 20)
        .def("calculate_signals", &SMAStrategy::calculateSignals)
        .def("get_name", &SMAStrategy::getName);
    
    // Portfolio
    py::class_<Portfolio>(m, "Portfolio")
        .def(py::init<double>(), py::arg("initial_capital") = 100000.0)
        .def("update_signal", &Portfolio::updateSignal)
        .def("update_fill", &Portfolio::updateFill)
        .def("get_current_price", &Portfolio::getCurrentPrice)
        .def("update_price", &Portfolio::updatePrice)
        .def("get_total_value", &Portfolio::getTotalValue);
    
    // ExecutionHandler
    py::class_<ExecutionHandler>(m, "ExecutionHandler")
        .def(py::init<>())
        .def("execute_order", &ExecutionHandler::executeOrder)
        .def("update_price", &ExecutionHandler::updatePrice);
    
    // BacktestingEngine
    py::class_<BacktestingEngine>(m, "BacktestingEngine")
        .def(py::init<>())
        .def("add_strategy", [](BacktestingEngine& self, std::shared_ptr<Strategy> strategy) {
            // Convert shared_ptr to unique_ptr for the C++ interface
            std::unique_ptr<Strategy> unique_strategy(strategy.get());
            strategy.reset(); // Release from shared_ptr to avoid double deletion
            self.addStrategy(std::move(unique_strategy));
        })
        .def("add_market_data", &BacktestingEngine::addMarketData,
             py::arg("symbol"), py::arg("price"), py::arg("timestamp"), py::arg("volume") = 0)
        .def("run", &BacktestingEngine::run);
    
    // Utility functions for creating events from Python
    m.def("create_market_event", 
          [](const std::string& symbol, double price, int64_t timestamp, int volume) {
              return std::make_shared<MarketEvent>(symbol, price, timestamp, volume);
          },
          py::arg("symbol"), py::arg("price"), py::arg("timestamp"), py::arg("volume") = 0,
          "Create a MarketEvent");
    
    m.def("create_signal_event",
          [](const std::string& symbol, OrderDirection direction, double strength, const std::string& strategy_id) {
              return std::make_shared<SignalEvent>(symbol, direction, strength, strategy_id);
          },
          py::arg("symbol"), py::arg("direction"), py::arg("strength") = 1.0, py::arg("strategy_id") = "",
          "Create a SignalEvent");
    
    // Version info
    m.attr("__version__") = "1.0.0";
}