"""Blend(AI)r – Blender add-on entry point.
Minimal but working scaffold that wires up operators, panels and preferences.
"""

bl_info = {
    "name": "BlendAIr",
    "author": "Mathieu Jammal <mathieu@polare.ch>",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > BlendAIr",
    "description": "AI-powered prompt interface for Blender with LLM, BlenderKit, and more.",
    "warning": "",
    "doc_url": "https://github.com/Matjay007/blendair",
    "tracker_url": "https://github.com/Matjay007/blendair/issues",
    "category": "3D View",
}

import bpy
from . import panels, operators, addon_prefs, deps, blenderkit

def register():
    deps.check_and_prompt_install()
    addon_prefs.register()
    operators.register()
    panels.register()
    blenderkit.register()

def unregister():
    blenderkit.unregister()
    panels.unregister()
    operators.unregister()
    addon_prefs.unregister()
