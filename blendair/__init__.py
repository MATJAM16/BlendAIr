"""Blend(AI)r – Blender add-on entry point.
Minimal but working scaffold that wires up operators, panels and preferences.
"""

bl_info = {
    "name": "Blend(AI)r",
    "author": "Cascade AI / Windsurf",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Blend(AI)r",
    "description": "Prompt-driven, AI-powered Blender workflow.",
    "warning": "Alpha",
    "doc_url": "https://github.com/windsurf-ai/blendair",
    "category": "3D View",
}

import bpy
from . import panels, operators, addon_prefs, deps

def register():
    deps.check_and_prompt_install()
    addon_prefs.register()
    operators.register()
    panels.register()

def unregister():
    panels.unregister()
    operators.unregister()
    addon_prefs.unregister()
