"""
Integration tests for tools/calculate_metrics.py

Tests cover:
- calculate_metrics with synthetic portfolio data
- get_price_at_date with daily and hourly time series
- detect_market_type for crypto vs stock portfolios
- calculate_portfolio_values with mock price data
"""

import json
import os
import sys
import tempfile
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.calculate_metrics import (
    calculate_metrics,
    get_price_at_date,
    detect_market_type,
    calculate_portfolio_values,
    load_position_data,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_portfolio_df(values):
    """Build a minimal portfolio DataFrame from a list of total values."""
    dates = pd.date_range("2025-01-01", periods=len(values), freq="D")
    return pd.DataFrame({
        "date": dates,
        "cash": values,
        "stock_value": [0.0] * len(values),
        "total_value": values,
    })


def _make_price_data(symbol, dates_prices):
    """Build mock price_data dict with daily time series."""
    time_series = {
        date: {"4. close": str(price)} for date, price in dates_prices.items()
    }
    return {symbol: {"Time Series (Daily)": time_series}}


# ---------------------------------------------------------------------------
# calculate_metrics
# ---------------------------------------------------------------------------

class TestCalculateMetrics:
    def test_positive_return(self):
        values = [10000, 10100, 10200, 10300, 10400, 10500]
        df = _make_portfolio_df(values)
        metrics = calculate_metrics(df)
        assert metrics["CR"] == pytest.approx((10500 - 10000) / 10000, rel=1e-6)
        assert metrics["Final Value"] == 10500
        assert metrics["Initial Value"] == 10000

    def test_zero_return(self):
        values = [10000] * 5
        df = _make_portfolio_df(values)
        metrics = calculate_metrics(df)
        assert metrics["CR"] == pytest.approx(0.0, abs=1e-9)
        assert metrics["Vol"] == pytest.approx(0.0, abs=1e-9)

    def test_negative_return(self):
        values = [10000, 9800, 9600, 9400]
        df = _make_portfolio_df(values)
        metrics = calculate_metrics(df)
        assert metrics["CR"] < 0
        assert metrics["MDD"] < 0

    def test_mdd_correct_on_drawdown(self):
        # Portfolio rises then falls sharply
        values = [100, 200, 150, 50, 80]
        df = _make_portfolio_df(values)
        metrics = calculate_metrics(df)
        # MDD should be negative
        assert metrics["MDD"] < 0

    def test_win_rate_all_positive(self):
        values = [100, 110, 120, 130, 140]
        df = _make_portfolio_df(values)
        metrics = calculate_metrics(df)
        assert metrics["Win Rate"] == pytest.approx(1.0)

    def test_win_rate_all_negative(self):
        values = [100, 90, 80, 70]
        df = _make_portfolio_df(values)
        metrics = calculate_metrics(df)
        assert metrics["Win Rate"] == pytest.approx(0.0)

    def test_returns_all_expected_keys(self):
        df = _make_portfolio_df([10000, 10100, 10200])
        metrics = calculate_metrics(df)
        expected_keys = [
            "CR", "Annualized Return", "SR", "Sharpe Ratio",
            "Vol", "MDD", "Calmar Ratio", "Win Rate",
            "Average Win", "Average Loss", "Initial Value",
            "Final Value", "Total Positions", "Number of Trades", "Date Range",
        ]
        for key in expected_keys:
            assert key in metrics, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# get_price_at_date
# ---------------------------------------------------------------------------

class TestGetPriceAtDate:
    def test_exact_daily_match(self):
        price_data = _make_price_data("AAPL", {"2025-01-02": 150.0})
        price = get_price_at_date(price_data, "AAPL", "2025-01-02")
        assert price == pytest.approx(150.0)

    def test_fallback_to_previous_daily(self):
        price_data = _make_price_data("AAPL", {"2025-01-02": 150.0})
        # Request a date after the available date
        price = get_price_at_date(price_data, "AAPL", "2025-01-05")
        assert price == pytest.approx(150.0)

    def test_missing_symbol_returns_none(self):
        price_data = _make_price_data("AAPL", {"2025-01-02": 150.0})
        assert get_price_at_date(price_data, "MSFT", "2025-01-02") is None

    def test_no_available_date_returns_none(self):
        price_data = _make_price_data("AAPL", {"2025-01-10": 150.0})
        # Request a date before earliest available
        assert get_price_at_date(price_data, "AAPL", "2025-01-01") is None

    def test_hourly_exact_match(self):
        symbol_data = {
            "Time Series (60min)": {
                "2025-01-02 10:00:00": {"4. close": "155.5"}
            }
        }
        price_data = {"AAPL": symbol_data}
        price = get_price_at_date(price_data, "AAPL", "2025-01-02 10:00:00")
        assert price == pytest.approx(155.5)


# ---------------------------------------------------------------------------
# detect_market_type
# ---------------------------------------------------------------------------

class TestDetectMarketType:
    def _make_positions(self, symbols):
        return [{"positions": {s: 10 for s in symbols}} for _ in range(3)]

    def test_detects_crypto(self):
        positions = self._make_positions(["BTC", "ETH", "CASH"])
        assert detect_market_type(positions) == "crypto"

    def test_detects_stock(self):
        positions = self._make_positions(["AAPL", "MSFT", "CASH"])
        assert detect_market_type(positions) == "stock"

    def test_cash_only_is_stock(self):
        positions = self._make_positions(["CASH"])
        assert detect_market_type(positions) == "stock"


# ---------------------------------------------------------------------------
# calculate_portfolio_values
# ---------------------------------------------------------------------------

class TestCalculatePortfolioValues:
    def test_cash_only_portfolio(self):
        positions = [
            {"date": "2025-01-02", "positions": {"CASH": 10000}},
            {"date": "2025-01-03", "positions": {"CASH": 10000}},
        ]
        price_data = {}
        df = calculate_portfolio_values(positions, price_data, verbose=False)
        assert len(df) == 2
        assert (df["total_value"] == 10000).all()

    def test_portfolio_with_stock(self):
        positions = [
            {"date": "2025-01-02", "positions": {"CASH": 5000, "AAPL": 10}},
        ]
        price_data = _make_price_data("AAPL", {"2025-01-02": 150.0})
        df = calculate_portfolio_values(positions, price_data, verbose=False)
        assert df.iloc[0]["total_value"] == pytest.approx(5000 + 10 * 150.0)

    def test_missing_price_does_not_crash(self):
        positions = [
            {"date": "2025-01-02", "positions": {"CASH": 5000, "AAPL": 10}},
        ]
        df = calculate_portfolio_values(positions, {}, verbose=False)
        # Stock value should be 0 when price missing
        assert df.iloc[0]["total_value"] == pytest.approx(5000.0)


# ---------------------------------------------------------------------------
# load_position_data
# ---------------------------------------------------------------------------

class TestLoadPositionData:
    def test_load_valid_jsonl(self):
        records = [
            {"date": "2025-01-02", "positions": {"CASH": 10000}},
            {"date": "2025-01-03", "positions": {"CASH": 9500, "AAPL": 5}},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
            tmp_path = f.name

        try:
            loaded = load_position_data(tmp_path)
            assert len(loaded) == 2
            assert loaded[0]["date"] == "2025-01-02"
            assert loaded[1]["positions"]["AAPL"] == 5
        finally:
            os.unlink(tmp_path)
