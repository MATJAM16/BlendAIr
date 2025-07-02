"""Utility helpers: Supabase client, job queue, logging."""
import threading
import time
import queue
from pathlib import Path
from typing import Callable, Any, Dict, Optional

try:
    from supabase import create_client, Client  # type: ignore
except ImportError:
    Client = Any  # type: ignore
    create_client = None  # type: ignore

import bpy
from .addon_prefs import get_pref

_job_q: "queue.Queue[Dict[str, Any]]" = queue.Queue()


def get_supabase() -> Optional["Client"]:
    prefs = get_pref()
    if create_client and prefs.supabase_url and prefs.supabase_key:
        return create_client(prefs.supabase_url, prefs.supabase_key)
    return None


def enqueue_job(job: Dict[str, Any]):
    _job_q.put(job)


class JobRunner(threading.Thread):
    daemon = True

    def run(self):
        while True:
            try:
                job = _job_q.get(timeout=1)
            except queue.Empty:
                continue
            self.process_job(job)
            _job_q.task_done()

    def process_job(self, job: Dict[str, Any]):
        # For now, just print; production: write to Supabase
        print("Processing job", job)
        func: Callable[..., Any] = job.get("func")
        if callable(func):
            try:
                func(*job.get("args", []), **job.get("kwargs", {}))
            except Exception as e:
                print("Job failed", e)


# Ensure there is one background runner
if not any(isinstance(t, JobRunner) for t in threading.enumerate()):
    JobRunner().start()
