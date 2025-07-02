"""Helpers for communicating with the LLM service."""
import requests
from typing import Optional
from .addon_prefs import get_pref


def fetch_script(prompt: str) -> Optional[str]:
    prefs = get_pref()
    try:
        resp = requests.post(prefs.llm_endpoint, json={"prompt": prompt}, timeout=30)
        resp.raise_for_status()
        return resp.json().get("script")
    except Exception as e:
        print(f"[BlendAIr] Failed to fetch script: {e}")
        return None
