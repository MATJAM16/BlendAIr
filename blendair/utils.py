"""Utility helpers for BlendAIr.

This single, clean implementation works in two contexts:
1. Inside Blender: full functionality (error logging, thread helpers, Supabase).
2. Headless environments (CI/tests): safe fall-backs so that importing the
   add-on does not crash when `bpy` is missing.
"""

from __future__ import annotations

import os
import threading
import traceback
from functools import wraps
from pathlib import Path
from queue import Queue
from types import SimpleNamespace
from typing import Any, Optional

# -----------------------------------------------------------------------------
# bpy import (real in Blender, dummy in CI)
# -----------------------------------------------------------------------------

try:
    import bpy  # type: ignore
    _IN_BLENDER = True
except ModuleNotFoundError:  # running in CI / outside Blender
    bpy = SimpleNamespace(app=SimpleNamespace(tempdir="/tmp"))  # type: ignore
    _IN_BLENDER = False

# -----------------------------------------------------------------------------
# Logging & safe-exec decorator
# -----------------------------------------------------------------------------

_LOG_PATH = Path(getattr(bpy.app, "tempdir", ".")) / "blendair.log"


def log_error(exc: BaseException) -> None:
    """Append a traceback to the add-on log file and echo to console."""

    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOG_PATH.open("a", encoding="utf-8") as fp:
        fp.write("\n---\n")
        traceback.print_exc(file=fp)
    print(f"[BlendAIr] Error logged to {_LOG_PATH}")


