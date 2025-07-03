"""Minimal BlenderMCP client wrapper.
This layer abstracts calls to an MCP server backed by Supabase.
Replace URL endpoints / auth headers as needed.
"""
from typing import Any, Dict, Optional
import requests

from .addon_prefs import get_pref


class BlenderMCPClient:
    def __init__(self):
        prefs = get_pref()
        self.base_url = getattr(prefs, "mcp_url", "http://localhost:9876")

    def get_context(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Fetch project context (models, assets) from MCP server."""
        try:
            r = requests.get(f"{self.base_url}/context/{project_id}")
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            print("[BlendAIr] MCP get_context failed", exc)
            return None

    def push_result(self, job_id: str, payload: Dict[str, Any]):
        """Push render or script result back to MCP."""
        try:
            r = requests.post(f"{self.base_url}/result/{job_id}", json=payload)
            r.raise_for_status()
        except Exception as exc:
            print("[BlendAIr] MCP push_result failed", exc)

def register():
    pass

def unregister():
    pass
