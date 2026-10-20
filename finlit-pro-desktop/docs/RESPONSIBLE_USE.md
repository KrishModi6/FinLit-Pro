# Responsible use

FinLit Pro is personal software. It was built for one person, its owner, to research stocks for
their own investment decisions. This page says what that means and where the limits are.

## The app gives recommendations, for its owner

You asked for an app whose analysis is investment advice for you, not a tool that hedges every
sentence. So it does make calls: the prediction model gives a verdict (STRONG BUY to STRONG SELL),
the options calculator says whether a contract is worth it at the current price, and the research
note ends in a recommendation (Buy, Accumulate, Hold, Reduce, Sell) with a conviction and a horizon.
The banner in the Research Note view and the "Personal use" note in the status bar say this once,
plainly, rather than on every screen.

The wording lives in one place, `finlit_pro/framing.py`, so it can be changed without touching
the views.

That framing is for you. FinLit Pro is not a licensed adviser, its output is not tailored to anyone
else's circumstances, and it should not be passed on to other people as advice.

## Why the recommendations can be wrong

Every recommendation is computed from the data and assumptions on screen, and each of those can be
wrong:

* **Data.** Prices come from unofficial Yahoo endpoints that can be delayed, incomplete or briefly
  wrong. SEC figures are as filed, and XBRL tagging varies. A stale or imported source is labelled,
  but a wrong number from a live source is not detectable.
* **The prediction model** uses price history only. Its out-of-sample record on the ticker is shown
  next to every forecast; if that record shows no skill, the forecast is not evidence of anything.
* **Simulations are not predictions.** The Monte Carlo and the options probabilities describe what
  happens if prices behave like the stated model (constant volatility, independent days, normal or
  fat-tailed shocks). Real prices are not obliged to. Crashes, earnings gaps, halts and regime
  changes fall outside these ranges more often than the models imply.
* **The options verdict** depends on your volatility and expected return. Under the market's own
  implied volatility every fairly priced option has zero expected value; "worth it" means only
  that your assumptions disagree with the market's in your favour.
* **The research note**, when written by a language model, can misread a filing or overstate a
  conclusion. Facts must cite source IDs, citations are checked, and a fact without a valid source is
  marked UNVERIFIED, but the note should still be read against the sources it links to.
* **Small samples.** One stock's history is a small sample for judging a model or estimating a drift.

## Practical rules

* Read the sources and dates (bottom panel) before acting on any number.
* Treat a model verdict as an input, weighted by its evaluation, not as a decision.
* Check option quotes with your broker before trading; the chain here may be delayed.
* Size positions for the drawdowns shown in Returns and Risk, not for the median outcome.
* Keep API keys in the credential store or environment variables (the app never writes them to a
  file), and do not share exported reports that include your positions or notes.

## Privacy

FinLit Pro has no account, server or telemetry. It talks to Yahoo Finance and SEC EDGAR for data,
to sec.gov with the contact email you set, and, only when you press Generate note with a key
stored, to Anthropic or OpenAI with the research brief. Settings, the cache and imported CSVs stay
in your Windows user folders (`%APPDATA%\FinLitPro`, `%LOCALAPPDATA%\FinLitPro`); keys stay in
Windows Credential Manager.
