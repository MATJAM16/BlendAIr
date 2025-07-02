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


class SupabasePoller(threading.Thread):
    """Polls Supabase 'jobs' table for queued scripts and executes them."""
    daemon = True

    def run(self):
        while True:
            sb = get_supabase()
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
                time.sleep(10)


# Ensure there is one background runner
if not any(isinstance(t, JobRunner) for t in threading.enumerate()):
    JobRunner().start()
if not any(isinstance(t, SupabasePoller) for t in threading.enumerate()):
    SupabasePoller().start()
