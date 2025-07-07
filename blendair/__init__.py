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
from . import addon_prefs, deps, operators, panels, blenderkit

# --- REGISTRATION --- #

# This list is the single source of truth for all add-on classes.
CLASSES = [
    # Core / Preferences
    addon_prefs.BlendAirAddonPreferences,

    # Operators
    operators.BLENDAIR_OT_ExecutePrompt,
    operators.BLENDAIR_OT_RestoreHistory,
    operators.BLENDAIR_OT_FavoriteHistory,
    operators.BLENDAIR_OT_CopyHistory,
    operators.BLENDAIR_OT_DeleteHistory,
    operators.BLENDAIR_OT_GoBackHistory,

    # Panels & UI
    panels.BLENDAIR_PT_MainPanel,
    panels.BLENDAIR_PT_PromptPanel,
    panels.BLENDAIR_PT_PromptHistory,

    # BlenderKit Integration
    blenderkit.BlendAirBKitAsset,
    blenderkit.BLENDAIR_OT_BKitSearch,
    blenderkit.BLENDAIR_OT_BKitImport,
    blenderkit.BLENDAIR_PT_BlenderKitPanel,
    blenderkit.BLENDAIR_UL_BKitAssets,
]

def register():
    """Register all add-on classes and properties."""
    deps.check_and_prompt_install()

    print("--- Registering BlendAIr --- ")
    for cls in CLASSES:
        try:
            bpy.utils.register_class(cls)
            print(f"Registered class: {cls.__name__}")
        except Exception as e:
            print(f"\n--- BLENDAIR REGISTRATION ERROR ---")
            print(f"Failed to register class: {cls.__name__}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            print("-------------------------------------\n")
            # Unregister all previously registered classes before failing
            unregister()
            return

    # Register scene properties
    bpy.types.Scene.blendair_prompt = bpy.props.StringProperty(
        name="BlendAIr Prompt",
        description="Enter your prompt for the AI",
        default=""
    )
    bpy.types.Scene.blendair_status = bpy.props.StringProperty(
        name="BlendAIr Status",
        default="Ready"
    )
    # BlenderKit properties
    bpy.types.Scene.blendair_bkit_query = bpy.props.StringProperty(name="BlenderKit Query", default="")
    bpy.types.Scene.blendair_bkit_assets = bpy.props.CollectionProperty(type=blenderkit.BlendAirBKitAsset)
    bpy.types.Scene.blendair_bkit_asset_index = bpy.props.IntProperty(name="Asset Index", default=0)

def unregister():
    """Unregister all add-on classes and properties in reverse order."""
    print("--- Unregistering BlendAIr --- ")
    for cls in reversed(CLASSES):
        try:
            bpy.utils.unregister_class(cls)
            print(f"Unregistered class: {cls.__name__}")
        except Exception as e:
            print(f"\n--- BLENDAIR UNREGISTRATION ERROR ---")
            print(f"Failed to unregister class: {cls.__name__}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            print("---------------------------------------\n")

    # Unregister scene properties
    del bpy.types.Scene.blendair_prompt
    del bpy.types.Scene.blendair_status
    del bpy.types.Scene.blendair_bkit_query
    del bpy.types.Scene.blendair_bkit_assets
    del bpy.types.Scene.blendair_bkit_asset_index