def safe_exec(func):  # noqa: D401 – simple decorator
    """Decorator for operator `execute` methods with robust error capture."""

    @wraps(func)
    def wrapper(self, context, *args, **kwargs):  # type: ignore[override]
        try:
            return func(self, context, *args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            log_error(exc)
            if _IN_BLENDER and hasattr(self, "report"):
                self.report({"ERROR"}, f"BlendAIr: {exc}")
            return {"CANCELLED"}

    return wrapper

# -----------------------------------------------------------------------------
# Job queue (used by background threads & operators)
# -----------------------------------------------------------------------------

_JOB_QUEUE: Queue[dict[str, Any]] = Queue()


def enqueue_job(job: dict[str, Any]) -> None:
    """Put a job dict onto the queue (thread-safe)."""

    _JOB_QUEUE.put(job)


# -----------------------------------------------------------------------------
# Supabase helper – returns client or None (safe in CI)
# -----------------------------------------------------------------------------

_SUPABASE_CLIENT: Optional[Any] = None


def get_supabase():  # noqa: D401
    """Create (once) and return a Supabase client, or ``None`` if unavailable."""

    global _SUPABASE_CLIENT  # noqa: PLW0603
    if _SUPABASE_CLIENT is not None:
        return _SUPABASE_CLIENT

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not (url and key):
        return None

    try:
        from supabase import create_client  # lazy import to avoid heavy dep if unused

        _SUPABASE_CLIENT = create_client(url, key)
        return _SUPABASE_CLIENT
    except Exception as exc:  # noqa: BLE001
        print("[BlendAIr] Supabase client init failed:", exc)
        return None


# -----------------------------------------------------------------------------
# Background thread management – real in Blender, no-op in CI
# -----------------------------------------------------------------------------

_RUNNING_THREADS: list[threading.Thread] = []
_STOP_EVENT = threading.Event()


def _supabase_poller() -> None:
    """Example poller that fetches queued jobs and enqueues them (simplified)."""

    sb = get_supabase()
    if sb is None:
        return  # nothing to do

    while not _STOP_EVENT.is_set():
        try:
            res = (
                sb.table("jobs")
                .select("id, script")
                .eq("status", "queued")
                .limit(5)
                .execute()
            )
            for row in res.data or []:
                enqueue_job({"func": exec, "args": (row.get("script", ""),)})
                sb.table("jobs").update({"status": "running"}).eq("id", row["id"]).execute()
        except Exception as exc:  # noqa: BLE001
            print("[BlendAIr] Supabase poller error:", exc)
        _STOP_EVENT.wait(5)


def start_background_threads() -> None:
    """Spin up background threads (only inside Blender)."""

    if not _IN_BLENDER:
        return  # CI – skip

    if _RUNNING_THREADS:
        return  # already running

    t = threading.Thread(target=_supabase_poller, name="BlendAIrSupabase", daemon=True)
    t.start()
    _RUNNING_THREADS.append(t)


def stop_background_threads() -> None:
    """Signal threads to stop and wait for them to finish."""

    _STOP_EVENT.set()
    for t in _RUNNING_THREADS:
        t.join(timeout=2)
    _RUNNING_THREADS.clear()
    _STOP_EVENT.clear()

This module intentionally avoids starting background threads or making real
network calls when imported in a non-Blender environment (e.g. GitHub CI).
Only the symbols required by other sub-modules and the tests are implemented.
"""

from __future__ import annotations

import os
import sys
import threading
import time
import traceback
from functools import wraps
from pathlib import Path
from queue import Queue, Empty
from types import SimpleNamespace

# -----------------------------------------------------------------------------
# bpy import (works with the fake module under tests)
# -----------------------------------------------------------------------------

try:
    import bpy  # type: ignore
except ModuleNotFoundError:
    # Fallback – create a minimal dummy bpy with the pieces we use here.
    bpy = SimpleNamespace(app=SimpleNamespace(tempdir="/tmp"))  # type: ignore

# -----------------------------------------------------------------------------
# Error logging & decorator
# -----------------------------------------------------------------------------

LOG_PATH = Path(getattr(bpy.app, "tempdir", ".")) / "blendair.log"


def log_error(exc: BaseException) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fp:
        fp.write("\n---\n")
        traceback.print_exc(file=fp)
    print(f"[BlendAIr] Error logged to {LOG_PATH}")


def safe_exec(func):  # noqa: D401 – simple decorator
    """Decorator that wraps an operator execute method in try/except."""

    @wraps(func)
    def wrapper(self, context, *args, **kwargs):  # type: ignore[override]
        try:
            return func(self, context, *args, **kwargs)
        except Exception as exc:  # noqa: BLE001 – log all exceptions
            log_error(exc)
            # Report to the user if running inside Blender.
            if hasattr(self, "report"):
                self.report({"ERROR"}, f"BlendAIr: {exc}")
            return {"CANCELLED"}

    return wrapper


# -----------------------------------------------------------------------------
# Job queue helpers (used by operators)
# -----------------------------------------------------------------------------

_job_queue: Queue = Queue()


def enqueue_job(job):  # noqa: ANN001 – accept any job structure for now
    """Place a job dict onto the background queue (stub for tests)."""

    _job_queue.put(job)


# -----------------------------------------------------------------------------
# Supabase helper (returns None in CI to avoid network)
# -----------------------------------------------------------------------------

_SUPABASE_CLIENT = None


def get_supabase():  # noqa: D401
    """Return a cached Supabase client or ``None`` in headless CI mode."""

    global _SUPABASE_CLIENT  # noqa: PLW0603
    if _SUPABASE_CLIENT is not None:
        return _SUPABASE_CLIENT

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if url and key:
        try:
            from supabase import create_client  # lazy import

            _SUPABASE_CLIENT = create_client(url, key)
            return _SUPABASE_CLIENT
        except Exception as exc:  # noqa: BLE001
            print("[BlendAIr] Failed to create Supabase client:", exc)
            return None
    return None


# -----------------------------------------------------------------------------
# Background thread management stubs (disabled in tests)
# -----------------------------------------------------------------------------

_running_threads: list[threading.Thread] = []
_stop_event = threading.Event()


def start_background_threads():
    """Disabled in CI – real threads start only inside Blender."""

    pass


def stop_background_threads():
    """Signal background threads to stop (no-op in CI)."""

    _stop_event.set()
    while _running_threads:
        t = _running_threads.pop()
        t.join(timeout=1)




    log_path = Path(bpy.app.tempdir) / "blendair.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n---\n")
        traceback.print_exc(file=f)
    print(f"[BlendAIr] Error logged to {log_path}")

def safe_exec(func):
    @wraps(func)
    def wrapper(self, context, *args, **kwargs):
        try:
            return func(self, context, *args, **kwargs)
        except Exception as exc:
            log_error(exc)
            self.report({'ERROR'}, f"BlendAIr: {exc}")
            return {'CANCELLED'}
    return wrapper
            if not sb:
                time.sleep(10)
                continue
            try:
                res = (
                    sb.table("jobs")
                    .select("id, script")
                    .eq("status", "queued")
                    .limit(5)
                    .execute()
                )
                for row in res.data or []:
                    script = row.get("script")
                    job_id = row.get("id")
                    if script:
                        enqueue_job({"func": exec, "args": (script,)})
                        sb.table("jobs").update({"status": "running"}).eq("id", job_id).execute()
                time.sleep(5)
            except Exception as exc:
                print("Supabase poller error", exc)
                
