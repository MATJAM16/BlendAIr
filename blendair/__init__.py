"""Blend(AI)r – Blender add-on entry point.
Minimal but working scaffold that wires up operators, panels and preferences.
"""

import importlib
import sys

try:
    import bpy
except ModuleNotFoundError:  # Running outside Blender (e.g., tests)
    from importlib import import_module
    bpy = import_module('. _bpy_stub', __package__)  # type: ignore
    sys.modules['bpy'] = bpy

from . import addon_prefs, operators, panels, gestures, blendluxcore_integration, mcp_client, ui

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

modules = [addon_prefs, operators, panels, gestures, blendluxcore_integration, mcp_client, ui]


def register():
    importlib.reload(addon_prefs)
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(gestures)
    importlib.reload(blendluxcore_integration)
    importlib.reload(mcp_client)
    importlib.reload(ui)
    operators.register()
    panels.register()
    gestures.register()
    blendluxcore_integration.register()
    mcp_client.register()
    addon_prefs.register()
    ui.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
