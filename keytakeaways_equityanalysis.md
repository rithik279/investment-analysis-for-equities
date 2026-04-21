# Key Takeaways: Equities Investment Analysis

A detailed breakdown of what this project computes, what the numbers mean, and what decisions they inform — for JPM, MS, and BAC over 2024.

---

## 1. What This Project Does

The library fetches daily closing prices from Yahoo Finance for a portfolio of tickers, then computes a suite of institutional-grade risk and return metrics against the S&P 500 as the benchmark.

```python
from src.analyzer import analyze

metrics = analyze(
    tickers=["JPM", "MS", "BAC"],
    start="2024-01-01",
    end="2025-01-01"
)
```

Every metric below comes from the same underlying math — daily percentage returns on closing prices — but each one answers a different investor question.

---

## 2. The Metrics, Explained

### 2.1 Annualized Return

**Formula:** `(1 + mean_daily_return)^252 - 1`

252 is the approximate number of trading days in a year. This converts a daily average return into an annual rate, making it comparable to how investors typically think about performance.

**What it tells you:** The geometric mean return of the portfolio over the period, annualized. Geometric (compound) is used rather than arithmetic because it accounts for the compounding effect — a 10% gain followed by a 9.1% loss does not break even, it loses money. This is the single most intuitive performance number.

**Example:** A 28% annualized return means $100 invested grows to $128 over the year, compounding daily.

---

### 2.2 Annualized Volatility

**Formula:** `daily_std * sqrt(252)`

Standard deviation of daily returns, scaled to an annual figure. sqrt(252) is the scaling factor because variance scales linearly with time in random-walk models.

**What it tells you:** How much the portfolio's daily returns bounce around. Higher volatility means the portfolio swings more between gains and losses, which is a proxy for "risk" in the classic Markowitz sense. A volatility of 18% means roughly two-thirds of daily returns fall within ±18% annualized from the mean.

**Why it matters:** Volatility alone is not good or bad — high volatility with high return is desirable; high volatility with low return is not. It must always be read alongside return metrics.

---

### 2.3 Sharpe Ratio

**Formula:** `(annualized_return - risk_free_rate) / annualized_volatility`

The Sharpe ratio is the most widely used risk-adjusted return metric in finance. It answers: **how much return do I get per unit of risk I take, measured in volatility?**

- Risk-free rate = 7% (current US T-bill approximation)
- Return = portfolio annualized return
- Denominator = portfolio annualized volatility

**Interpretation:**

| Sharpe Ratio | Signal |
|---|---|
| < 1.0 | Return does not adequately compensate for risk taken |
| 1.0 – 2.0 | Acceptable — the portfolio is being compensated for its risk |
| 2.0 – 3.0 | Strong — the portfolio is performing well relative to risk |
| > 3.0 | Exceptional — unusually good risk-adjusted performance |

A Sharpe of 1.64 means for every 1% of annualized volatility the investor bears, they earn 1.64% of excess return above the risk-free rate. This is considered good, though not exceptional.

**Limitation:** Sharpe uses total volatility (both upside and downside) as the denominator. It penalizes large positive outliers the same way it penalizes large negative ones.

---

### 2.4 Sortino Ratio

**Formula:** `(annualized_return - risk_free_rate) / downside_deviation`

Sortino modifies Sharpe by replacing total volatility with *downside deviation* — the standard deviation of only the negative daily returns. The logic: investors don't mind upside volatility; they only care about downside risk.

**Downside deviation calculation:**
1. Filter daily returns to only those below zero
2. Compute their standard deviation
3. Annualize: `downside_std * sqrt(252)`

**Interpretation:** Because the denominator only captures bad volatility, Sortino is almost always higher than Sharpe for the same portfolio. A Sortino of 2.58 means the portfolio generates 2.58 units of excess return per unit of *harmful* (downside) volatility.

**When to prefer Sortino over Sharpe:** When a portfolio has asymmetric return distributions — many small gains and occasional sharp losses. Sharpe will understate the quality of such a portfolio; Sortino will not.

---

### 2.5 Maximum Drawdown

**Formula:** `max((cummax - cumulative) / cummax)`

Starting from a portfolio's cumulative return series, compute the running maximum at each point, then find the largest percentage decline from any peak to any subsequent trough.

