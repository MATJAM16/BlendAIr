"""Blend(AI)r – Blender add-on entry point.
Minimal but working scaffold that wires up operators, panels and preferences.
"""

import importlib
import bpy

from . import addon_prefs, operators, panels, gestures, blendluxcore_integration, mcp_client

bl_info = {
    "name": "Blend(AI)r",
    "author": "Cascade AI",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Blend(AI)r",
    "description": "Prompt- and gesture-driven editing with Supabase integration.",
    "warning": "Alpha",
    "doc_url": "https://github.com/yourorg/blendair",
    "category": "3D View",
}

modules = [addon_prefs, operators, panels, gestures, blendluxcore_integration, mcp_client]


def register():
    for m in modules:
        importlib.reload(m)
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
