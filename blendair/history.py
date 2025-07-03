"""
BlendAIr Prompt and Gesture History Management
- Handles in-memory and Supabase-backed history for prompts, responses, gestures.
- Supports undo/redo, favorites, and analytics.
"""
from .supabase_client import insert, select, update, delete
import datetime

# In-memory cache (for fast undo/redo and local-only mode)
prompt_history = []  # List of dicts
current_index = -1

def log_prompt(user_id, project_id, prompt, response, provider=None, model=None, token_usage=None, cost_usd=None, latency_ms=None, previous_id=None, favorite=False):
    global current_index
    undo_pointer = current_index if current_index >= 0 else None
    entry = {
        'user_id': user_id,
        'project_id': project_id,
        'prompt': prompt,
        'response': response,
        'provider': provider,
        'model': model,
        'token_usage': token_usage,
        'cost_usd': cost_usd,
        'latency_ms': latency_ms,
        'previous_id': previous_id,
        'created_at': datetime.datetime.utcnow().isoformat(),
        'favorite': favorite,
        'undo_pointer': undo_pointer
    }
    # Save to Supabase
    try:
        insert('prompt_history', entry)
    except Exception as e:
        print(f"[BlendAIr] Failed to log prompt to Supabase: {e}")
    # Save to memory
    prompt_history.append(entry)
    current_index = len(prompt_history) - 1
    return entry


def update_prompt_favorite(history_id, favorite=True):
    try:
        from .supabase_client import update
        update('prompt_history', {'id': f'eq.{history_id}'}, {'favorite': favorite})
    except Exception as e:
        print(f"[BlendAIr] Failed to update favorite: {e}")


def set_undo_pointer(idx):
    global current_index
    if 0 <= idx < len(prompt_history):
        current_index = idx


def go_back():
    global current_index
    if current_index >= 0:
        entry = prompt_history[current_index]
        pointer = entry.get('undo_pointer')
        if pointer is not None and 0 <= pointer < len(prompt_history):
            current_index = pointer
            return prompt_history[pointer]
    return None

def get_prompt_history(user_id=None, project_id=None, limit=100):
    filters = {}
    if user_id:
        filters['user_id'] = f"eq.{user_id}"
    if project_id:
        filters['project_id'] = f"eq.{project_id}"
    try:
        results = select('prompt_history', filters, limit)
        # Sort favorites first
        results.sort(key=lambda x: x.get('favorite', False), reverse=True)
        return results
    except Exception as e:
        print(f"[BlendAIr] Failed to fetch prompt history: {e}")
        return []

def undo():
    global current_index
    if current_index > 0:
        current_index -= 1
        return prompt_history[current_index]
    return None

def redo():
    global current_index
    if current_index < len(prompt_history) - 1:
        current_index += 1
        return prompt_history[current_index]
    return None

def log_gesture(user_id, project_id, gesture):
    entry = {
        'user_id': user_id,
        'project_id': project_id,
        'gesture': gesture,
        'created_at': datetime.datetime.utcnow().isoformat()
    }
    try:
        insert('gesture_history', entry)
    except Exception as e:
        print(f"[BlendAIr] Failed to log gesture to Supabase: {e}")
    return entry

def get_gesture_history(user_id=None, project_id=None, limit=100):
    filters = {}
    if user_id:
        filters['user_id'] = f"eq.{user_id}"
    if project_id:
        filters['project_id'] = f"eq.{project_id}"
    try:
        return select('gesture_history', filters, limit)
    except Exception as e:
        print(f"[BlendAIr] Failed to fetch gesture history: {e}")
        return []
