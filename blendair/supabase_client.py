import requests
import os

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

# You can also set these dynamically from the add-on preferences

def set_supabase_creds(url, key):
    global SUPABASE_URL, SUPABASE_KEY
    SUPABASE_URL = url
    SUPABASE_KEY = key

def _headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }

def insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.post(url, headers=_headers(), json=data)
    resp.raise_for_status()
    return resp.json()

def select(table, filters=None, limit=100):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {'limit': limit}
    if filters:
        params.update(filters)
    resp = requests.get(url, headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json()

def update(table, match, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: v for k, v in filters.items()}
    headers = get_headers()
    headers['Prefer'] = 'return=representation'
    r = requests.patch(url, headers=headers, params=params, json=data)
    r.raise_for_status()
    return r.json()

def delete(table, match):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = get_headers()
    resp = requests.delete(url, headers=headers, params=match)
    resp.raise_for_status()
    return resp.json()

def test_supabase():
    """Test connection by fetching user_prefs (should return 200 or 401 if keys are valid)."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/user_prefs"
        resp = requests.get(url, headers=get_headers(), params={'limit': 1})
        return resp.status_code == 200 or resp.status_code == 401
    except Exception as e:
        print(f"[BlendAIr] Supabase test failed: {e}")
        return False
