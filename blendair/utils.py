import bpy
import traceback
import threading
from pathlib import Path
from functools import wraps

# --- THREAD MANAGEMENT ---
# Global list to hold running background threads and an event to signal them to stop.
running_threads = []
stop_event = threading.Event()

def log_error(exc):
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
                time.sleep(10)



