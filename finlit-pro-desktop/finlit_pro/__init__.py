"""FinLit Pro Desktop: a personal stock research workstation.

Layers, each importable without the ones above it:

    data/       market data and SEC filings, with provenance on every dataset
    model/      the FinLit AI Predictor and its walk-forward evaluation
    analytics/  Monte Carlo, options, risk, fundamentals
    research/   the cited filings and financials analysis
    ui/         the PySide6 desktop interface (the only layer that imports Qt)
"""

__version__ = "1.0.0"
APP_NAME = "FinLit Pro"
