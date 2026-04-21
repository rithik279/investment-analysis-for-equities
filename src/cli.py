"""CLI entry point."""

import argparse

from src.analyzer import analyze, EquityAnalyzer
from src.report import render_report


def main():
    parser = argparse.ArgumentParser(description="Equity Investment Analysis")
    parser.add_argument("--tickers", nargs="+", default=["JPM", "MS", "BAC"], help="Equity tickers")
    parser.add_argument("--weights", nargs="+", type=float, default=None, help="Portfolio weights (must sum to 1)")
    parser.add_argument("--start", default="2024-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2025-01-01", help="End date YYYY-MM-DD")
    parser.add_argument("--rfr", type=float, default=0.07, help="Annual risk-free rate")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")
    parser.add_argument("--plots", action="store_true", help="Show plots")
    parser.add_argument("--save-plots", action="store_true", help="Save plots to reports/")
    args = parser.parse_args()

    metrics = analyze(
        tickers=args.tickers,
        weights=args.weights,
        start=args.start,
        end=args.end,
        risk_free_rate=args.rfr,
        generate_plots=args.plots,
        save_plots=args.save_plots,
    )

    print("\n=== Portfolio Metrics ===")
    for k, v in metrics.to_dict().items():
        if k not in ("tickers", "weights", "start_date", "end_date"):
            label = k.replace("_", " ").title()
            val = f"{v * 100:.2f}%" if abs(v) < 10 else f"${v:,.0f}"
            print(f"  {label}: {val}")

    if args.report:
        analyzer = EquityAnalyzer(args.tickers, args.weights, args.start, args.end, args.rfr)
        prices = analyzer.fetch_data()
        _ = analyzer.compute_metrics()
        path = render_report(metrics, prices)
        print(f"\nReport saved: {path}")


if __name__ == "__main__":
    main()
