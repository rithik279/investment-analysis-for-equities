"""Main entry point — runs analysis and generates report."""

from src.analyzer import analyze
from src.report import render_report
from src.analyzer import EquityAnalyzer

if __name__ == "__main__":
    tickers = ["JPM", "MS", "BAC"]
    start = "2024-01-01"
    end = "2025-01-01"

    metrics = analyze(tickers=tickers, start=start, end=end, generate_plots=False)

    analyzer = EquityAnalyzer(tickers, start_date=start, end_date=end)
    prices = analyzer.fetch_data()
    _ = analyzer.compute_metrics()
    report_path = render_report(metrics, prices)
    print(f"Report: {report_path}")
