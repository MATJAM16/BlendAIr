"""BlendAIr utility helpers.

Works in Blender (real `bpy`) and in CI/tests (no `bpy`).
"""

from __future__ import annotations

import os
import threading
import traceback
from functools import wraps
from pathlib import Path
from queue import Queue
from types import SimpleNamespace
from typing import Any, Optional, Final

# -----------------------------------------------------------------------------
# bpy import setup
# -----------------------------------------------------------------------------
try:
    import bpy  # type: ignore
    IN_BLENDER: Final = True
    # Ensure required attributes exist for tests
    if not hasattr(bpy, "app"):
        bpy.app = SimpleNamespace(tempdir="/tmp")  # type: ignore
except ModuleNotFoundError:
    bpy = SimpleNamespace(app=SimpleNamespace(tempdir="/tmp"))  # type: ignore
    IN_BLENDER = False  # type: ignore

# -----------------------------------------------------------------------------
# Logging utilities
# -----------------------------------------------------------------------------
LOG_PATH = Path(getattr(bpy.app, "tempdir", ".")) / "blendair.log"

def log_error(exc: BaseException) -> None:
    """Log exception traceback to file and console."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fp:
        fp.write("\n---\n")
        traceback.print_exc(file=fp)
    print(f"[BlendAIr] Error logged to {LOG_PATH}")

# -----------------------------------------------------------------------------
# Decorators
# -----------------------------------------------------------------------------

def safe_exec(func):  # noqa: D401
    """Decorator wrapping Blender operator execute methods."""
    @wraps(func)
    def wrapper(self, context, *args, **kwargs):  # type: ignore[override]
        try:
            return func(self, context, *args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            log_error(exc)
            if IN_BLENDER and hasattr(self, "report"):
                self.report({"ERROR"}, f"BlendAIr: {exc}")
            return {"CANCELLED"}
    return wrapper

# -----------------------------------------------------------------------------
# Job queue
# -----------------------------------------------------------------------------
JOB_QUEUE: Queue[dict[str, Any]] = Queue()

def enqueue_job(job: dict[str, Any]) -> None:
    """Add a job dict to the global queue."""
    JOB_QUEUE.put(job)

# -----------------------------------------------------------------------------
# Supabase helper (optional)
# -----------------------------------------------------------------------------
_SUPABASE_CLIENT: Optional[Any] = None

def get_supabase():
    """Return Supabase client or None if env or dependency missing."""
    global _SUPABASE_CLIENT  # noqa: PLW0603
    if _SUPABASE_CLIENT is not None:
        return _SUPABASE_CLIENT

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not (url and key):
        return None
    try:
        from supabase import create_client  # lazy import
        _SUPABASE_CLIENT = create_client(url, key)
        return _SUPABASE_CLIENT
    except Exception as exc:  # noqa: BLE001
        print("[BlendAIr] Supabase client init failed:", exc)
        return None

# -----------------------------------------------------------------------------
# Background thread stubs (threads disabled in CI)
# -----------------------------------------------------------------------------
_RUNNING_THREADS: list[threading.Thread] = []
_STOP_EVENT = threading.Event()

def start_background_threads() -> None:
    """Start background threads inside Blender only."""
    if not IN_BLENDER or _RUNNING_THREADS:
        return
    # Example thread: Supabase poller (define your real function elsewhere)
    # t = threading.Thread(target=_supabase_poller, daemon=True, name="BlendAIrPoller")
    # t.start()
    # _RUNNING_THREADS.append(t)


def stop_background_threads() -> None:
    """Stop and join background threads."""
    _STOP_EVENT.set()
    for t in _RUNNING_THREADS:
        t.join(timeout=2)
    _RUNNING_THREADS.clear()
    _STOP_EVENT.clear()

