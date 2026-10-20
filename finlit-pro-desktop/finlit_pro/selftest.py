"""`FinLitPro.exe --self-test`: open the real window offscreen on DEMO and check it works.

Exits 0 when prices, the prediction model, Monte Carlo, risk and fundamentals
all load; 1 otherwise. It uses a temporary data folder and never goes
online, so it is safe to run anywhere. The build workflow runs it on the
frozen Windows build, and it is a quick check after installing.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time


def run(timeout_s: float = 120.0) -> int:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["FINLIT_PRO_HOME"] = tempfile.mkdtemp(prefix="finlit-pro-selftest-")
    from finlit_pro.config import Settings
    from finlit_pro.ui.app import make_app

    app = make_app([])
    from finlit_pro.ui.main_window import MainWindow

    window = MainWindow(Settings(watchlist=["DEMO"], ai_provider="rules"))
    window.load("DEMO")

    def ready() -> bool:
        ws = window.ws
        return bool(ws and ws.history and ws.forecast and ws.mc and ws.risk and ws.fundamentals)

    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline and not ready():
        app.processEvents()
        time.sleep(0.02)
    ok = ready()
    for job in window.jobs.values():
        job.cancel()
    window.runner.wait(30_000)
    message = "FinLit Pro self-test passed." if ok else "FinLit Pro self-test failed: the DEMO workspace did not finish loading."
    print(message, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1
