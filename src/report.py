"""Generates a static HTML report from EquityAnalyzer results."""

from __future__ import annotations

import os
from datetime import datetime


def format_pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def format_currency(v: float) -> str:
    return f"${v:,.0f}"


def render_report(metrics, prices, output_path: str = "reports/equity_analysis_report.html") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    price_rows = ""
    for date, row in prices.iterrows():
        row_html = "<tr>" + "".join(f"<td>{v:.2f}</td>" for v in row) + "</tr>"
        price_rows += row_html

    rows = [
        ("Annualized Return", format_pct(metrics.annualized_return)),
        ("Annualized Volatility", format_pct(metrics.annualized_volatility)),
        ("Sharpe Ratio", f"{metrics.sharpe_ratio:.2f}"),
        ("Sortino Ratio", f"{metrics.sortino_ratio:.2f}"),
        ("Max Drawdown", format_pct(metrics.max_drawdown)),
        ("Calmar Ratio", f"{metrics.calmar_ratio:.2f}"),
        ("Beta", f"{metrics.beta:.2f}"),
        ("Alpha", format_pct(metrics.alpha)),
        ("Treynor Ratio", f"{metrics.treynor_ratio:.2f}"),
        ("VaR (90%)", format_currency(metrics.var_90)),
        ("VaR (95%)", format_currency(metrics.var_95)),
        ("VaR (99%)", format_currency(metrics.var_99)),
        ("CVaR (95%)", format_currency(metrics.cvar_95)),
    ]

    metrics_rows = ""
    for label, value in rows:
        metrics_rows += f"<tr><td>{label}</td><td><strong>{value}</strong></td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Equity Analysis Report — {", ".join(metrics.tickers)}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f172a; color: #e2e8f0; padding: 2rem; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ color: #60a5fa; margin-bottom: 0.5rem; }}
  .subtitle {{ color: #94a3b8; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem; }}
  .card {{ background: #1e293b; border-radius: 8px; padding: 1.5rem; border: 1px solid #334155; }}
  h2 {{ color: #93c5fd; font-size: 1.1rem; margin-bottom: 1rem; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td {{ padding: 0.5rem 0; border-bottom: 1px solid #1e293b; }}
  tr:last-child td {{ border-bottom: none; }}
  .val {{ text-align: right; color: #86efac; }}
  .header {{ text-align: left; }}
  .tag {{ display: inline-block; background: #1d4ed8; color: white; padding: 0.2rem 0.6rem;
         border-radius: 4px; font-size: 0.75rem; margin-right: 0.5rem; margin-bottom: 0.5rem; }}
  .weights {{ margin-bottom: 1.5rem; }}
  footer {{ text-align: center; color: #475569; margin-top: 2rem; font-size: 0.8rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>Equity Analysis Report</h1>
  <p class="subtitle">{metrics.start_date} → {metrics.end_date} &nbsp;|&nbsp; Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>

  <div class="weights">
    <span class="tag">Tickers</span>
    <span class="tag" style="background:#0f172a; border:1px solid #475569;">{'</span><span class="tag" style="background:#0f172a; border:1px solid #475569;">'.join(metrics.tickers)}</span>
    &nbsp;&nbsp;
    <span class="tag">Weights</span>
    <span class="tag" style="background:#0f172a; border:1px solid #475569;">{'</span><span class="tag" style="background:#0f172a; border:1px solid #475569;">'.join(f"{w:.0%}" for w in metrics.weights)}</span>
  </div>

  <div class="grid">
    <div class="card">
      <h2>Risk &amp; Return Metrics</h2>
      <table>
        <thead><tr><th class="header">Metric</th><th class="val">Value</th></tr></thead>
        <tbody>{metrics_rows}</tbody>
      </table>
    </div>

    <div class="card">
      <h2>Price Data Preview</h2>
      <div style="overflow-x:auto;">
      <table>
        <thead><tr><th>Date</th>{''.join(f'<th>{t}</th>' for t in metrics.tickers)}</tr></thead>
        <tbody>{price_rows}</tbody>
      </table>
      </div>
    </div>
  </div>

  <footer>Equities Investment Analysis Library — {", ".join(metrics.tickers)} Portfolio</footer>
</div>
</body>
</html>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
