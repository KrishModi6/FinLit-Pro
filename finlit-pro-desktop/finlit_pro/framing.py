"""How the application describes its own outputs, in one place.

This is a single-user tool. Its verdicts are recommendations for its owner's
own investment decisions, and it says so plainly instead of hedging every
screen. It is equally plain about what the numbers rest on: simulations are
model outputs, not predictions, and every recommendation inherits the
uncertainty of its data and assumptions.
"""

PERSONAL_USE = (
    "Personal use. Verdicts, signals and analysis in FinLit Pro are its recommendations for the owner's "
    "own investment decisions. They are computed from the data and assumptions shown and can be wrong."
)

SIMULATION_NOTE = (
    "Simulated outcomes under the stated assumptions, not predictions. Real prices are not obliged to follow "
    "the model, and normal-shock models understate crash risk."
)

MODEL_NOTE = (
    "Model outputs are point estimates from historical prices only. Check the evaluation metrics before "
    "relying on them: out-of-sample skill is what matters."
)

OPTIONS_NOTE = (
    "Probabilities assume lognormal prices at the chosen volatility. Market-implied figures use the option's "
    "own implied volatility; model figures use your assumptions."
)

ANALYSIS_NOTE = (
    "Facts are tied to numbered sources. Interpretation is the analysis engine's judgement and is labelled "
    "with its confidence."
)