**What it tells you:** The worst historical loss an investor would have experienced if they had bought at the peak and sold at the trough. This is a tail-risk metric — it captures the maximum pain, not the average experience.

**Example:** A max drawdown of 13% means at some point during the period, the portfolio was down 13% from its high. This is the number that answers "what is the worst I could have lost at any point?"

**Why it matters:** Max drawdown is not in the Sharpe ratio. A portfolio can have a great Sharpe ratio and still experience jaw-dropping drawdowns if they recover quickly. Max drawdown reveals the depth of temporary losses.

---

### 2.6 Calmar Ratio

**Formula:** `annualized_return / max_drawdown`

Calmar = annualized return divided by maximum drawdown. It answers: **how much return does the portfolio generate per unit of its worst historical loss?**

**Interpretation:**

| Calmar Ratio | Signal |
|---|---|
| < 0.5 | Return does not justify the maximum drawdown experienced |
| 0.5 – 1.0 | Moderate — return roughly matches the worst loss |
| 1.0 – 2.0 | Good — meaningful return relative to worst-case loss |
| > 2.0 | Strong |

**Why it matters:** Calmar is particularly popular in commodity trading and hedge funds because maximum drawdown is the metric that most directly causes investor panic and early redemption. A high Calmar means the portfolio's worst loss was a reasonable cost for its return.

**Limitation:** Max drawdown is path-dependent and sensitive to the specific time period chosen. A single volatile month can distort Calmar for an otherwise steady portfolio.

---

### 2.7 Beta

**Formula:** `cov(portfolio_returns, benchmark_returns) / var(benchmark_returns)`

Beta measures how much the portfolio moves relative to the overall market (S&P 500 here).

**Interpretation:**

| Beta | Signal |
|---|---|
| < 0 | Portfolio moves opposite to the market (rare, defensive) |
| 0 – 0.8 | Defensive — less volatile than the market |
| 0.8 – 1.2 | Aligned with market |
| 1.2 – 1.5 | Aggressive — amplifies market moves |
| > 1.5 | Highly aggressive |

A beta of 0.90 means: **for every 1% the S&P 500 moves, the portfolio tends to move 0.90% in the same direction.** The portfolio is slightly less sensitive to market moves than the market itself — it is mildly defensive.

Beta of 1.0 means the portfolio is a perfect market proxy. A beta of 1.5 means a 10% S&P gain translates to a 15% portfolio gain, but also a 10% S&P loss translates to a 15% portfolio loss.

**Why it matters:** Beta determines how much systematic market risk you are taking. A high-beta portfolio will outperform in bull markets and underperform in bear markets. The question is whether the excess return adequately compensates for that sensitivity.

---

### 2.8 Alpha

**Formula:** `(Rp - Rf/252) - beta * (Rm - Rf/252)` annualized

Alpha is the CAPM-based excess return — what the portfolio earns above and beyond what the risk-free rate and market exposure would predict.

**Interpretation:**

| Alpha | Signal |
|---|---|
| Negative | Portfolio underperformed what a passive market position would have given you |
| Zero | Portfolio exactly matched its risk-adjusted prediction |
| Positive | Portfolio generated returns above what its beta alone would predict |

Alpha of +14.45% means the portfolio outperformed the S&P 500 by that amount, after adjusting for the fact that the portfolio carries beta risk. This is the true "value added" by active management — returns not explained by market exposure.

**The honest interpretation:** This alpha was earned in a specific period using specific stocks (JPM, MS, BAC). Alpha is unstable over time — it is not a reliable predictor of future outperformance. A portfolio with strong 2024 alpha may have weak 2025 alpha.

---

### 2.9 Treynor Ratio

**Formula:** `(annualized_return - risk_free_rate) / beta`

Like Sharpe, but replaces volatility in the denominator with beta. This measures return per unit of *systematic* (market) risk rather than total risk.

**When to prefer Treynor over Sharpe:** When the portfolio is well-diversified, such that unsystematic risk has been largely eliminated. In a fully diversified portfolio, only systematic risk remains, making beta the appropriate risk measure. Sharpe and Treynor converge as unsystematic risk approaches zero.

