"""Background jobs, so slow providers or long computations never freeze the window.

Each job carries the request id it was started under; the window drops any
result whose id is no longer current, so switching tickers quickly can never
leave one company's numbers under another's name.
"""

from __future__ import annotations

import inspect
import threading
import traceback
from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from finlit_pro.credentials import CredentialError
from finlit_pro.data.models import DataError
from finlit_pro.research import AnalysisError
from finlit_pro.research.note import NoteError
from finlit_pro.validation import ValidationError

EXPECTED = (DataError, ValidationError, AnalysisError, NoteError, CredentialError, ValueError, InterruptedError)


class _Signals(QObject):
    done = Signal(int, object)
    failed = Signal(int, str)
    progress = Signal(int, int, int)  # request id, done, total


class Job(QRunnable):
    """Runs fn(*args). If fn accepts `progress` / `cancelled` keywords, they are supplied."""

    def __init__(self, request_id: int, fn: Callable, *args, **kwargs) -> None:
        super().__init__()
        self.request_id = request_id
        self.fn, self.args, self.kwargs = fn, args, kwargs
        self.signals = _Signals()
        self.cancel_event = threading.Event()
        try:
            params = inspect.signature(fn).parameters
        except (TypeError, ValueError):
            params = {}
        if "progress" in params:
            self.kwargs.setdefault("progress", lambda done, total=0: self._emit(self.signals.progress, self.request_id, int(done), int(total)))
        if "cancelled" in params:
            self.kwargs.setdefault("cancelled", self.cancel_event.is_set)

    def cancel(self) -> None:
        self.cancel_event.set()

    def _emit(self, signal, *args) -> None:
        """Emit unless the window has already gone.

        First Version: a job still running when the window closed (an evaluation, say)
        emitted on a deleted signal object and printed a RuntimeError traceback at exit.
        Current Version: the job notices, marks itself cancelled and stops quietly.
        """
        try:
            signal.emit(*args)
        except RuntimeError:
            self.cancel_event.set()

    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
        except EXPECTED as exc:
            self._emit(self.signals.failed, self.request_id, str(exc))
        except Exception as exc:  # noqa: BLE001 - last line of defence for the UI
            traceback.print_exc()
            self._emit(self.signals.failed, self.request_id, f"Unexpected error ({exc.__class__.__name__}: {exc}).")
        else:
            self._emit(self.signals.done, self.request_id, result)


class Runner:
    def __init__(self) -> None:
        self.pool = QThreadPool.globalInstance()
        self._live: set[QRunnable] = set()

    def start(self, job: Job, on_done: Callable | None = None, on_failed: Callable | None = None, on_progress: Callable | None = None) -> Job:
        job.setAutoDelete(False)
        self._live.add(job)

        def finish(*_):
            self._live.discard(job)

        if on_done:
            job.signals.done.connect(on_done)
        if on_failed:
            job.signals.failed.connect(on_failed)
        if on_progress:
            job.signals.progress.connect(on_progress)
        job.signals.done.connect(finish)
        job.signals.failed.connect(finish)
        self.pool.start(job)
        return job

    def cancel_all(self) -> None:
        for job in list(self._live):
            job.cancel()

    def wait(self, ms: int = 30000) -> bool:
        return self.pool.waitForDone(ms)
