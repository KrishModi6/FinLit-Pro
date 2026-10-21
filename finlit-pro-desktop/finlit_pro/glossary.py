"""Plain-language definitions for every term, ratio and value the app shows.

Hover over a label, a table row, a column heading, a verdict or a setting and
its definition appears: what it is, and how to read it. Help > Glossary (F1)
lists every term with a search box.

    tip("Sharpe ratio")   -> tooltip HTML for that label, or "" if unknown
    lookup("P/E (TTM)")   -> the Term, resolving the label through ALIASES

Labels are matched exactly (case-insensitive) against each term's name and its
aliases, then against a few families (P10, FY2024, Year 3, 10-K/A). Unknown
labels get no tooltip rather than a guess.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Term:
    name: str
    category: str
    meaning: str
    reading: str = ""
    aliases: tuple[str, ...] = field(default_factory=tuple)


SIGNALS = "Signals and charts"
RISK = "Returns and risk"
MODEL = "Prediction model"
EVAL = "Model evaluation"
MC = "Monte Carlo"
OPTIONS = "Options"
STATEMENTS = "Financial statements"
RATIOS = "Ratios"
QUALITY = "Quality scores"
DCF = "Valuation (DCF)"
FILINGS = "SEC filings"
DATA = "Data and sources"
NOTE = "Research note"

CATEGORIES = [SIGNALS, RISK, MODEL, EVAL, MC, OPTIONS, STATEMENTS, RATIOS, QUALITY, DCF, FILINGS, DATA, NOTE]

_TERMS: list[tuple[str, Term]] = [
    # ------------------------------------------------------------------ direction and verdicts
    ("bullish", Term("Bullish", SIGNALS,
        "Expecting or pointing to a rise in price. A bullish signal is evidence that buyers are in control; a bullish investor expects the stock to go up. The name comes from a bull, which strikes upward with its horns.",
        "Bullish describes a direction, not a certainty. Several independent bullish signals carry more weight than one. The opposite is bearish.",
        ("Bull", "Bullish crossover"))),
    ("bearish", Term("Bearish", SIGNALS,
        "Expecting or pointing to a fall in price. A bearish signal is evidence that sellers are in control; a bearish investor expects the stock to go down. The name comes from a bear, which swipes downward with its paws.",
        "Bearish describes a direction, not a certainty. The opposite is bullish.",
        ("Bear", "Bearish crossover"))),
    ("bull_market", Term("Bull market", SIGNALS,
        "A long period of rising prices, often defined as a rise of 20% or more from a recent low.",
        "Most stocks rise in a bull market, so a stock's gains then say less about the stock itself.")),
    ("bear_market", Term("Bear market", SIGNALS,
        "A long period of falling prices, often defined as a fall of 20% or more from a recent high.",
        "Correlations rise in bear markets: most stocks fall together, and diversification helps less than usual.")),
    ("strong_buy", Term("STRONG BUY", MODEL,
        "The prediction model's most bullish verdict: its six technical signals add up to +4 or more out of a possible +12.",
        "Check the out-of-sample evaluation below: the row for STRONG BUY shows what actually followed this verdict on this stock in the past.")),
    ("buy", Term("BUY", MODEL,
        "The prediction model's bullish verdict: its six signals add up to +2 or +3.",
        "A modest bullish lean from technical signals only. It ignores valuation, earnings and news.")),
    ("hold", Term("HOLD", MODEL,
        "The prediction model's neutral verdict: its six signals add up to between -1 and +1, so bullish and bearish evidence roughly cancel out.",
        "No technical edge either way. It does not mean the stock is fairly valued.")),
    ("sell", Term("SELL", MODEL,
        "The prediction model's bearish verdict: its six signals add up to -2 or -3.",
        "A modest bearish lean from technical signals only.")),
    ("strong_sell", Term("STRONG SELL", MODEL,
        "The prediction model's most bearish verdict: its six signals add up to -4 or less.",
        "Strongly negative technicals often follow a sharp fall; check the evaluation to see whether this verdict has preceded further falls on this stock or rebounds.")),
    ("verdict", Term("Verdict", MODEL,
        "The model's recommendation, from STRONG SELL to STRONG BUY, set by its signal score: +4 or more STRONG BUY, +2 BUY, -1 to +1 HOLD, -2 SELL, -4 or less STRONG SELL.",
        "The verdict comes from technical signals; the composite target comes from the price projections. They can disagree.")),
    ("signal_score", Term("Signal score", MODEL,
        "The sum of the six signals (RSI, MACD, moving averages, Bollinger position, volume, momentum), each scored from -2 (bearish) to +2 (bullish), so the total runs from -12 to +12.",
        "Above zero leans bullish, below zero bearish. The verdict thresholds are +4, +2, -2 and -4.",
        ("Score",))),

    # ------------------------------------------------------------------ technical signals
    ("rsi", Term("RSI (Relative Strength Index)", SIGNALS,
        "Compares the size of recent up days with recent down days over 14 sessions, on a 0 to 100 scale. 100 means every day was up; 0 means every day was down.",
        "Above 70 is called overbought (a fast rise that often pauses), below 30 oversold (a fast fall that often bounces), 40 to 60 neutral. In a strong trend RSI can stay overbought or oversold for weeks.",
        ("RSI", "RSI 14"))),
    ("overbought", Term("Overbought", SIGNALS,
        "A price that has risen so far, so fast, that a pause or pullback has become more likely than usual. Usually judged by RSI above 70 or a price at the upper Bollinger Band.",
        "A warning, not a sell signal on its own: strong uptrends stay overbought for long stretches.",
        ("Approaching overbought",))),
    ("oversold", Term("Oversold", SIGNALS,
        "A price that has fallen so far, so fast, that a bounce has become more likely than usual. Usually judged by RSI below 30 or a price at the lower Bollinger Band.",
        "A possible opportunity, not a buy signal on its own: falling knives can keep falling.",
        ("Approaching oversold",))),
    ("macd", Term("MACD", SIGNALS,
        "Moving Average Convergence Divergence. The MACD line is the 12-day exponential average of the price minus the 26-day one. The signal line is a 9-day average of the MACD line, and the histogram is the gap between the two.",
        "MACD above its signal line is bullish momentum, below it bearish. A crossover marks a change in momentum; a growing histogram means the move is accelerating.",
        ("MACD 12,26,9",))),
    ("macd_histogram", Term("MACD histogram", SIGNALS,
        "MACD line minus its signal line, drawn as bars.",
        "Positive and growing: upward momentum accelerating. Positive and shrinking: upward momentum fading. Negative works the same way downward.")),
    ("crossover", Term("Crossover", SIGNALS,
        "When one line crosses another: the MACD line crossing its signal line, or a short moving average crossing a long one.",
        "Crossing upward is read as bullish, downward as bearish. 'Accelerating' means the histogram is growing in the direction of the cross.",
        ("Bearish crossover, accelerating", "Bullish crossover, accelerating"))),
    ("moving_averages", Term("Moving averages (signal)", SIGNALS,
        "Compares today's price with its 20-day and 50-day simple moving averages.",
        "Price above the 20-day, which is above the 50-day, is an uptrend (+2). Price below the 20-day, which is below the 50-day, is a downtrend (-2). Mixed positions score in between.",
        ("Moving averages",))),
    ("sma", Term("SMA (simple moving average)", SIGNALS,
        "The average closing price over the last N sessions, recalculated every day. SMA 20 covers about a month, SMA 50 about a quarter, SMA 200 about a year.",
        "Price above its 200-day average is commonly read as a long-term uptrend. The 50-day crossing above the 200-day is called a golden cross (bullish), crossing below a death cross (bearish).",
        ("SMA 20", "SMA 50", "SMA 200"))),
    ("ema", Term("EMA (exponential moving average)", SIGNALS,
        "A moving average that gives more weight to recent prices, so it reacts faster than a simple average. EMA 12 and EMA 26 feed MACD and the model's momentum target.")),
    ("uptrend", Term("Uptrend", SIGNALS,
        "A sequence of higher highs and higher lows; here, price above its 20-day average, which is above its 50-day average.",
        "Trends tend to persist in the short run, which is why many signals follow them.",
        ("Uptrend: price > SMA20 > SMA50",))),
    ("downtrend", Term("Downtrend", SIGNALS,
        "A sequence of lower highs and lower lows; here, price below its 20-day average, which is below its 50-day average.",
        "",
        ("Downtrend: price < SMA20 < SMA50",))),
    ("bollinger", Term("Bollinger Bands", SIGNALS,
        "A 20-day moving average with bands two standard deviations above and below it. In calm conditions about 95% of closes fall between the bands. The position is where the price sits: 0% at the lower band, 100% at the upper.",
        "Near the upper band the price is stretched (above 95% scores -2); near the lower band it is depressed (below 5% scores +2). The bands widen when volatility rises.",
        ("Bollinger 20,2", "Bollinger Bands", "Bollinger"))),
    ("volume", Term("Volume", SIGNALS,
        "The number of shares traded in a session.",
        "Moves on heavy volume (well above the 20-day average) are more convincing than moves on light volume. Above 1.5 times average on an up day is a confirmed rally (+2); on a down day it is a high-volume selloff (-2).")),
    ("selloff", Term("High-volume selloff (distribution)", SIGNALS,
        "A down day on volume well above normal: many holders selling at once, which traders call distribution.",
        "Read as bearish, because it suggests large investors are leaving.",
        ("High-volume selloff", "Distribution"))),
    ("rally", Term("High-volume rally", SIGNALS,
        "An up day on volume well above normal: heavy buying.",
        "Read as bullish, because it suggests large investors are buying.",
        ("High volume rally",))),
    ("momentum", Term("Momentum", SIGNALS,
        "The percentage change in price over the last 10 and 30 sessions.",
        "Above +5% over 10 days and +10% over 30 scores +2; below -5% and -10% scores -2. Momentum tends to persist for weeks to months, then fade.")),
    ("candles", Term("Candlestick", SIGNALS,
        "Each candle shows one session: the body spans the open and the close, and the thin wicks reach the high and the low. Green means it closed above the open, red below.",
        "Long wicks show prices that were rejected during the day; long bodies show conviction.",
        ("Candles", "OHLC"))),
    ("line_chart", Term("Line chart", SIGNALS, "One point per session at the closing price. Used automatically when there are too many sessions for candles to stay readable.", "", ("Line",))),
    ("log_scale", Term("Log scale", SIGNALS,
        "A price axis on which equal distances are equal percentage moves: 10 to 20 is as tall as 100 to 200.",
        "Use it for long histories, where a linear axis makes early moves invisible.")),
    ("adjusted_close", Term("Adjusted close", DATA,
        "The closing price adjusted for dividends and stock splits, so that returns over time compare like with like.",
        "Returns, the prediction model and the Monte Carlo use adjusted closes. The chart shows the prices actually traded.")),
    ("last_price", Term("Last", DATA, "The latest traded price, delayed by up to 15 minutes during market hours.", "", ("Last price",))),
    ("change_pct", Term("Change on the day", DATA, "The percentage change from the previous session's close to the latest price.", "", ("Chg %", "Change on the day"))),
    ("range", Term("Date range", DATA,
        "The period the chart and the return and risk statistics cover. 1M to 10Y count back from the last session, YTD from 1 January, Max uses all history, and Custom uses the From and To dates.",
        "The prediction model, Monte Carlo and evaluation use their own lookbacks, not this range.",
        ("Range", "1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "10Y", "Max", "Custom", "From", "To"))),
    ("benchmark", Term("Benchmark", RISK,
        "The index or fund the stock is compared with. SPY, an exchange-traded fund that tracks the S&P 500, is the default.",
        "Beta, alpha, correlation and the capture ratios all measure the stock against this benchmark.",
        ("Default benchmark",))),
    ("risk_free_rate", Term("Risk-free rate", RISK,
        "The return on an investment with no default risk; here the yield on 13-week US Treasury bills (Yahoo symbol ^IRX).",
        "Sharpe and Sortino ratios measure return above this rate, and option prices depend on it.",
        ("Risk-free rate (%)", "Risk-free rate (no view)", "Fallback risk-free rate (%)"))),

    # ------------------------------------------------------------------ returns and risk
    ("total_return", Term("Total return", RISK,
        "The percentage gain or loss over the period, with dividends reinvested.",
        "Compare it with the benchmark's total return over the same period.")),
    ("cagr", Term("CAGR (compound annual growth rate)", RISK,
        "The steady yearly rate that would turn the starting value into the ending value. A stock that doubles in five years has a CAGR of about 14.9%.",
        "Smooths out the path, so two stocks with the same CAGR can have had very different rides. Pair it with volatility and drawdown.",
        ("CAGR",))),
    ("volatility", Term("Volatility (annualised)", RISK,
        "How much the price typically swings: the standard deviation of daily returns, scaled to a year by multiplying by the square root of 252.",
        "The S&P 500 runs at about 15 to 20%. Large, steady companies are often 20 to 30%, fast-growing or small companies 40% or more. A 30% volatility means a typical year lands within about 30% of its average.",
        ("Volatility (annualised)", "Volatility (annual)", "Volatility"))),
    ("sharpe", Term("Sharpe ratio", RISK,
        "Return above the risk-free rate, divided by volatility: how much extra return each unit of risk earned.",
        "Below 0: did worse than Treasury bills. 0.5 is ordinary, above 1 is good, above 2 is exceptional and rarely lasts. Compare stocks over the same period.",
        ("Sharpe",))),
    ("sortino", Term("Sortino ratio", RISK,
        "Like the Sharpe ratio, but it counts only downside volatility, so large up days are not treated as risk.",
        "Higher is better. A Sortino well above the Sharpe means much of the volatility was to the upside.")),
    ("max_drawdown", Term("Maximum drawdown", RISK,
        "The largest fall from a peak to a later low during the period, before a new high was reached.",
        "The loss someone who bought at the worst time would have sat through. Size positions so a drawdown like this would not force a sale.",
        ("Max drawdown", "Drawdown"))),
    ("time_under_water", Term("Longest time below a prior high", RISK,
        "The longest stretch, in calendar days, that the price stayed below a previous peak.",
        "Shows how long recovery took. Long stretches test patience as much as drawdowns test nerves.",
        ("Longest time below a prior high (days)",))),
    ("calmar", Term("Calmar ratio", RISK,
        "CAGR divided by maximum drawdown: return per unit of worst-case pain.",
        "Above 1 means the yearly return exceeded the worst fall; above 0.5 is respectable.")),
    ("var95", Term("1-day VaR 95% (value at risk)", RISK,
        "The daily loss that was exceeded on only 5% of days (one day in twenty), from the stock's own history.",
        "A VaR of 2.5% means that, on one day in twenty, the stock lost more than 2.5%. It says nothing about how much more: see CVaR.",
        ("1-day VaR 95% (historical)", "VaR 95", "VaR"))),
    ("var99", Term("1-day VaR 99%", RISK,
        "The daily loss exceeded on only 1% of days (about two and a half days a year).",
        "", ("1-day VaR 99% (historical)",))),
    ("cvar95", Term("CVaR 95% (expected shortfall)", RISK,
        "The average loss on the worst 5% of days, those beyond the VaR.",
        "Measures how bad the bad days are. Always at least as large as the VaR.",
        ("1-day CVaR 95%", "CVaR 95", "CVaR"))),
    ("parametric_var", Term("Parametric VaR", RISK, "VaR calculated from the average and volatility of returns assuming a normal bell curve, instead of from the actual worst days.", "It is usually smaller than historical VaR for stocks with fat tails.")),
    ("skew", Term("Skew of daily returns", RISK,
        "Whether big moves are more often up or down. Zero is symmetric.",
        "Negative skew: more large down days than large up days (crash-prone). Positive skew: occasional large jumps up.",
        ("Skew",))),
    ("kurtosis", Term("Excess kurtosis", RISK,
        "How fat the tails are: how often extreme days happen compared with a normal bell curve, which scores 0.",
        "Above 3 means extreme days are much more common than a normal model assumes, so normal-based risk numbers understate the danger.",
        ("Kurtosis",))),
    ("best_day", Term("Best day", RISK, "The largest one-day gain in the period.")),
    ("worst_day", Term("Worst day", RISK, "The largest one-day loss in the period.", "Compare it with VaR: the worst day is often several times the 95% VaR.")),
    ("up_days", Term("Up days", RISK, "The share of sessions that closed higher than the session before.", "Most stocks rise on 50 to 55% of days; the size of the moves matters more than the count.")),
    ("beta", Term("Beta", RISK,
        "How much the stock tends to move when the benchmark moves. A beta of 1.3 means it has typically moved about 1.3% for every 1% move in the market.",
        "Above 1: amplifies the market (more risk in a downturn). Below 1: more defensive. Near 0: moves independently. Negative: tends to move against the market.")),
    ("alpha", Term("Alpha (Jensen's, annualised)", RISK,
        "Return beyond what the stock's beta to the benchmark would explain, per year. Positive alpha means it beat the market after adjusting for the market risk it took.",
        "Noisy over short periods: a year of alpha says little about skill or the future.",
        ("Alpha (Jensen, annualised)", "Alpha"))),
    ("correlation", Term("Correlation", RISK,
        "How closely the stock's daily moves line up with the benchmark's, from -1 (always opposite) through 0 (unrelated) to +1 (always together).",
        "Low correlation means the stock adds diversification to a portfolio that holds the benchmark.")),
    ("r_squared", Term("R-squared", RISK, "The share of the stock's daily variation that the benchmark explains, from 0 to 1. It is the correlation squared.")),
    ("tracking_error", Term("Tracking error", RISK,
        "The volatility of the stock's return minus the benchmark's return.",
        "High tracking error means the stock often behaves very differently from the market.")),
    ("information_ratio", Term("Information ratio", RISK,
        "Return above the benchmark divided by tracking error: consistency of outperformance.",
        "Above 0.5 is good, above 1 rare.")),
    ("up_capture", Term("Up-market capture", RISK,
        "The stock's average return on days the benchmark rose, as a share of the benchmark's average return on those days.",
        "Above 1.0 (100%): it gains more than the market on good days.")),
    ("down_capture", Term("Down-market capture", RISK,
        "The stock's average return on days the benchmark fell, as a share of the benchmark's.",
        "Below 1.0: it falls less than the market on bad days. The best combination is high up-capture and low down-capture.")),
    ("cumulative_return", Term("Cumulative return", RISK, "The running total return since the start of the selected range, with dividends reinvested.", "", ("Cumulative return and drawdown",))),
    ("daily_returns", Term("Daily returns distribution", RISK,
        "A histogram of one-day returns over the range, with a normal bell curve of the same average and volatility drawn over it.",
        "Bars beyond the curve at the edges are the extreme days a normal model underestimates.",
        ("Daily returns",))),
    ("rolling_stats", Term("Rolling volatility and beta", RISK,
        "Volatility measured over a moving 63-session window (about a quarter), and beta over a moving 126-session window (about half a year).",
        "Shows how risk changes over time. A recent jump in volatility often follows news or earnings.",
        ("Rolling 63-day volatility and 126-day beta",))),
    ("monthly_returns", Term("Monthly returns", RISK, "Total return for each calendar month; the last column is the calendar year.")),
    ("stock_col", Term("Stock", RISK, "The figure for the loaded ticker.")),

    # ------------------------------------------------------------------ prediction model
    ("finlit_predictor", Term("FinLit AI Predictor", MODEL,
        "The owner's stock-prediction model from the original FinLit Pro app. It blends three price projections (a Monte Carlo median, a regression trend and an EMA momentum target) into a composite target, and scores six technical signals into a verdict.",
        "v1.0 is the original, unchanged. v1.1 fixes four documented defects. Both use price history only.",
        ("FinLit AI Predictor v1.0", "FinLit AI Predictor v1.1", "FinLit AI Predictor v1.0 (original)", "FinLit AI Predictor v1.1 (corrected)", "Model"))),
    ("composite_target", Term("Composite target", MODEL,
        "The model's point forecast for the price at the horizon: 40% Monte Carlo median, 30% regression trend, 30% EMA momentum target.",
        "One number from a wide range of possible outcomes. The percentiles and the evaluation show how uncertain it is.",
        ("Target",))),
    ("expected_change", Term("Expected change", MODEL, "The composite target compared with today's price, in percent.")),
    ("prob_rise", Term("P(rise), simulated", MODEL,
        "The share of the model's simulated price paths that finish above today's price.",
        "It is the model's own estimate. The Brier score in the evaluation shows whether such estimates have been reliable on this stock.",
        ("Probability of a rise",))),
    ("model_agreement", Term("Model agreement", MODEL,
        "How close the three component targets are to each other: High if their spread is under 2% of the price, Medium under 5%, otherwise Low.",
        "Low agreement means the components point in different directions, so the composite target is less settled.")),
    ("model_spread", Term("Model spread", MODEL,
        "The disagreement between the three component targets: their standard deviation as a share of the price, or the gap between the highest and lowest in dollars.",
        "", ("Model spread (% of price)", "Model spread ($)"))),
    ("mc_component", Term("Monte Carlo median (component)", MODEL,
        "The median final price across the model's simulated paths, which draw daily returns from a normal distribution with the stock's recent average and volatility. Weight 40%.",
        "", ("Monte Carlo median",))),
    ("regression_trend", Term("Regression trend", MODEL,
        "A straight line fitted through the last 120 closes and extended to the horizon. Weight 30%.",
        "Assumes the recent trend continues in a straight line. The R-squared says how well a line fits.")),
    ("regression_r2", Term("Regression R-squared", MODEL,
        "How well a straight line fits the last 120 closes, from 0 (no trend) to 1 (a perfect line).",
        "Below about 0.3 the trend component is mostly noise.",
        ("Regression R2",))),
    ("ema_momentum", Term("EMA momentum target", MODEL,
        "Today's price moved by the gap between the 12-day and 26-day exponential averages, projected over the horizon. Weight 30%. v1.0 extrapolates the gap in a straight line; v1.1 lets it fade with a 60-session half-life.",
        "", ("EMA momentum",))),
    ("confidence_pct", Term("Confidence % (original heuristic)", MODEL,
        "The original model's 'confidence': 90, 75 or 60 minus the spread between its components. Shown in v1.0 for completeness.",
        "It is not a probability of anything. Use the out-of-sample evaluation to judge the model.",
        ("Confidence % (original heuristic, not a probability)",))),
    ("forecast_horizon", Term("Forecast horizon", MODEL,
        "How far ahead the forecast looks, in trading days. About 21 trading days make a month, 63 a quarter and 252 a year.",
        "", ("Horizon",))),
    ("simulations", Term("Simulations", MC,
        "The number of simulated price paths. More paths make the percentiles more stable, not more accurate.",
        "", ("Simulations (paths)", "Paths"))),
    ("random_seed", Term("Random seed", MC,
        "A starting number for the random generator. The same seed reproduces exactly the same paths.",
        "Changing it shows how much of a result is sampling noise.",
        ("Seed",))),
    ("regression_window", Term("Regression window", MODEL, "The number of recent closes the trend line is fitted through: 120 sessions, about six months.")),
    ("indicators", Term("Indicators", MODEL, "The technical indicators the model computes from prices: moving averages, Bollinger Bands, RSI, MACD and average volume.")),
    ("component_weights", Term("Component weights", MODEL, "How the three projections are blended into the composite target: 40% Monte Carlo median, 30% regression trend, 30% EMA momentum.", "", ("Weight",))),
    ("minimum_history", Term("Minimum history", MODEL, "The fewest sessions of price history the model accepts. With less, it refuses to run and says why.")),
    ("price_history_input", Term("Price history (model input)", MODEL,
        "The data the model reads: the last 730 calendar days of daily open, high, low, close and volume, adjusted for splits and dividends. Nothing else: no earnings, valuation or news.",
        "", ("Price history",))),
    ("sessions_used", Term("Sessions used", MODEL, "How many trading sessions of history the model actually used.")),
    ("mean_log_return", Term("Mean daily log return", MODEL,
        "The average daily return over the model's window, in continuously compounded (logarithmic) form. 0.001 is about 0.1% a day, or roughly 29% a year.",
        "The least reliable input in finance: a strong run inflates it, and the simulation projects it forward.")),
    ("mc_mean", Term("Monte Carlo mean", MODEL, "The average final price across the simulated paths. It sits above the median because prices are skewed: they can rise without limit but fall only to zero.")),
    ("percentile", Term("Percentile", MC,
        "P10 is the price that 10% of simulated outcomes fall below; P50 is the median, the middle outcome; P90 is the price only 10% of outcomes exceed.",
        "P10 to P90 is the range that holds the middle 80% of outcomes under the model's assumptions.",
        ("Percentiles", "Percentile"))),
    ("forecast_range", Term("Forecast range (fan chart)", MODEL,
        "The recent price, then the model's simulated 10 to 90 and 25 to 75 percentile bands widening to the horizon, with the median path and the composite target.",
        "", ("Forecast range",))),
    ("component", Term("Component", MODEL, "One of the three price projections the composite target blends.")),
    ("signal", Term("Signal", MODEL, "One of the six technical tests the model scores from -2 (bearish) to +2 (bullish).", "", ("Signals",))),
    ("reading", Term("Reading", MODEL, "What the signal currently shows, in words, with the value it was judged on.")),
    ("diagnostic", Term("Diagnostic", MODEL, "Intermediate numbers the model computed, shown so its output can be checked.")),
    ("model_inputs", Term("Inputs", MODEL, "Everything the model reads, and every fixed setting it uses.", "", ("Input",))),
    ("model_outputs", Term("Outputs", MODEL, "Everything the model produces: its component targets, their weights, the composite target and the simulated percentiles.")),

    # ------------------------------------------------------------------ evaluation
    ("walk_forward", Term("Out-of-sample (walk-forward) evaluation", EVAL,
        "A replay of the model through the stock's past. At each origin date the model sees only the prices up to that day, makes its forecast, and is scored on what actually happened next. Nothing is tuned on the results.",
        "This is how a fund checks a signal before trusting it. A model that cannot beat simple baselines here has no demonstrated edge on this stock.",
        ("Out-of-sample evaluation",))),
    ("origins", Term("Origins", EVAL,
        "The past dates the evaluation forecasts from. Non-overlapping steps by the horizon, so each outcome is independent. Every 5 sessions gives more forecasts, but neighbouring outcomes overlap, which overstates significance.",
        "", ("Non-overlapping (step = horizon)", "Every 5 sessions (overlapping)"))),
    ("hit_rate", Term("Directional hit rate", EVAL,
        "The share of past forecasts that got the direction (up or down) right.",
        "Compare it with always calling the more common direction: stocks rise more often than they fall, so 55% may be no better than always saying 'up'.",
        ("Hit rate",))),
    ("p_value", Term("Hit-rate p-value", EVAL,
        "The chance of a hit rate at least this high from a model with no real edge over the naive call, by luck alone.",
        "Below 0.05 is conventionally called significant. Above it, the hit rate could easily be luck.")),
    ("mae", Term("Mean absolute error", EVAL,
        "The average size of the miss between the forecast price and the actual price, as a share of the starting price.",
        "Compare it with the no-change forecast's error; on its own it mostly measures how volatile the stock is.")),
    ("skill", Term("Skill vs no-change", EVAL,
        "1 minus the model's average error divided by the error of simply forecasting no change.",
        "Positive: more accurate than assuming the price stays put. Zero or negative: no better, or worse. Few price-only models achieve meaningful positive skill.")),
    ("rmse", Term("Root mean squared error", EVAL, "Like mean absolute error, but large misses count more.")),
    ("ic", Term("Information coefficient (IC)", EVAL,
        "The rank correlation between forecast returns and actual returns: whether bigger predicted gains were followed by bigger actual gains.",
        "Funds treat a steady IC of 0.05 or more as useful. Near zero or negative: the forecasts did not rank outcomes.",
        ("Information coefficient", "IC"))),
    ("ic_t", Term("IC t-statistic", EVAL,
        "How many standard errors the information coefficient is from zero.",
        "Beyond plus or minus 2, the IC is unlikely to be luck; inside that range it could be.")),
    ("band_coverage", Term("10-90 band coverage", EVAL,
        "How often the actual outcome landed inside the model's 10th to 90th percentile range.",
        "A well-calibrated band covers about 80%. Much less: the model was overconfident (band too narrow). Much more: too cautious.",
        ("Coverage",))),
    ("brier", Term("Brier score", EVAL,
        "The average squared error of the model's probability of a rise, where each outcome counts as 1 (rose) or 0 (fell). 0 is perfect; 0.25 is what always saying 50% scores.",
        "Lower is better. Compare it with the constant base-rate figure: if the model is not lower, its probabilities add nothing.",
        ("Brier score (P up)",))),
    ("long_flat", Term("Long/flat strategy", EVAL,
        "Own the stock for the horizon after each BUY or STRONG BUY verdict, hold cash otherwise, paying the transaction cost set in Settings on every change.",
        "Compare its CAGR, Sharpe and drawdown with buy and hold over the same periods.",
        ("Long/flat", "Long/flat CAGR", "Long/flat Sharpe", "Long/flat max drawdown"))),
    ("long_short", Term("Long/short strategy", EVAL,
        "Own the stock after bullish verdicts, bet against it (short) after SELL or STRONG SELL, and hold cash after HOLD.",
        "Shorting profits from falls but loses without limit on rises; this tests whether the bearish verdicts add value.",
        ("Long/short", "Long/short CAGR", "Long/short Sharpe", "Long/short max drawdown"))),
    ("buy_and_hold", Term("Buy and hold", EVAL,
        "Simply owning the stock through every evaluation period: the baseline any strategy has to beat.",
        "", ("Buy and hold CAGR", "Buy and hold Sharpe", "Buy and hold max drawdown"))),
    ("exposure", Term("Exposure", EVAL,
        "The share of periods the strategy held a position.",
        "A strategy that is invested half the time can have a lower CAGR than buy and hold yet a better Sharpe.",
        ("Long/flat exposure", "Long/short exposure"))),
    ("forecasts", Term("Forecasts", EVAL, "How many past forecasts fall in this row.")),
    ("mean_outcome", Term("Mean outcome", EVAL, "The average actual return over the horizon after forecasts with this verdict.", "If STRONG BUY rows are not followed by better outcomes than STRONG SELL rows, the verdicts are not ranking anything.")),
    ("mean_forecast", Term("Mean forecast", EVAL, "The average return the model predicted for forecasts in this row.")),
    ("compare_with", Term("Compare with", EVAL, "The baseline or rule of thumb the metric should be judged against.")),
    ("assessment", Term("Assessment", EVAL, "A warning when the metric fails its comparison. Blank means it passed.")),
    ("growth_of_1", Term("Growth of 1", EVAL, "What 1 dollar would have become following each strategy, on a log scale so that equal heights are equal percentage changes.")),

    # ------------------------------------------------------------------ Monte Carlo
    ("monte_carlo", Term("Monte Carlo simulation", MC,
        "Thousands of possible future price paths, each built from random daily returns that follow the chosen assumptions. The spread of where they end is a picture of the uncertainty.",
        "It shows what happens if prices behave like the model. Real prices are not obliged to: crashes, earnings jumps and regime changes fall outside these ranges more often than the model implies.",
        ("Monte Carlo",))),
    ("mc_horizon", Term("Horizon (trading days)", MC, "How far ahead to simulate. 21 trading days is about a month, 63 a quarter, 252 a year, 504 two years.")),
    ("lookback", Term("Lookback (years)", MC, "How much history the volatility and drift are estimated from.", "Longer lookbacks are steadier but slower to react to a change in the stock.")),
    ("return_distribution", Term("Return distribution", MC,
        "How the random daily returns are drawn. Normal (GBM): a bell curve, the textbook model. Fat tails (Student-t): more extreme days, matched to the stock's own history. Historical bootstrap: real past returns resampled in 10-day blocks.",
        "Fat tails or bootstrap give a more honest picture of crash risk than the normal model.",
        ("Normal (GBM)", "Fat tails (Student-t)", "Historical bootstrap"))),
    ("gbm", Term("GBM (geometric Brownian motion)", MC, "The standard textbook model of a stock price: normally distributed daily returns with constant volatility. It is the basis of Black-Scholes.", "It understates how often extreme days happen.")),
    ("student_t", Term("Student-t (fat tails)", MC, "A bell-shaped distribution with fatter tails than the normal one, so extreme days are more common. Its degrees of freedom are matched to the stock's excess kurtosis.", "Lower degrees of freedom mean fatter tails; 30 or more is close to normal.", ("t df", "Degrees of freedom"))),
    ("bootstrap", Term("Historical bootstrap", MC, "Simulated paths built by stitching together random 10-day blocks of the stock's actual past returns, so real crashes and rallies recur.", "It cannot produce anything worse than history contains.")),
    ("drift", Term("Drift", MC,
        "The average return the simulation assumes. Historical drift uses the stock's past average; zero expected return assumes the typical path goes nowhere; custom uses the annual return you enter.",
        "Past drift is the least reliable input: a strong run inflates every simulated path. Zero drift isolates pure risk.",
        ("Historical drift", "Zero expected return", "Custom expected return"))),
    ("expected_return_input", Term("Expected return (% per year)", MC,
        "Your view of the stock's average yearly return, used when drift is Custom and in the options calculator.",
        "Long-run stock market returns have averaged around 7 to 10% a year.",
        ("Expected return", "Expected return used"))),
    ("vol_override", Term("Volatility override (% per year)", MC, "A volatility to use instead of the one estimated from history. Leave it blank to use the estimate.", "Use it to stress-test: what if volatility doubles?")),
    ("median_outcome", Term("Median outcome", MC, "The middle simulated final price: half the paths end above it, half below.")),
    ("p10_p90", Term("10th to 90th percentile", MC, "The range holding the middle 80% of simulated final prices, and its width as a share of today's price.", "", ("Monte Carlo 10th to 90th",))),
    ("paths_above", Term("Paths above today", MC, "The share of simulated paths that end above today's price.")),
    ("mc_var", Term("VaR 95 / CVaR 95 (horizon)", MC,
        "Over the whole horizon: the loss that only 5% of simulated paths exceed (VaR), and the average loss across those worst 5% (CVaR).",
        "", ("VaR 95 / CVaR 95",))),
    ("mean_path_drawdown", Term("Mean path drawdown", MC, "The average of each simulated path's largest peak-to-trough fall along the way.", "Even paths that end higher usually suffer a fall like this on the way, which is what tests whether you hold on.")),
    ("p_up_down_20", Term("P(+20%) / P(-20%)", MC, "The share of simulated paths that end at least 20% above today, and at least 20% below.")),
    ("vol_used", Term("Volatility used", MC, "The annual volatility the simulation actually used: the estimate from the lookback, or your override.")),
    ("calibration", Term("Calibration", MC,
        "A test on the stock's own history: at past dates the model is fitted on the data available then, and the app records where the actual price ended up within the forecast distribution.",
        "If the 10-90 band caught about 80% of outcomes, the model was honest about its uncertainty on this stock. Uniform bars in the histogram mean well calibrated; tall bars at the edges mean the bands were too narrow.",
        ("Calibration on this stock's history",))),
    ("band", Term("Band", MC, "A percentile range, such as 10-90: the range a calibrated model should catch the outcome inside 80% of the time.")),
    ("nominal", Term("Nominal", MC, "How often the band should contain the outcome if the model is right.")),
    ("observed", Term("Observed", MC, "How often the band actually contained the outcome in the historical test.")),
    ("mean_row", Term("Mean", MC, "The average simulated final price. It is above the median because prices can rise without limit but cannot fall below zero.")),
    ("assumptions_mc", Term("Assumptions and uncertainty", MC, "What the simulation takes for granted. Each assumption is a way the real outcome can differ from the simulated range.")),
    ("mc_fan", Term("Outcome range over the horizon", MC, "The recent price, then the simulated 5-95, 10-90 and 25-75 percentile bands widening to the horizon, with the median and a sample of individual paths.", "The bands widen with time because uncertainty compounds.")),
    ("mc_distribution", Term("Distribution at the horizon", MC, "A histogram of the simulated final prices: red bars end below today's price, green above, with lines at the 5th, 50th and 95th percentiles.", "A long right tail is normal for prices, which can rise without limit but cannot fall below zero.")),

    # ------------------------------------------------------------------ options
    ("option", Term("Option", OPTIONS,
        "A contract giving the right, not the obligation, to buy (a call) or sell (a put) 100 shares at a fixed price (the strike) until a set date (the expiry). The buyer pays a premium for that right.",
        "", ("Option chain",))),
    ("call", Term("Call", OPTIONS,
        "The right to buy 100 shares at the strike price until expiry. A call gains value when the stock rises.",
        "Buying a call is a bullish bet with a loss limited to the premium.",
        ("Calls",))),
    ("put", Term("Put", OPTIONS,
        "The right to sell 100 shares at the strike price until expiry. A put gains value when the stock falls.",
        "Buying a put is a bearish bet or insurance on shares you own.",
        ("Puts",))),
    ("strike", Term("Strike", OPTIONS, "The price at which the option lets you buy (call) or sell (put) the shares.")),
    ("expiry", Term("Expiry", OPTIONS, "The last day the option can be used. After it, an option that is not in the money is worth nothing.", "Short-dated options lose value fastest (see theta).", ("Expiration",))),
    ("premium", Term("Premium", OPTIONS,
        "The price of the option, quoted per share. One contract covers 100 shares, so a premium of 2.50 costs 250 dollars per contract.",
        "", ("Premium per share", "Premium (position)"))),
    ("contracts", Term("Contracts", OPTIONS, "How many option contracts. Each covers 100 shares.")),
    ("long_short_position", Term("Buy (long) / Sell (short)", OPTIONS,
        "Buying (long) pays the premium for the right; the most you can lose is the premium. Selling (short) collects the premium and takes on the obligation; a short call's loss has no limit.",
        "", ("Buy (long)", "Sell (short)", "Position"))),
    ("bid", Term("Bid", OPTIONS, "The highest price a buyer is currently offering. Selling at market gets roughly this.")),
    ("ask", Term("Ask", OPTIONS, "The lowest price a seller is currently asking. Buying at market pays roughly this.")),
    ("mid", Term("Mid", OPTIONS, "Halfway between bid and ask: a fair estimate of the option's price when there is no recent trade.", "A wide gap between bid and ask means the option is illiquid and costly to trade.")),
    ("last_trade", Term("Last (option)", OPTIONS, "The price of the most recent trade, which may be hours old for thinly traded contracts.")),
    ("iv", Term("Implied volatility (IV)", OPTIONS,
        "The volatility that, put into the Black-Scholes model, reproduces the option's market price. It is the market's estimate of how much the stock will move until expiry.",
        "IV above the stock's historical volatility means options are expensive relative to past movement, often before earnings. 'IV (Yahoo)' is Yahoo's figure; the calculator also computes its own from the premium.",
        ("IV (Yahoo)", "Implied volatility (from premium)", "Implied (market)", "Implied volatility"))),
    ("historical_vol", Term("Historical volatility", OPTIONS,
        "Volatility measured from the stock's past daily returns over the last year or the last three months.",
        "The 3-month figure reacts faster to recent turbulence.",
        ("Historical, 1 year", "Historical, 3 months"))),
    ("vol_source", Term("Volatility source", OPTIONS, "Which volatility 'your assumptions' use: historical over one year or three months, the market's implied volatility, or your own figure.")),
    ("volatility_input", Term("Volatility (% per year)", OPTIONS, "The annual volatility used for your assumptions.", "Higher volatility raises the value of every option, calls and puts alike.")),
    ("open_interest", Term("Open interest", OPTIONS, "The number of contracts currently open (not yet closed or expired).", "Higher open interest means a more liquid, more reliably priced contract.", ("Open int.",))),
    ("option_volume", Term("Volume (options)", OPTIONS, "Contracts traded today.")),
    ("itm", Term("In the money (ITM)", OPTIONS,
        "A call is in the money when the stock is above the strike; a put when it is below. At expiry, an in-the-money option is worth the difference.",
        "Strikes highlighted in the chain are currently in the money.",
        ("In the money",))),
    ("p_itm", Term("P(ITM)", OPTIONS,
        "The probability that the option finishes in the money at expiry, under each scenario's assumptions.",
        "Finishing in the money is not the same as profiting: the stock must also cover the premium (see breakeven).")),
    ("p_profit", Term("P(profit)", OPTIONS,
        "The probability that the position makes money at expiry: for a bought call, that the stock ends above the breakeven.",
        "Bought options often have a low probability of profit but a large payoff when they win; expected value weighs both.")),
    ("breakeven", Term("Breakeven at expiry", OPTIONS, "The stock price at expiry at which the position neither gains nor loses: strike plus premium for a call, strike minus premium for a put.", "", ("Breakeven",))),
    ("ev", Term("Expected value (EV)", OPTIONS,
        "The probability-weighted average profit or loss of the position at expiry, after the premium, in today's dollars.",
        "Positive EV under your assumptions means the option is cheap if your view of volatility and return is right.",
        ("EV / share", "EV / position"))),
    ("fair_value", Term("Fair value", OPTIONS, "The premium at which the expected value would be exactly zero under the scenario's assumptions.", "Fair value above the premium: cheap. Below: expensive.")),
    ("scenario", Term("Scenario", OPTIONS, "A set of assumptions about volatility and return under which the probabilities and expected value are calculated.")),
    ("market_implied", Term("Market-implied", OPTIONS,
        "The scenario that uses the option's own implied volatility and a risk-neutral return. Under it a fairly priced option has an expected value of zero by construction.",
        "It shows what the market's price assumes, not whether the option is worth buying.")),
    ("your_assumptions", Term("Your assumptions", OPTIONS,
        "The scenario that uses your volatility and expected return. The worth-it verdict comes from this row.",
        "The verdict is only as good as your assumptions are better than the market's.")),
    ("fat_tailed_mc", Term("Fat-tailed Monte Carlo", OPTIONS, "The same calculation over simulated prices with fat tails (Student-t), as a check on the lognormal formula.", "Real prices have more extreme days than the lognormal formula assumes; if this row disagrees sharply with Your assumptions, tail moves drive the result.", ("Also simulate fat tails (Student-t Monte Carlo)",))),
    ("worth_it", Term("Worth it", OPTIONS,
        "Under your assumptions, the position's expected value is at least 5% of the premium in your favour: the option is priced cheaply for buying (or richly for selling).",
        "It is a recommendation for your own decision, and only as good as your volatility and return assumptions.")),
    ("marginal", Term("Marginal", OPTIONS, "The expected value is within 5% of the premium: the price is close to fair under your assumptions, within the noise of the volatility estimate.")),
    ("not_worth_it", Term("Not worth it", OPTIONS, "Under your assumptions, the position's expected value is negative by more than 5% of the premium: you would be overpaying (or underselling).")),
    ("black_scholes", Term("Black-Scholes model", OPTIONS, "The standard formula for an option's fair price from the stock price, strike, time to expiry, interest rate, dividend yield and volatility.", "It assumes lognormal prices and constant volatility, which real markets bend.", ("Model price at your volatility",))),
    ("greeks", Term("Greeks", OPTIONS, "Sensitivities of the option's value: delta (to the stock price), gamma (how delta changes), theta (to time), vega (to volatility) and rho (to interest rates). Shown for the whole position.", "", ("Greek (position)",))),
    ("delta", Term("Delta", OPTIONS,
        "How much the position's value changes, in dollars, when the stock rises 1 dollar. For one contract it is shown per 100 shares.",
        "A delta of 50 behaves like owning 50 shares. Call deltas run from 0 to 100 per contract, put deltas from -100 to 0. Delta is also a rough probability of finishing in the money.")),
    ("gamma", Term("Gamma", OPTIONS, "How much delta changes when the stock rises 1 dollar.", "High gamma (near the strike, close to expiry) means the position's exposure shifts quickly.")),
    ("theta", Term("Theta (per day)", OPTIONS,
        "How much value the position loses each calendar day from the passage of time, all else equal.",
        "Negative for bought options: time decay works against the buyer and for the seller, and speeds up near expiry.",
        ("Theta / day", "Theta"))),
    ("vega", Term("Vega (per volatility point)", OPTIONS, "How much the position's value changes when implied volatility rises one percentage point.", "Bought options gain when volatility rises; implied volatility often falls after earnings, which hurts buyers.", ("Vega / 1 vol pt", "Vega"))),
    ("rho", Term("Rho (per rate point)", OPTIONS, "How much the position's value changes when interest rates rise one percentage point.", "Usually small, except for long-dated options.", ("Rho / 1 pt", "Rho"))),
    ("max_profit", Term("Max profit", OPTIONS, "The most the position can make at expiry. A bought call's maximum profit is unlimited.", "", ("Max profit (position)",))),
    ("max_loss", Term("Max loss", OPTIONS, "The most the position can lose at expiry. For a bought option it is the premium paid; for a sold call it is unlimited.", "", ("Max loss (position)",))),
    ("underlying", Term("Underlying", OPTIONS, "The stock the option is on, and its current price.")),
    ("days_to_expiry", Term("Days to expiry", OPTIONS, "Calendar days until the option expires.")),
    ("dividend_yield_options", Term("Dividend yield (options)", OPTIONS, "The stock's yearly dividends as a share of its price, used in pricing because dividends lower the expected future share price.", "", ("Dividend yield (%)",))),
    ("payoff_chart", Term("Payoff chart", OPTIONS, "Profit or loss of the position at expiry for each possible stock price, with the distribution of prices under your assumptions shaded behind it.")),

    # ------------------------------------------------------------------ statements
    ("revenue", Term("Revenue", STATEMENTS, "Total sales of goods and services in the period, before any costs. Also called the top line.", "Growth in revenue is the raw material for growth in profit.", ("Sales",))),
    ("gross_profit", Term("Gross profit", STATEMENTS, "Revenue minus the direct cost of producing what was sold.", "Gross margin (gross profit / revenue) shows pricing power: software often above 70%, retailers 20 to 40%.")),
    ("operating_income", Term("Operating income (EBIT)", STATEMENTS, "Profit from the business itself: gross profit minus operating costs such as research, sales and administration, before interest and taxes.", "", ("Operating income", "EBIT"))),
    ("net_income", Term("Net income", STATEMENTS, "Profit after every cost, interest and tax: the bottom line that belongs to shareholders.")),
    ("eps", Term("Diluted EPS (earnings per share)", STATEMENTS, "Net income divided by the share count including stock options and convertibles that could become shares.", "Restated here for stock splits so years compare like with like.", ("Diluted EPS", "EPS"))),
    ("ocf", Term("Operating cash flow", STATEMENTS, "Cash the business actually generated from operations in the period, after paying suppliers, staff and taxes.", "Consistently above net income suggests high-quality earnings.")),
    ("capex", Term("Capital expenditure (capex)", STATEMENTS, "Cash spent on long-lived assets such as factories, equipment and data centres.", "", ("Capital expenditure",))),
    ("fcf", Term("Free cash flow (FCF)", STATEMENTS, "Operating cash flow minus capital expenditure: cash left over that could be paid to shareholders, used for buybacks, or reinvested.", "The basis of the DCF valuation.", ("Free cash flow", "FCF"))),
    ("rnd", Term("Research and development", STATEMENTS, "Spending on developing new products and technology, counted as an expense.")),
    ("sbc", Term("Stock-based compensation", STATEMENTS, "Pay given to employees in shares or options. It is a real cost to shareholders (it dilutes them) but is added back in operating cash flow.", "Above about 8% of revenue it flatters cash flow noticeably.")),
    ("dividends_paid", Term("Dividends paid", STATEMENTS, "Cash paid to shareholders as dividends in the year.")),
    ("buybacks", Term("Share repurchases (buybacks)", STATEMENTS, "Cash spent buying back the company's own shares, which reduces the share count.", "", ("Share repurchases",))),
    ("cash", Term("Cash and equivalents", STATEMENTS, "Cash and very short-term, safe investments the company holds.")),
    ("total_debt", Term("Total debt", STATEMENTS, "All borrowing: long-term debt including the part due within a year, plus short-term borrowings. Counted once, without double counting overlapping XBRL tags.")),
    ("equity", Term("Shareholders' equity", STATEMENTS, "Assets minus liabilities: the accounting value belonging to shareholders, also called book value.", "Large buybacks can push it very low, which inflates return on equity.", ("Equity", "Book value"))),
    ("total_assets", Term("Total assets", STATEMENTS, "Everything the company owns or is owed, at accounting value.")),
    ("diluted_shares", Term("Diluted shares", STATEMENTS, "The average share count for the year, including shares that options and convertibles could create.")),
    ("fiscal_year", Term("Fiscal year (FY)", STATEMENTS, "The company's accounting year, which may not match the calendar year. FY2025 is the fiscal year ending in 2025 (Apple's ends in late September).", "Hover over a value to see the filing it came from; double-click to open it.")),
    ("ttm", Term("TTM (trailing twelve months)", STATEMENTS, "The most recent four quarters added together: the latest fiscal year plus the year-to-date from the latest 10-Q, minus the same period a year earlier.", "More current than the last annual report.", ("Trailing twelve months",))),
    ("annual_statements", Term("Annual statements", STATEMENTS, "Ten fiscal years of figures from the company's 10-K filings, taken from the SEC's XBRL data. Where a later filing restated a year, the restated figure is shown.", "", ("Results by fiscal year",))),
    ("margins", Term("Margins", STATEMENTS, "Profit as a share of revenue at each level: gross, operating, net, and free cash flow.", "Rising margins mean each dollar of sales is producing more profit.", ("Gross", "Operating", "Net"))),

    # ------------------------------------------------------------------ ratios
    ("market_cap", Term("Market capitalisation", RATIOS, "Share price times shares outstanding: what the stock market values the whole company at.", "Large cap above about 10 billion dollars, mid cap 2 to 10 billion, small cap below.", ("Market cap",))),
    ("enterprise_value", Term("Enterprise value (EV)", RATIOS, "Market cap plus debt minus cash: the price of buying the whole business, debts included.", "Compares companies with different amounts of debt fairly.", ("EV", "Enterprise value"))),
    ("pe", Term("P/E (price to earnings, TTM)", RATIOS,
        "Share price divided by earnings per share over the last twelve months (here market cap / net income): how many years of current profit the price pays for.",
        "The S&P 500 has averaged around 15 to 20. High P/E: the market expects strong growth (or profits are temporarily low). Low P/E: cheap, or the market expects trouble. Not meaningful when earnings are negative.",
        ("P/E (TTM)", "P/E", "PE"))),
    ("ev_ebit", Term("EV / EBIT", RATIOS,
        "Enterprise value divided by operating income: the price of the whole business per dollar of operating profit, unaffected by how it is financed.",
        "Below about 10 is often called cheap, above 25 expensive, but growth and industry matter.",
        ("EV/EBIT",))),
    ("ps", Term("P/S (price to sales)", RATIOS, "Market cap divided by revenue.", "Useful for companies without profits yet; compare within an industry.")),
    ("fcf_yield", Term("FCF yield", RATIOS,
        "Free cash flow divided by market cap: the cash return the business generates on its current price.",
        "Above 5 to 6% is attractive for a steady business; below 2% means the price relies on strong growth. Compare it with the Treasury yield.")),
    ("dividend_yield", Term("Dividend yield", RATIOS, "Dividends paid over the last twelve months divided by the share price.", "A very high yield can signal a dividend at risk of being cut.")),
    ("gross_margin", Term("Gross margin", RATIOS, "Gross profit as a share of revenue.", "Shows pricing power and production efficiency; compare within an industry.")),
    ("operating_margin", Term("Operating margin", RATIOS, "Operating income as a share of revenue.", "Above 20% is strong for most industries.")),
    ("net_margin", Term("Net margin", RATIOS, "Net income as a share of revenue.")),
    ("roic", Term("ROIC (return on invested capital)", RATIOS,
        "After-tax operating profit divided by the capital invested in the business (debt plus equity minus cash).",
        "Above the cost of capital (roughly 8 to 10%) the business creates value as it grows; above 15% suggests a durable advantage. Very high values usually mean a small capital base after large buybacks.",
        ("ROIC",))),
    ("roe", Term("ROE (return on equity)", RATIOS,
        "Net income divided by average shareholders' equity.",
        "Above 15% is strong, but debt and buybacks inflate it by shrinking equity. Read it alongside debt to equity.",
        ("ROE",))),
    ("roa", Term("ROA (return on assets)", RATIOS, "Net income divided by total assets.", "Used in the Piotroski score; banks run at around 1%.")),
    ("revenue_cagr", Term("Revenue CAGR", RATIOS, "The compound annual growth rate of revenue over 5 years (and 3 years below it).", "", ("Revenue CAGR 5y", "Revenue CAGR 3y"))),
    ("eps_cagr", Term("EPS CAGR 5y", RATIOS, "The compound annual growth rate of diluted earnings per share over five years.", "Grows faster than net income when the share count falls.")),
    ("fcf_cagr", Term("FCF CAGR 5y", RATIOS, "The compound annual growth rate of free cash flow over five years.")),
    ("net_debt", Term("Net debt", RATIOS, "Total debt minus cash and short-term investments. Negative means net cash: more cash than debt.", "Net cash gives flexibility in a downturn.", ("Net cash", "net cash"))),
    ("debt_equity", Term("Debt / equity", RATIOS, "Total debt divided by shareholders' equity.", "Below 0.5 is conservative, above 2 highly levered; but companies with large buybacks can have small equity and a high ratio without much risk.", ("Debt to equity",))),
    ("current_ratio", Term("Current ratio", RATIOS, "Current assets divided by current liabilities: whether the company can pay its bills due within a year.", "Below 1 is not alarming for companies with strong cash flow.")),
    ("interest_coverage", Term("Interest coverage", RATIOS, "Operating income divided by interest expense: how many times profit covers the interest bill.", "Below 2 is a warning sign; above 8 is comfortable.")),
    ("share_count_change", Term("Share count change per year", RATIOS, "The average yearly change in diluted shares over three years.", "Negative means buybacks shrink the share count, so each share owns more of the company. Positive means dilution.", ("Share count / yr",))),
    ("sbc_ratio", Term("Stock-based compensation to revenue", RATIOS, "Stock-based pay as a share of revenue.")),

    # ------------------------------------------------------------------ quality scores
    ("piotroski", Term("Piotroski F-score", QUALITY,
        "Nine pass/fail tests of profitability, balance-sheet strength and efficiency, comparing the latest fiscal year with the one before. Each pass scores 1.",
        "8 or 9 is strong and improving; 0 to 3 is weak. A test without enough data is shown as n/a and not counted.",
        ("F-score",))),
    ("pf_roa", Term("Positive return on assets", QUALITY, "Pass if net income divided by total assets is above zero: the company was profitable.")),
    ("pf_cfo", Term("Positive operating cash flow", QUALITY, "Pass if operating cash flow was above zero.")),
    ("pf_roa_up", Term("ROA improved", QUALITY, "Pass if return on assets was higher than the year before.")),
    ("pf_accruals", Term("Cash flow exceeds net income", QUALITY, "Pass if operating cash flow was larger than net income: profits are backed by cash, not accounting accruals.")),
    ("pf_leverage", Term("Leverage fell", QUALITY, "Pass if long-term debt relative to assets fell from the year before.")),
    ("pf_current", Term("Current ratio improved", QUALITY, "Pass if current assets relative to current liabilities rose: better short-term liquidity.")),
    ("pf_dilution", Term("No share dilution", QUALITY, "Pass if the diluted share count did not rise.")),
    ("pf_gross", Term("Gross margin improved", QUALITY, "Pass if gross margin was higher than the year before.")),
    ("pf_turnover", Term("Asset turnover improved", QUALITY, "Pass if revenue relative to total assets rose: the company used its assets more productively.")),
    ("pass_fail", Term("Pass / Fail", QUALITY, "Whether the company passed this Piotroski test in the latest fiscal year.", "", ("Pass", "Fail", "Test"))),
    ("altman", Term("Altman Z-score", QUALITY,
        "A bankruptcy-risk score combining working capital, retained earnings, operating profit, market value and sales, each relative to assets or liabilities.",
        "Above 2.99: safe zone. 1.81 to 2.99: grey zone. Below 1.81: distress zone. Built for manufacturers; not meaningful for banks and insurers.",
        ("Safe zone", "Grey zone", "Distress zone", "Safe zone (above 2.99)"))),

    # ------------------------------------------------------------------ DCF
    ("dcf", Term("DCF (discounted cash flow)", DCF,
        "A valuation that projects the company's future free cash flow, discounts each year back to today at your required return, and adds a terminal value for the years beyond.",
        "Highly sensitive to growth, discount rate and terminal growth: check the sensitivity grid before trusting any single value.",
        ("Valuation (DCF)", "Discounted cash flow assumptions"))),
    ("intrinsic_value", Term("Intrinsic value per share", DCF, "What the DCF says each share is worth under your assumptions.", "Compare with the price: a large gap means either an opportunity or assumptions the market does not share.", ("Intrinsic value / share",))),
    ("base_fcf", Term("Base free cash flow", DCF, "The starting free cash flow for the projection, by default the trailing twelve months, in millions of dollars.", "", ("Base free cash flow ($M)",))),
    ("growth_stage1", Term("Growth, years 1-5", DCF, "The yearly free cash flow growth assumed during the high-growth stage.", "The default is the lower of 5-year revenue and FCF growth, limited to between -5% and 15%.", ("Growth, years 1-5 (%)", "Growth"))),
    ("high_growth_years", Term("High-growth years", DCF, "How many years the stage-one growth rate lasts.")),
    ("fade_years", Term("Fade years", DCF, "Years over which growth slides in a straight line from the stage-one rate down to the terminal rate.")),
    ("discount_rate", Term("Discount rate", DCF,
        "The yearly return you require for owning the stock, used to convert future cash into today's dollars.",
        "8 to 10% is typical for a large company; use more for riskier businesses. A higher rate lowers the value.",
        ("Discount rate (%)",))),
    ("terminal_growth", Term("Terminal growth", DCF,
        "The growth rate assumed forever after the forecast years.",
        "Keep it at or below long-run economic growth (about 2 to 3%). It must be below the discount rate.",
        ("Terminal growth (%)",))),
    ("net_cash_input", Term("Net cash ($M)", DCF, "Cash minus debt, added to the value of the operations. Negative for a company with net debt.")),
    ("shares_input", Term("Shares (M)", DCF, "Shares outstanding, in millions, used to turn the company's value into a value per share.")),
    ("terminal_share", Term("Terminal value share of EV", DCF, "How much of the DCF value comes from the years beyond the forecast.", "Above about 75%, the value rests mostly on the terminal growth assumption.")),
    ("reverse_dcf", Term("Growth the price implies (reverse DCF)", DCF,
        "The stage-one growth rate at which the DCF value equals today's price: the growth the market is pricing in.",
        "Compare it with the growth the company has actually delivered. Implied growth well above history means a demanding price.",
        ("Growth the price implies",))),
    ("sensitivity", Term("Sensitivity grid", DCF, "The DCF value per share for different discount rates (rows) and terminal growth rates (columns).", "Shows how much the value depends on two assumptions nobody knows precisely.", ("Sensitivity: value per share", "Discount \\ Terminal"))),
    ("mc_dcf", Term("Monte Carlo DCF", DCF, "The DCF run 20,000 times with growth, discount rate and terminal growth drawn at random around your inputs.", "P(value > price) is the share of those valuations above today's price.", ("Monte Carlo: P(value > price)",))),
    ("projected_cf", Term("Projected cash flows", DCF, "The free cash flow assumed for each forecast year and its present value.", "", ("Present value",))),
    ("present_value", Term("Present value", DCF, "A future amount converted into today's dollars at the discount rate.")),

    # ------------------------------------------------------------------ filings
    ("form_10k", Term("10-K", FILINGS, "The annual report US companies file with the SEC: audited financial statements, the business description (Item 1), risk factors (Item 1A) and management's discussion (Item 7).")),
    ("form_10q", Term("10-Q", FILINGS, "The quarterly report, filed for the first three quarters of the fiscal year. Its statements are unaudited.")),
    ("form_8k", Term("8-K", FILINGS, "A report of a significant event between regular reports: earnings releases, acquisitions, executive changes, material agreements.")),
    ("form_def14a", Term("DEF 14A (proxy statement)", FILINGS, "The document sent before the annual meeting: executive pay, board elections and shareholder votes.", "", ("DEF 14A",))),
    ("form_4", Term("Form 4 (insider transaction)", FILINGS, "Filed within two business days when a director, officer or 10% owner buys or sells the company's shares.", "Many insider sales are routine (planned sales, tax on vested shares); clusters of open-market buying are more informative.", ("Form 4",))),
    ("form_s1", Term("S-1 / S-3", FILINGS, "Registration statements for issuing new securities, for example at an IPO (S-1) or a later offering (S-3).", "", ("S-1", "S-3"))),
    ("form_13dg", Term("SC 13D / SC 13G", FILINGS, "Filed by anyone who acquires more than 5% of a company's shares. 13D means an active investor who may seek changes; 13G a passive one.", "", ("SC 13D", "SC 13G", "SC 13D/A", "SC 13G/A"))),
    ("form_20f", Term("20-F / 40-F / 6-K", FILINGS, "Annual reports of foreign companies listed in the US (20-F; 40-F for Canadian companies) and their interim reports (6-K).", "", ("20-F", "40-F", "6-K"))),
    ("amendment", Term("Amendment (/A)", FILINGS, "A filing ending in /A amends an earlier filing of the same form.")),
    ("accession", Term("Accession number", FILINGS, "The SEC's unique identifier for a filing: the filer's ID, the year and a sequence number.")),
    ("filed", Term("Filed", FILINGS, "The date the filing was submitted to the SEC, when the information became public.")),
    ("report_date", Term("Report date", FILINGS, "The end of the period the filing covers, for example the fiscal year end of a 10-K.")),
    ("form", Term("Form", FILINGS, "The type of SEC filing (10-K, 10-Q, 8-K and so on).")),
    ("description", Term("Description", FILINGS, "The filer's own description of the document.")),
    ("item_business", Term("Business (Item 1)", FILINGS, "The 10-K section describing what the company does, its products, markets and competition.", "", ("Business",))),
    ("item_risk", Term("Risk Factors (Item 1A)", FILINGS, "The section listing the risks the company itself considers material.", "", ("Risk Factors",))),
    ("item_mda", Term("MD&A (Management's Discussion and Analysis)", FILINGS, "Management's explanation of the results, what drove them, liquidity, and the outlook. Item 7 in a 10-K, Item 2 in a 10-Q.", "", ("MD&A",))),
    ("filing_index", Term("Filing index", FILINGS, "The company's filings on EDGAR, newest first. Double-click a row to open the document on sec.gov. The filter shows the periodic and material forms, or every filing including insider Form 4s.", "", ("Periodic and material (10-K, 10-Q, 8-K, proxy, ownership)", "All filings, including Form 4"))),
    ("report_text", Term("Report text", FILINGS, "The Business, Risk Factors and MD&A sections extracted from the latest 10-K and any newer 10-Q, as the research note reads them. Long sections are cut at the length set in Settings.")),
    ("insider_count", Term("Insider filings", FILINGS, "How many Form 4 insider-transaction filings the company had in the last 90 days.")),
    ("cik", Term("CIK", FILINGS, "Central Index Key: the SEC's permanent identifier for a company.")),
    ("xbrl", Term("XBRL", FILINGS, "The machine-readable tagging in SEC filings that lets each number (revenue, net income and so on) be read directly from the filing.")),

    # ------------------------------------------------------------------ data and sources
    ("status_live", Term("Live", DATA, "Fetched from the provider just now.")),
    ("status_cache", Term("Cached", DATA, "From FinLit Pro's saved copy, still within its refresh interval (15 minutes for prices, 12 hours for SEC statements). Press F5 to fetch fresh data.")),
    ("status_stale", Term("Offline copy", DATA, "The provider could not be reached, so the last saved copy is shown. Its retrieval time says how old it is.", "Recent moves may be missing.")),
    ("status_import", Term("Imported file", DATA, "Prices from a CSV file you imported with File > Import prices, used because the online providers failed.")),
    ("status_demo", Term("Simulated", DATA, "Generated data for the DEMO ticker, not a real security.")),
    ("as_of", Term("As of", DATA, "The date the data describes: the last price bar, the balance-sheet date or the filing period.")),
    ("retrieved", Term("Retrieved", DATA, "When FinLit Pro fetched the data. For a cached copy, when it was first fetched.")),
    ("provider", Term("Provider", DATA, "The service the data came from.")),
    ("dataset", Term("Dataset", DATA, "What the data is used for in the app.")),
    ("status", Term("Status", DATA, "How the data was obtained: Live, Cached, Offline copy, Imported file or Simulated.")),
    ("detail", Term("Detail", DATA, "Extra provenance, such as the filing accession number or the reason a fallback was used.")),
    ("yahoo", Term("Yahoo Finance", DATA, "The source of prices, quotes, option chains, headlines and the T-bill rate. Its endpoints are unofficial and intended for personal use, so FinLit Pro throttles requests, caches results and falls back to other routes when it fails.")),
    ("sec_edgar", Term("SEC EDGAR", DATA, "The US Securities and Exchange Commission's public database of company filings, the official source of the financial statements and filing text.", "", ("SEC EDGAR access",))),
    ("personal_use", Term("Personal use", DATA, "FinLit Pro's verdicts, signals and research notes are recommendations for its owner's own investment decisions, computed from the data and assumptions shown. They can be wrong, and simulations are not guarantees.")),
    ("sec_email", Term("SEC contact email", DATA, "The SEC asks every program that reads EDGAR to identify itself with a contact email in each request. It is not an account and is sent only to sec.gov.", "", ("Contact email", "SEC contact email"))),
    ("demo", Term("DEMO", DATA, "A simulated stock (with its own simulated market, DEMO-MKT) for trying every view with no internet. Nothing about it is real.")),
    ("symbol", Term("Symbol", DATA, "The ticker symbol a stock trades under, such as AAPL for Apple.")),
    ("prices_dataset", Term("Prices (dataset)", DATA, "The daily price history behind the chart, returns, risk, prediction model, Monte Carlo and options views.", "", ("Prices",))),
    ("fundamentals_dataset", Term("Fundamentals (dataset)", DATA, "The SEC data behind the Fundamentals view: XBRL financial statements (company facts) and the filing index.", "", ("Fundamentals",))),
    ("sessions", Term("Session", DATA, "A trading day. US markets have about 252 sessions a year.", "", ("Sessions", "Trading days"))),

    # ------------------------------------------------------------------ research note
    ("rec_buy", Term("Buy (recommendation)", NOTE, "The research note's strongest positive recommendation: the evidence supports owning the stock now.", "Read the conviction and the uncertainties with it.")),
    ("rec_accumulate", Term("Accumulate", NOTE, "A positive recommendation to build a position gradually, for example on weakness, rather than all at once.")),
    ("rec_hold", Term("Hold (recommendation)", NOTE, "Keep an existing position but do not add to it: the evidence is balanced.")),
    ("rec_reduce", Term("Reduce", NOTE, "A negative recommendation to trim an existing position.")),
    ("rec_sell", Term("Sell (recommendation)", NOTE, "The strongest negative recommendation: the evidence supports exiting the position.")),
    ("rec_none", Term("No recommendation", NOTE, "The data was not enough to support a view; the note says what is missing.")),
    ("conviction", Term("Conviction", NOTE, "How strongly the evidence supports the recommendation: Low, Medium or High.", "Low conviction means the call could easily flip with new information.")),
    ("confidence", Term("Confidence (interpretation)", NOTE, "How sure the analysis engine is of each interpretation: Low, Medium or High.")),
    ("facts", Term("Facts", NOTE, "Statements that can be checked against the cited sources. Each cites source IDs such as S3; one without a valid source is marked UNVERIFIED.")),
    ("interpretation", Term("Interpretation", NOTE, "Judgements drawn from the facts, kept separate from them and labelled with a confidence level.")),
    ("risks", Term("Risks", NOTE, "Things that could hurt the investment, with their sources.")),
    ("uncertainties", Term("Uncertainties", NOTE, "Ways the conclusion itself could be wrong: missing or stale data, small samples, model limits.")),
    ("data_gaps", Term("Data gaps", NOTE, "Data the note would have used but could not get.")),
    ("source_ids", Term("Source IDs", NOTE, "S1, S2 and so on: numbered sources listed at the end of the note with their links, dates and retrieval times.")),
    ("unverified", Term("UNVERIFIED", NOTE, "A fact that cites no source, or a source ID that does not exist. Treat it as unconfirmed.")),
    ("brief", Term("Research brief", NOTE, "The figures, filing excerpts and headlines the note is based on, each tagged with source IDs. 'Show brief' displays exactly what the analysis engine read.")),
    ("engine", Term("Analysis engine", NOTE, "What writes the note: Claude or an OpenAI model when a key is stored, or the built-in rules engine, which applies fixed published thresholds.", "Automatic uses Claude if a Claude key is stored, then OpenAI, then the rules engine.", ("Engine",))),
    ("horizon_note", Term("Horizon (note)", NOTE, "The holding period the recommendation applies to.")),
    ("api_key", Term("API key", NOTE,
        "A secret that lets FinLit Pro call Anthropic's Claude or OpenAI's models to write the research note. It is stored in Windows Credential Manager, never in a file, and sent only to that provider.",
        "Test key checks it without spending anything. Usage is billed by the provider to the account the key belongs to.",
        ("Anthropic API key", "OpenAI API key"))),
    ("llm_model", Term("Model (analysis engine)", NOTE,
        "Which language model writes the note. For Claude, Opus is the most capable, Sonnet faster and cheaper, Haiku the fastest and cheapest. The OpenAI choice falls back to a smaller model if the first is unavailable to the key.",
        "", ("Claude model", "OpenAI model"))),
    ("effort", Term("Claude effort", NOTE,
        "How much reasoning Claude puts into the note: low, medium, high or xhigh. Higher effort is slower and uses more tokens.",
        "High is a good default for a research note.")),
    ("filing_excerpt", Term("Filing excerpt length", NOTE,
        "How many characters of each filing section (Business, Risk Factors, MD&A) the research note reads. About four characters make a token.",
        "Longer excerpts give the analysis more to work with and cost more.",
        ("Filing excerpt length (characters per section)",))),
    ("transaction_cost", Term("Transaction cost", EVAL,
        "The cost assumed for each trade in the model's strategy test, in basis points (1 bp = 0.01%). It covers commission, the bid-ask spread and slippage.",
        "5 bp is realistic for a liquid large-cap stock; use more for small or illiquid stocks.",
        ("Transaction cost (bp per trade)",))),
]

TERMS: dict[str, Term] = dict(_TERMS)

# Label -> term key, case-insensitive. Built from each term's name and aliases.
ALIASES: dict[str, str] = {}
for _key, _term in _TERMS:
    for _label in (_term.name, *_term.aliases):
        ALIASES.setdefault(_label.casefold(), _key)

# Labels that read the same in more than one place resolve here to the general meaning.
for _label, _key in {
    "volume": "volume", "last": "last_price", "buy": "buy", "sell": "sell", "hold": "hold",
    "position": "long_short_position", "growth": "growth_stage1",
    "expected return": "expected_return_input", "horizon": "forecast_horizon", "net cash": "net_debt",
    "worth it": "worth_it", "marginal": "marginal", "not worth it": "not_worth_it",
    "mean": "mean_row",
}.items():
    ALIASES[_label] = _key

_FAMILIES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^p\d{1,2}$", re.I), "percentile"),
    (re.compile(r"^fy\d{4}$", re.I), "fiscal_year"),
    (re.compile(r"^year \d+$", re.I), "projected_cf"),
    (re.compile(r"^(10-k|10-q|8-k|20-f|40-f|def 14a)/a$", re.I), "amendment"),
    (re.compile(r"^benchmark \S+$", re.I), "benchmark"),
    (re.compile(r"^(5|10|25)-(95|90|75)$"), "band"),
    (re.compile(r"^\d+ contract\(s\)$"), "greeks"),
    (re.compile(r"^(sma|ema)\s?\d+$", re.I), "sma"),
    (re.compile(r"^\d+ trading days$", re.I), "forecast_horizon"),
    (re.compile(r"^(worth it|not worth it|marginal) at ", re.I), None),  # resolved below
    (re.compile(r"^\d+ form 4 \(insider transaction\) filings", re.I), "insider_count"),
]


def _normalise(label: str) -> str:
    return re.sub(r"\s+", " ", (label or "").strip()).casefold()


def lookup(label: str) -> Term | None:
    """The term a displayed label refers to, or None."""
    text = _normalise(label)
    if not text:
        return None
    if text in TERMS:
        return TERMS[text]
    key = ALIASES.get(text)
    if key:
        return TERMS[key]
    for pattern, key in _FAMILIES:
        if pattern.search(text):
            if key is None:
                return TERMS["not_worth_it"] if text.startswith("not") else TERMS["worth_it" if text.startswith("worth") else "marginal"]
            return TERMS[key]
    return None


def _is_html(text: str) -> bool:
    return text.lstrip().startswith("<")


def tip_for(term: Term, extra: str = "") -> str:
    """Tooltip HTML: name, meaning, how to read it, and an optional note about this instance.

    `extra` may be plain text (escaped) or tooltip HTML from this module (inserted as is).
    """
    e = html.escape
    parts = [f"<b>{e(term.name)}</b>", e(term.meaning)]
    if term.reading:
        parts.append(f"<i>How to read it:</i> {e(term.reading)}")
    if extra:
        parts.append(extra if _is_html(extra) else e(extra))
    body = "<br><br>".join([parts[0] + "<br>" + parts[1], *parts[2:]])
    return f"<table width='380'><tr><td>{body}</td></tr></table>"


def plain(label_or_key: str) -> str:
    """The definition as plain text, for HTML title attributes in the research note and the exported report."""
    term = TERMS.get(label_or_key) or lookup(label_or_key)
    if term is None:
        return ""
    return f"{term.name}: {term.meaning}" + (f" How to read it: {term.reading}" if term.reading else "")


def tip(label: str, extra: str = "") -> str:
    """Tooltip HTML for a displayed label, or `extra` alone (plain) when the label is not a known term."""
    term = lookup(label)
    if term is None:
        return extra
    redundant = extra and not _is_html(extra) and extra.strip().casefold() in term.meaning.casefold()
    return tip_for(term, "" if redundant else extra)


# What the action buttons do (not glossary terms, so not listed in the Glossary dialog).
ACTIONS = {
    "Load": "Load the symbol typed in the box (Enter does the same).",
    "Refresh": "Fetch fresh data from the providers, bypassing the saved copies (F5).",
    "Add": "Add the loaded symbol to the watchlist.",
    "Remove": "Remove the selected symbol from the watchlist.",
    "Apply": "Use this symbol as the benchmark for the risk statistics.",
    "Run model": "Run the selected prediction model on the loaded prices at the chosen horizon.",
    "Run evaluation": "Replay the model through this stock's history and score its past forecasts against what happened.",
    "Cancel": "Stop the running job.",
    "Run simulation": "Simulate price paths with the assumptions above.",
    "Load chain": "Fetch the option chain for the chosen expiry from Yahoo Finance.",
    "Analyze contract": "Price the contract, estimate its probabilities and expected value, and give a verdict.",
    "Calculate": "Recalculate the DCF with the assumptions above.",
    "Reset to filing defaults": "Restore the DCF assumptions derived from the company's filings.",
    "Load latest 10-K and 10-Q text": "Download the latest annual and quarterly reports and extract the Business, Risk Factors and MD&A sections.",
    "Generate note": "Write a research note from everything loaded for this symbol, citing a source for every fact.",
    "Show brief": "Show the research brief: exactly the figures and excerpts the analysis engine reads.",
    "Copy": "Copy the note as plain text.",
    "Save": "Save the SEC contact email and load the fundamentals.",
}

# Words in free-text readings (signal descriptions, verdict reasons) that deserve a definition.
KEYWORDS = ["overbought", "oversold", "bullish", "bearish", "uptrend", "downtrend", "crossover", "selloff", "rally",
            "momentum", "bollinger", "macd", "rsi", "volume", "implied volatility", "expected value", "breakeven"]


def explain_text(text: str) -> str:
    """Definitions of the glossary keywords that appear in a free-text reading, as tooltip HTML."""
    found, low = [], (text or "").casefold()
    for word in KEYWORDS:
        if re.search(rf"\b{re.escape(word)}\b", low):
            term = lookup(word) or TERMS.get(word)
            if term and term not in found:
                found.append(term)
    if not found:
        return ""
    e = html.escape
    body = "<br><br>".join(f"<b>{e(t.name)}</b>: {e(t.meaning)}" for t in found[:3])
    return f"<table width='380'><tr><td>{body}</td></tr></table>"


def by_category() -> dict[str, list[Term]]:
    out: dict[str, list[Term]] = {c: [] for c in CATEGORIES}
    for _, term in _TERMS:
        out[term.category].append(term)
    for terms in out.values():
        terms.sort(key=lambda t: t.name.casefold())
    return out