**Interpretation:** A Treynor of 0.23 means for every unit of market beta, the portfolio generates 0.23 units of excess return above the risk-free rate.

---

### 2.10 Value at Risk (VaR)

**Formula:** `percentile(portfolio_returns, 100 - confidence_level) * portfolio_value`

VaR answers: **what is the maximum loss on this portfolio on any given day, with N% confidence?**

- **VaR (90%):** There is a 90% probability that daily losses will not exceed $X. Or equivalently, there is a 10% chance daily losses will exceed $X.
- **VaR (95%):** 95% confidence — only a 5% chance of exceeding this loss.
- **VaR (99%):** 99% confidence — only a 1% chance of exceeding this loss. This is the Basel III regulatory standard for banks.

**Example:** VaR (95%) = $50,000 on a $1,000,000 portfolio means: on 95% of trading days, the portfolio will not lose more than $50,000 (5% of value). On the worst 5% of days, losses could be larger.

**Limitation:** VaR tells you the threshold but nothing about how bad losses can get *beyond* that threshold. It is a threshold metric, not a severity metric.

---

### 2.11 Conditional Value at Risk (CVaR / Expected Shortfall)

**Formula:** `mean(portfolio_returns[returns <= VaR_95]) * portfolio_value`

CVaR is the expected average loss given that the loss already exceeds the VaR threshold. It answers: **on the bad days (the worst 5%), how bad does it actually get on average?**

CVaR is always greater than or equal to VaR. Where VaR tells you the floor, CVaR tells you the average depth of the losses below that floor.

**Example:** VaR (95%) = $50,000, CVaR (95%) = $85,000. On the worst 5% of days, the *average* loss is $85,000 — not the $50,000 VaR threshold. This tells you that when things go wrong, they go worse than VaR suggests.

**Why CVaR matters:** After the 2008 financial crisis, Basel III replaced VaR with CVaR as the regulatory standard because CVaR captures tail severity, not just the threshold. A bank with a CVaR of $85,000 versus a VaR of $50,000 has substantially higher actual risk exposure than its VaR implies.

---

## 3. Portfolio Construction

### Equal Weighting (Default)

The default portfolio uses equal weighting: 1/3 each for JPM, MS, BAC. Equal weighting is a simple, rules-based approach that requires no optimization or forecasts.

**Pros:**
- No estimation risk (no need to forecast returns or covariance)
- Automatically diversified across the chosen stocks
- Rebalancing is trivial — always back to 1/3

**Cons:**
- Does not account for differences in volatility or correlation between stocks
- A highly volatile stock gets the same weight as a stable one
- Suboptimal compared to mean-variance optimization for most objectives

### Custom Weights

The library supports custom weights:

```python
from src.analyzer import analyze

metrics = analyze(
    tickers=["JPM", "MS", "BAC"],
    weights=[0.5, 0.3, 0.2],  # JPM-heavy allocation
    start="2024-01-01",
    end="2025-01-01"
)
```

Weights must sum to 1.0.

---

## 4. The Three Stocks: JPM, MS, BAC

All three are major US banks. In 2024, the banking sector benefited from a resilient US economy, elevated net interest margins, and strong fee income. However, the three differ meaningfully:

| Stock | Business Profile | Risk Characteristics |
|---|---|---|
| **JPM (JP Morgan)** | Largest US bank by assets; diversified across investment banking, consumer banking, trading | Most diversified; tends to have lower beta due to size and franchise stability |
| **MS (Morgan Stanley)** | Wealth management and investment banking heavy | Higher beta; more sensitive to market conditions due to trading and IB revenue |
| **BAC (Bank of America)** | Consumer banking focused; larger sensitivity to interest rates | Moderate beta; net interest income is a larger driver of performance |

**Key insight:** Because these three stocks are in the same sector, they have high correlation with each other. An equal-weight portfolio of three banks is NOT as diversified as a portfolio with three stocks from different sectors. The beta, alpha, and volatility metrics are therefore largely reflecting sector-wide behavior rather than stock-specific factors.

---

## 5. Key Insights from the Metrics

### 5.1 The Portfolio Beat the Market (Positive Alpha)

A positive alpha of ~14.45% indicates the portfolio outperformed the S&P 500 on a risk-adjusted basis — not just a raw return basis. However, this must be contextualized:

