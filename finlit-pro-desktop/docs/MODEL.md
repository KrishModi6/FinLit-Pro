# Model card: FinLit AI Predictor

This is the stock-prediction model FinLit Pro was built around. It was not designed for this app:
it is the owner's existing model, found in the earlier FinLit Pro code and connected here without
changing what it computes. This card says where it came from, what it takes in and puts out, what
was changed and why, and how its performance is measured. It makes no performance claims.

## Where it came from

| | |
| --- | --- |
| Source | `KrishModi6/finlit-pro-legacy`, `app.py`, the "AI Predictor" page (lines 2134 to 2688, Streamlit) |
| Related | The FinLit Pro website's `src/pages/simulator/AiPredictor.jsx` is a simpler GBM simulation. Its drift error is fixed in this app's Monte Carlo view (FIXLOG #1); it is not the prediction model. |
| Port | `finlit_pro/model/finlit_predictor.py` |
| Versions | **v1.0** (original, reproduced exactly) and **v1.1** (four documented corrections). v1.0 is the default. |

## What it does

| Component | Weight | Method |
| --- | --- | --- |
| Monte Carlo median | 40% | Normal daily log-return shocks with the window's mean and standard deviation, seed 42 |
| Regression trend | 30% | Least-squares line through the last 120 closes, extended to the horizon |
| EMA momentum | 30% | The EMA 12/26 gap applied to today's price over the horizon |
| Signal score | sets the verdict | Six signals (RSI, MACD, moving averages, Bollinger position, volume, momentum), each -2 to +2 |

Composite target = 0.4 x MC median + 0.3 x trend + 0.3 x EMA target. Verdict: STRONG BUY at a score
of 4 or more, BUY at 2, STRONG SELL at -4 or less, SELL at -2, otherwise HOLD. Full pseudocode is in
[ALGORITHMS.md](ALGORITHMS.md#2-the-finlit-ai-predictor-modelfinlit_predictorpy).

## Inputs

| Input | Value | Notes |
| --- | --- | --- |
| Price history | 730 calendar days of daily bars | Open, high, low, close, volume, adjusted for splits and dividends (as `yfinance history(period="730d")` returned) |
| Forecast horizon | 7, 14, 30, 60 or 90 trading days | The original's choices; nothing else is offered |
| Simulations | 500, 1,000, 5,000 or 10,000 | The original's choices |
| Random seed | 42 | Fixed in the original, so every run is reproducible |
| Minimum history | 60 sessions | Below this the model refuses to run and says why |

No fundamentals, no news, no other tickers, no macro data. The Prediction view lists these inputs
next to every forecast.

## Outputs

Verdict, composite target and expected change, the three component targets and their weights,
the simulated 10th to 90th percentile prices and the share of paths that end higher, the six
signals with their readings, and diagnostics (model agreement, regression R squared, RSI, MACD
histogram, volatility, mean daily return, sessions used). v1.0 also shows the original
"confidence %", labelled as a heuristic, not a probability.

## v1.0 and v1.1

v1.0 is checked against an independent transcription of the original code, loops and global random
generator included (`tests/test_model.py::test_v10_reproduces_the_original_model`), to 1e-9.

v1.1 changes exactly four things. Each is a defect in the original, not a new idea:

| # | Original (v1.0) | v1.1 | Why |
| --- | --- | --- | --- |
| 1 | RSI from plain 14-day rolling means (Cutler's RSI) | Wilder's smoothing | The RSI thresholds of 30 and 70 are defined for Wilder's RSI; charting platforms and the FinLit Pro website use it |
| 2 | "10-day" momentum used `closes[-10]`, nine sessions back | `closes[-11]` (and `closes[-31]` for 30 days) | Off by one |
| 3 | EMA momentum extrapolated linearly over the horizon | Decays with a 60-session half-life | Linear extrapolation turns a 3% gap into an implausible move at 60 to 90 days |
| 4 | "Confidence %" = 90 minus the models' disagreement | Reports the disagreement only | It read like a probability and was not one |

Everything else (simulation, regression, weights, thresholds, labels) is identical, and
`test_v11_changes_only_the_documented_parts` checks that.

## How it is measured, the way a fund would review a signal

The original reported no track record. `finlit_pro/model/evaluation.py` measures one on the loaded
ticker every time the model runs, and the Prediction view shows it beside the forecast.

* **Point in time.** At each past origin the model receives only the bars up to that date. A test
  (`test_walk_forward_is_point_in_time_and_scores_against_the_future`) checks that no later bar
  ever reaches it.
* **Out of sample.** Nothing is fitted, tuned or selected on the evaluation period. The model's
  parameters are the original's.
* **Non-overlapping** by default: origins step by the horizon, so outcomes are independent and the
  significance tests are not inflated. An overlapping option is offered and labelled as such.
* **Against baselines**, not in isolation: direction against always calling the majority direction,
  with a p-value; error against a no-change forecast (skill); ranking skill as an information
  coefficient with its t-statistic; the 10-90 band's coverage against the promised 80%; the
  probability of a rise against a constant base rate (Brier score).
* **As a position**: long/flat and long/short from the verdict, after a per-trade cost set in
  Settings, against buy-and-hold over the same periods (CAGR, Sharpe, maximum drawdown, exposure).
* **By verdict**: mean outcome and hit rate for each of the five labels, which shows whether a
  STRONG BUY has actually preceded better returns than a BUY.

Each metric that fails its comparison is flagged in the table. The research note uses the same
results: if the model shows no significant skill on the ticker, the note says so and gives its
verdict little weight.

**No results are quoted in this card.** They depend on the ticker, the horizon and the period, and
one stock's history is a small sample. Run the evaluation on the ticker in front of you and read
it there.

## Known limitations

* Technical inputs only: the model knows nothing about earnings, valuation, news or the market.
* One ticker at a time. A fund would test a signal across a universe of stocks, free of
  survivorship bias, with sector and market neutralisation; this app cannot.
* Normal shocks with a constant volatility understate crash risk; the percentile band is the
  model's, and its coverage on the ticker is the honest measure of it.
* Two years of history is a short window for estimating drift.
* A fixed seed makes results repeatable, not more accurate.

## Connecting another model (the integration point)

The Prediction view, the evaluation and the research note talk to models only through the
`PredictionModel` protocol in `finlit_pro/model/interface.py`. To add a model:

```python
# finlit_pro/model/my_model.py
import pandas as pd
from finlit_pro.model.interface import Forecast, InputSpec

class MyModel:
    key, name, version = "my-model-v1", "My model", "1.0"
    description = "What it does, in one paragraph."
    horizons = (5, 21, 63)               # trading days it supports
    simulations = (1,)                   # (1,) if it does not simulate
    lookback_calendar_days = 365         # history it needs before the first forecast
    bullish, bearish = ("BUY",), ("SELL",)   # verdict labels for the strategy test

    def input_spec(self, horizon, simulations):
        return [InputSpec("Price history", "365 calendar days", "Adjusted daily closes")]

    def predict(self, bars: pd.DataFrame, horizon: int, simulations: int, seed=42) -> Forecast:
        # Use ONLY `bars`. The evaluation passes history truncated at each origin date.
        p = float(bars["adjclose"].iloc[-1])
        target = p  # your forecast here
        return Forecast(self.name, self.version, bars.index[-1], horizon, p, target,
                        "BUY" if target > p else "SELL")
```

Then register it in `finlit_pro/model/registry.py`:

```python
from finlit_pro.model.my_model import MyModel
register(MyModel())
```

It appears in the Prediction view's model list, is evaluated the same way, and is cited in the
research note. Percentile bands, a probability of a rise, a signal score, components and signals are
all optional: the view shows what the model provides, and
`tests/test_gui.py::test_a_connected_model_plugs_in_without_other_changes` checks a model that
returns only a point forecast. A model that needs other data (fundamentals, another ticker) should
fetch it point in time inside `predict` from the dates in `bars`, never from today.
