"""Background jobs, so a slow network or a big simulation never freezes the window.

Every job carries the request id it was started under. The window ignores a
result whose id is no longer current, so switching tickers twice in quick
succession cannot leave the screen showing the older company's numbers under
the newer one's name. (The FinLit Pro website hit exactly this race.)
"""

from __future__ import annotations

import threading
import traceback
from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from finlit_quant.ai import AIError
from finlit_quant.data.models import DataError
from finlit_quant.validation import ValidationError

FRIENDLY = (DataError, ValidationError, AIError, ValueError)


class _Signals(QObject):
    done = Signal(int, object)
    failed = Signal(int, str)
    chunk = Signal(int, str)


class Job(QRunnable):
    def __init__(self, request_id: int, fn: Callable, *args, **kwargs) -> None:
        super().__init__()
        self.request_id = request_id
        self.fn, self.args, self.kwargs = fn, args, kwargs
        self.signals = _Signals()

    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
        except FRIENDLY as exc:
            self.signals.failed.emit(self.request_id, str(exc))
        except Exception as exc:  # noqa: BLE001 - last line of defence for the UI
            traceback.print_exc()
            self.signals.failed.emit(self.request_id, f"Something unexpected went wrong ({exc.__class__.__name__}: {exc}). Try again.")
        else:
            self.signals.done.emit(self.request_id, result)


class StreamJob(QRunnable):
    """Runs a generator, forwarding each piece as it arrives."""

    def __init__(self, request_id: int, make_iter: Callable) -> None:
        super().__init__()
        self.request_id = request_id
        self.make_iter = make_iter
        self.signals = _Signals()
        self.cancelled = threading.Event()

    def run(self) -> None:
        parts: list[str] = []
        try:
            for piece in self.make_iter():
                if self.cancelled.is_set():
                    break
                parts.append(piece)
                self.signals.chunk.emit(self.request_id, piece)
        except FRIENDLY as exc:
            self.signals.failed.emit(self.request_id, str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            self.signals.failed.emit(self.request_id, f"The AI request failed unexpectedly ({exc.__class__.__name__}). Try again.")
            return
        self.signals.done.emit(self.request_id, "".join(parts))


class Runner:
    """Starts jobs and keeps them alive until they report back."""

    def __init__(self) -> None:
        self.pool = QThreadPool.globalInstance()
        self._live: set[QRunnable] = set()

    def start(self, job: QRunnable, on_done: Callable | None = None, on_failed: Callable | None = None, on_chunk: Callable | None = None) -> QRunnable:
        job.setAutoDelete(False)
        self._live.add(job)

        def finish(*_):
            self._live.discard(job)

        if on_done:
            job.signals.done.connect(on_done)
        if on_failed:
            job.signals.failed.connect(on_failed)
        if on_chunk:
            job.signals.chunk.connect(on_chunk)
        job.signals.done.connect(finish)
        job.signals.failed.connect(finish)
        self.pool.start(job)
        return job

    def wait(self, ms: int = 30000) -> bool:
        return self.pool.waitForDone(ms)
