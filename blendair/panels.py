import bpy


class BLENDAIR_PT_MainPanel(bpy.types.Panel):
    bl_label = "Blend(AI)r"
    bl_idname = "BLENDAIR_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend(AI)r'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        from .addon_prefs import get_pref
        prefs = get_pref()
        if not getattr(scene, 'blendair_onboarding_complete', False):
            box = layout.box()
            box.label(text="👋 Welcome to BlendAIr!", icon='INFO')
            box.label(text="Get started in seconds:")
            box.operator("blendair.onboarding", text="Complete Onboarding", icon='CHECKMARK').tooltip = "Complete the onboarding process to get started with BlendAIr."
            box.operator("blendair.show_prompt_bar", text="Show Prompt Bar", icon='GREASEPENCIL').tooltip = "Open the floating overlay prompt bar to send AI requests."
            layout.separator()
        layout.label(text="Prompt History:", icon='PREVIEW_RANGE').tooltip = "View, restore, favorite, copy, delete, or undo previous prompts and responses."
        layout.label(text="LLM Provider:", icon='INFO')
        layout.prop(prefs, "llm_provider", text="").tooltip = "Choose your preferred Large Language Model provider."
        # API key status
        provider = getattr(prefs, 'llm_provider', 'blendair_cloud')
        key_status = False
        if provider == 'blendair_cloud':
            key_status = bool(prefs.blendair_api_key)
        elif provider == 'openai':
            key_status = bool(prefs.openai_api_key)
        elif provider == 'gemini':
            key_status = bool(prefs.gemini_api_key)
        elif provider == 'huggingface':
            key_status = bool(prefs.huggingface_api_key)
        elif provider == 'grok':
            key_status = bool(prefs.grok_api_key)
        elif provider == 'deepseek':
            key_status = bool(prefs.deepseek_api_key)
        elif provider == 'local':
            key_status = bool(prefs.local_llm_endpoint)
        layout.label(text=f"API Key: {'✅' if key_status else '❌'}")
        layout.operator("wm.show_preferences", text="Configure API Keys", icon='PREFERENCES')
        layout.separator()
        layout.prop(scene, "blendair_project", text="Project")
        layout.separator()
        layout.prop(scene, "blendair_prompt")
        layout.operator("blendair.download_model", icon='IMPORT')
        layout.operator("blendair.render", icon='RENDER_STILL')
        layout.operator("blendair.mcp_fetch", icon='FILE_REFRESH')
        layout.prop(scene, "blendair_use_mcp", text="Use BlenderMCP")
        # Supabase config check
        supabase_ok = bool(getattr(prefs, 'supabase_url', '')) and bool(getattr(prefs, 'supabase_key', ''))
        if not supabase_ok:
            layout.label(text="Supabase not configured!", icon='ERROR')
            layout.operator("wm.show_preferences", text="Configure Supabase", icon='PREFERENCES')
        layout.operator("blendair.upload_model", icon='EXPORT')
        layout.separator()
        layout.operator("blendair.execute_prompt", text="Run Prompt", icon='PLAY').prompt = scene.blendair_prompt
        op.prompt = "Rotate 15 degrees"


class BLENDAIR_PT_PromptHistory(bpy.types.Panel):
    bl_label = "Prompt History"
    bl_idname = "BLENDAIR_PT_prompt_history"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BlendAIr"
    bl_parent_id = "BLENDAIR_PT_main"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        from . import history
        user_id = 'local'  # TODO: get from context
        project_id = getattr(context.scene, 'blendair_project', 'demo')
        if not hasattr(context.scene, 'blendair_search_query'):
            context.scene["blendair_search_query"] = ""
        row = layout.row()
        row.prop(context.scene, 'blendair_search_query', text="Search")
        search_query = context.scene.get("blendair_search_query", "")
        entries = history.get_prompt_history(user_id=user_id, project_id=project_id, limit=50)
        filtered = [e for e in entries if search_query.lower() in (e.get('prompt','')+e.get('response','')).lower()]
        fav_count = sum(1 for e in filtered if e.get('favorite', False))
        layout.label(text=f"Favorites: {fav_count}")
        current_prompt = getattr(context.scene, 'blendair_prompt', '')
        for entry in filtered[:20]:
            box = layout.box()
            is_fav = entry.get('favorite', False)
            is_active = entry.get('prompt', '') == current_prompt
            row = box.row(align=True)
            icon_fav = 'FAVORITE' if is_fav else 'SOLO_OFF'
            if is_active:
                row.alert = True
            row.label(text=("★ " if is_fav else "") + (entry.get('prompt', '')[:30] + '...'), icon=icon_fav if is_fav else 'NONE')
            row.label(text=entry.get('response', '')[:30] + '...')
            row.label(text=entry.get('provider', '')[:12])
            row.label(text=entry.get('model', '')[:12])
            row.label(text=str(entry.get('token_usage', '')))
            row.label(text=str(entry.get('cost_usd', '')))
            row.label(text=entry.get('created_at', '')[:19].replace('T',' '))
            ops = row.row(align=True)
            r = ops.operator('blendair.restore_history', text='', icon='FILE_REFRESH')
            r.history_id = str(entry.get('id',''))
            r.tooltip = "Restore this prompt and response to the prompt bar."
            f = ops.operator('blendair.favorite_history', text='', icon=icon_fav)
            f.history_id = str(entry.get('id',''))
            f.tooltip = "Mark this prompt as a favorite."
            c = ops.operator('blendair.copy_history', text='', icon='COPYDOWN')
            c.history_id = str(entry.get('id',''))
            c.tooltip = "Copy prompt and response to clipboard."
            d = ops.operator('blendair.delete_history', text='', icon='TRASH')
            d.history_id = str(entry.get('id',''))
            d.tooltip = "Delete this prompt history entry."
            g = ops.operator('blendair.go_back_history', text='', icon='LOOP_BACK')
            g.history_id = str(entry.get('id',''))
            g.tooltip = "Undo to this point in the prompt history."

from .addon_prefs import get_pref
from .operators import (
    BLENDAIR_OT_RestoreHistory,
    BLENDAIR_OT_FavoriteHistory,
    BLENDAIR_OT_CopyHistory,
    BLENDAIR_OT_DeleteHistory,
    BLENDAIR_OT_GoBackHistory
)

classes = [
    BLENDAIR_PT_MainPanel,
    BLENDAIR_PT_PromptHistory,
    BLENDAIR_OT_RestoreHistory,
    BLENDAIR_OT_FavoriteHistory,
    BLENDAIR_OT_CopyHistory,
    BLENDAIR_OT_DeleteHistory,
    BLENDAIR_OT_GoBackHistory
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.blendair_search_query = bpy.props.StringProperty(name="Search", default="")
    bpy.types.Scene.blendair_onboarding_complete = bpy.props.BoolProperty(name="BlendAIr Onboarding Complete", description="Has the user completed onboarding?", default=False)
    bpy.types.Scene.blendair_project = bpy.props.StringProperty(name="Project ID", default="demo")
    bpy.types.Scene.blendair_prompt = bpy.props.StringProperty(name="Prompt", default="Rotate 15 degrees")
    bpy.types.Scene.blendair_use_mcp = bpy.props.BoolProperty(name="Use MCP", default=False)


def unregister():
    del bpy.types.Scene.blendair_project
    del bpy.types.Scene.blendair_prompt
    del bpy.types.Scene.blendair_use_mcp
    if hasattr(bpy.types.Scene, 'blendair_search_query'):
        del bpy.types.Scene.blendair_search_query
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
