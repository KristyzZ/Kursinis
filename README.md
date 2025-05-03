# Investment Portfolio Manager

A desktop-based investment portfolio tracker built with Python and Tkinter. This application allows users to manage stock investments, view live market data, analyze performance by sector, sort investments, and export reports.

---

## 📦 Features

- ✅ Add, update, and remove stock investments
- 📈 Live price updates via `yfinance`
- 🔄 Sort by name, symbol, price, profit/loss, or % change
- 📊 Sector distribution pie chart
- 🧠 Calculate profit/loss and historical change (daily/weekly/monthly/yearly)
- 💾 Save/load data to/from `portfolio.json`
- 📤 Export portfolio to CSV and Excel
- 🔐 Singleton pattern for portfolio manager
- 🧪 Unit testing support (unittest ready)
- 🎨 Tkinter-based graphical interface

---

## 🚀 Getting Started

### Prerequisites

Install required packages:
```bash
pip install yfinance pandas openpyxl matplotlib
```

### Run the App

```bash
python main.py
```

---

## 📁 Project Structure

```
.
├── /.git
├── /Include
├── /Lib
├── /models
│   └── investment.py
│   └── portfolio.py
│   └── stock.py
├── /Scripts
├── /share
├── /ui
│   └── portfolio_app.py
├── /utils
│   └── file_operations.py
│   └── exceptions.py

├── /tests
│   └── test_portfolio.py
│   └── __init__.py
│   └── test_file_operations_fixed.py
│   └── test_stock.py
├── main.py
├── portfolio.json
└── README.md
```

---

## 🧠 OOP Concepts Used

- **Encapsulation**: Investment data managed via class attributes
- **Inheritance**: `Stock` inherits from abstract `Investment`
- **Polymorphism**: `calculate_value()` implemented in each investment type
- **Abstraction**: `Investment` defines abstract methods

### Design Pattern

- **Singleton**: Ensures a single shared `PortfolioManager` instance

---

## 🧪 Testing

Unit tests can be added in the `/tests` folder using the `unittest` framework.

---

## 📌 Future Improvements

- Add crypto or ETF support
- Add historical performance chart
- Enable multiple user profiles

---

## 🛠 Author

Created by Kristijonas Čepelis EKf-24 for OOP coursework (2025).
