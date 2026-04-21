"""Portfolio risk metrics computation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import yfinance as yf
from dataclasses import dataclass, asdict


@dataclass
class PortfolioMetrics:
    tickers: list[str]
    weights: list[float]
    start_date: str
    end_date: str
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    beta: float
    alpha: float
    treynor_ratio: float
    var_90: float
    var_95: float
    var_99: float
    cvar_95: float

    def to_dict(self) -> dict:
        return asdict(self)


def fetch_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    data = yf.download(tickers, start=start, end=end)["Close"]
    if data.empty:
        raise ValueError(f"No data fetched for tickers: {tickers}")
    return data.dropna()


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()


def compute_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices / prices.shift(1)).dropna()


def compute_annualized_return(portfolio_returns: pd.Series, method: str = "simple") -> float:
    if method == "simple":
        return (1 + portfolio_returns.mean()) ** 252 - 1
    return portfolio_returns.mean() * 252


def compute_volatility(portfolio_returns: pd.Series) -> float:
    return portfolio_returns.std() * np.sqrt(252)


def compute_beta(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    combined = np.cov(portfolio_returns.to_numpy().flatten(), benchmark_returns.to_numpy().flatten())
    return combined[0, 1] / combined[1, 1]


def compute_alpha(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    beta: float,
    risk_free_rate: float = 0.07,
) -> float:
    excess_portfolio = np.mean(portfolio_returns) - risk_free_rate / 252
    excess_benchmark = np.mean(benchmark_returns) - risk_free_rate / 252
    return (excess_portfolio - beta * excess_benchmark) * 252


def compute_sharpe_ratio(
    portfolio_returns: pd.Series, risk_free_rate: float = 0.07, volatility: float | None = None
) -> float:
    vol = volatility if volatility is not None else compute_volatility(portfolio_returns)
    return (compute_annualized_return(portfolio_returns) - risk_free_rate) / vol


def compute_sortino_ratio(portfolio_returns: pd.Series, risk_free_rate: float = 0.07) -> float:
    negative_returns = portfolio_returns[portfolio_returns < 0]
    downside_dev = negative_returns.std() * np.sqrt(252)
    return (compute_annualized_return(portfolio_returns) - risk_free_rate) / downside_dev


def compute_max_drawdown(portfolio_returns: pd.Series) -> float:
    cumulative = (1 + portfolio_returns).cumprod()
    drawdown = (cumulative.cummax() - cumulative) / cumulative.cummax()
    return drawdown.max()


def compute_calmar_ratio(portfolio_returns: pd.Series) -> float:
    return compute_annualized_return(portfolio_returns) / compute_max_drawdown(portfolio_returns)


def compute_treynor_ratio(portfolio_returns: pd.Series, beta: float, risk_free_rate: float = 0.07) -> float:
    return (compute_annualized_return(portfolio_returns) - risk_free_rate) / beta


def compute_var(portfolio_returns: pd.Series, percentile: int, portfolio_value: float = 1_000_000) -> float:
    return np.percentile(portfolio_returns, 100 - percentile) * portfolio_value


def compute_cvar(portfolio_returns: pd.Series, percentile: int, portfolio_value: float = 1_000_000) -> float:
    threshold = np.percentile(portfolio_returns, 100 - percentile)
    return portfolio_returns[portfolio_returns <= threshold].mean() * portfolio_value


class EquityAnalyzer:
    DEFAULT_TICKERS = ["JPM", "MS", "BAC"]

    def __init__(
        self,
        tickers: list[str] | None = None,
        weights: list[float] | None = None,
        start_date: str = "2024-01-01",
        end_date: str = "2025-01-01",
        risk_free_rate: float = 0.07,
    ):
        self.tickers = tickers or self.DEFAULT_TICKERS
        self.weights = np.array(weights or [1 / len(self.tickers)] * len(self.tickers))
        self.start_date = start_date
        self.end_date = end_date
        self.risk_free_rate = risk_free_rate
        self._prices: pd.DataFrame | None = None
        self._returns: pd.DataFrame | None = None
        self._log_returns: pd.DataFrame | None = None
        self._portfolio_returns: pd.Series | None = None
        self._benchmark_returns: pd.Series | None = None
        self._metrics: PortfolioMetrics | None = None

    def fetch_data(self) -> pd.DataFrame:
        self._prices = fetch_prices(self.tickers, self.start_date, self.end_date)
        self._returns = compute_returns(self._prices)
        self._log_returns = compute_log_returns(self._prices)
        self._portfolio_returns = self._returns.dot(self.weights)
        benchmark = yf.download("^GSPC", start=self.start_date, end=self.end_date)["Close"]
        self._benchmark_returns = benchmark.pct_change().dropna()
        return self._prices

    def compute_metrics(self) -> PortfolioMetrics:
        if self._portfolio_returns is None:
            self.fetch_data()

        beta = compute_beta(self._portfolio_returns, self._benchmark_returns)
        volatility = compute_volatility(self._portfolio_returns)
        ann_return = compute_annualized_return(self._portfolio_returns)
        max_dd = compute_max_drawdown(self._portfolio_returns)
        port_value = 1_000_000

        self._metrics = PortfolioMetrics(
            tickers=self.tickers,
            weights=self.weights.tolist(),
            start_date=self.start_date,
            end_date=self.end_date,
            annualized_return=ann_return,
            annualized_volatility=volatility,
            sharpe_ratio=compute_sharpe_ratio(self._portfolio_returns, self.risk_free_rate, volatility),
            sortino_ratio=compute_sortino_ratio(self._portfolio_returns, self.risk_free_rate),
            max_drawdown=max_dd,
            calmar_ratio=ann_return / max_dd,
            beta=beta,
            alpha=compute_alpha(self._portfolio_returns, self._benchmark_returns, beta, self.risk_free_rate),
            treynor_ratio=compute_treynor_ratio(self._portfolio_returns, beta, self.risk_free_rate),
            var_90=compute_var(self._portfolio_returns, 90, port_value),
            var_95=compute_var(self._portfolio_returns, 95, port_value),
            var_99=compute_var(self._portfolio_returns, 99, port_value),
            cvar_95=compute_cvar(self._portfolio_returns, 95, port_value),
        )
        return self._metrics

    def plot_cumulative_returns(self, save_path: str | None = None) -> None:
        if self._portfolio_returns is None:
            self.fetch_data()
        cumulative = (1 + self._portfolio_returns).cumprod()
        plt.figure(figsize=(10, 5))
        plt.plot(cumulative.index, cumulative.values, label="Portfolio", color="#2563eb")
        benchmark_cumulative = (1 + self._benchmark_returns).cumprod()
        plt.plot(benchmark_cumulative.index, benchmark_cumulative.values, label="S&P 500", color="#dc2626", linestyle="--")
        plt.title("Cumulative Returns: Portfolio vs S&P 500")
        plt.xlabel("Date")
        plt.ylabel("Cumulative Return")
        plt.legend()
        plt.grid(True, alpha=0.3)
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.show()
        plt.close()

    def plot_drawdown(self, save_path: str | None = None) -> None:
        if self._portfolio_returns is None:
            self.fetch_data()
        cumulative = (1 + self._portfolio_returns).cumprod()
        drawdown = (cumulative.cummax() - cumulative) / cumulative.cummax()
        plt.figure(figsize=(10, 4))
        plt.fill_between(drawdown.index, drawdown.values, color="#ef4444", alpha=0.4)
        plt.plot(drawdown.index, drawdown.values, color="#ef4444")
        plt.title("Portfolio Drawdown")
        plt.xlabel("Date")
        plt.ylabel("Drawdown")
        plt.grid(True, alpha=0.3)
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.show()
        plt.close()


def analyze(
    tickers: list[str] | None = None,
    weights: list[float] | None = None,
    start: str = "2024-01-01",
    end: str = "2025-01-01",
    risk_free_rate: float = 0.07,
    generate_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "reports",
) -> PortfolioMetrics:
    """Main entry point. Runs full analysis and returns metrics.

    Args:
        tickers: List of equity tickers. Defaults to JPM, MS, BAC.
        weights: Portfolio weights (must sum to 1). Defaults to equal weight.
        start: Start date (YYYY-MM-DD).
        end: End date (YYYY-MM-DD).
        risk_free_rate: Annual risk-free rate for ratio calculations.
        generate_plots: Whether to display plots.
        save_plots: Whether to save plots to output_dir.
        output_dir: Directory for saved outputs.

    Returns:
        PortfolioMetrics dataclass with all computed risk/return values.
    """
    analyzer = EquityAnalyzer(tickers, weights, start, end, risk_free_rate)
    _ = analyzer.fetch_data()
    metrics = analyzer.compute_metrics()

    if generate_plots:
        prefix = f"{output_dir}/" if save_plots else None
        analyzer.plot_cumulative_returns(save_path=f"{prefix}cumret.png" if save_plots else None)
        analyzer.plot_drawdown(save_path=f"{prefix}drawdown.png" if save_plots else None)

    return metrics