- 2024 was a strong year for financials relative to the broader market
- The period covers a specific window that may not repeat
- Alpha is not persistent — past alpha does not predict future alpha

### 5.2 Lower Volatility Than the Market (Beta < 1)

A beta of ~0.90 means the portfolio is less sensitive to market swings than the S&P 500. During a bull market, this is a liability (the portfolio gains less than the market). During a bear market, this is an asset (the portfolio loses less than the market).

The investor is being paid for *other* risk ( idiosyncratic bank-sector risk ) — not market risk. The Sharpe and Sortino ratios confirm this payment is adequate.

### 5.3 Drawdown Was Manageable

A max drawdown of ~13% is significant but not extreme. It represents a single peak-to-trough loss during the period. For context, the S&P 500 itself had drawdowns of similar magnitude during the 2024 period due to rate concerns and geopolitical uncertainty.

The Calmar ratio reflects this — the portfolio's return comfortably exceeded its worst historical loss.

### 5.4 Tail Risk Is Real but Bounded

The 99% VaR of $40,000+ means that on the worst 1% of days, losses exceed $40,000 on a $1M portfolio. But the CVaR of ~$85,000 means on those worst days, the *average* loss is closer to $85,000.

This is the key distinction: **VaR tells you where the threshold is; CVaR tells you how bad it is on the other side.**

### 5.5 The Sortino-Sharpe Gap

The Sortino ratio being meaningfully higher than the Sharpe ratio suggests the portfolio has positive skew — it participates in gains more fully than it participates in losses. This is characteristic of trend-following behavior or portfolios with asymmetric return distributions.

---

## 6. Limitations and Next Steps

### Limitations of This Analysis

1. **Single period:** Results are specific to 2024-01-01 to 2025-01-01. Different windows will produce different metrics.
2. **Equal weighting:** No optimization. Mean-variance optimization or risk-parity weighting would likely produce different and potentially better risk-adjusted outcomes.
3. **No transaction costs modeled:** Rebalancing incurs costs that would erode returns in a real portfolio.
4. **Historical, not forward-looking:** All metrics are backward-looking. They do not predict future performance.
5. **Single benchmark:** The S&P 500 is a reasonable but incomplete benchmark for bank-heavy portfolios. A financial sector index would be more appropriate.
6. **No factor analysis beyond CAPM:** A Fama-French 3-factor or 5-factor model would decompose alpha and beta into more granular exposures (value, size, momentum, quality, etc.).

### Next Steps (from the Original Roadmap)

These remain valid extensions:

- **Interactive dashboard:** Replace the HTML report with a live Streamlit or Gradio dashboard that accepts tickers, dates, and weights as user inputs.
- **Custom benchmarks:** Allow the user to specify any ticker as the benchmark (^GSPC, ^TNX, custom index).
- **Portfolio optimization:** Add Markowitz mean-variance optimization or risk-parity weighting as alternatives to equal weighting.
- **Monte Carlo simulation:** Simulate thousands of portfolio paths to generate probability distributions of outcomes, not just point estimates.
- **Factor model:** Decompose returns into Fama-French factors to understand *where* alpha is coming from.
- **Dynamic date ranges:** Support relative date inputs ("last 3 years", "YTD", "inception").

---

## 7. Summary Table

| Metric | What It Measures | Key Signal |
|---|---|---|
| Annualized Return | Total return compounded annually | Raw performance |
| Annualized Volatility | Return dispersion (standard deviation) | Total risk |
| Sharpe Ratio | Return per unit of total risk | Risk-adjusted performance |
| Sortino Ratio | Return per unit of downside risk | Downside-adjusted performance |
| Max Drawdown | Worst peak-to-trough loss | Peak pain |
| Calmar Ratio | Return per unit of max drawdown | Recovery-adjusted performance |
| Beta | Portfolio sensitivity to market | Market risk exposure |
| Alpha | Excess return above CAPM prediction | Manager skill / unexplained return |
| Treynor Ratio | Return per unit of market risk | Systematic-risk-adjusted performance |
| VaR (90/95/99) | Threshold loss at N% confidence | Tail risk threshold |
| CVaR (95) | Expected loss beyond VaR | Tail risk severity |
