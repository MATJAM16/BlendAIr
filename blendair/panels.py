import bpy
from bpy.types import Panel

class BLENDAIR_PT_Sidebar(Panel):
    bl_label = "Blend(AI)r"
    bl_idname = "BLENDAIR_PT_sidebar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend(AI)r'

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        layout.prop(wm, 'blendair_current_prompt', text="Prompt")
        row = layout.row()
        row.operator('blendair.execute_prompt', text="Run Prompt", icon='PLAY')
        layout.label(text=wm.get('blendair_status', 'Ready'), icon='INFO')

def register():
    bpy.utils.register_class(BLENDAIR_PT_Sidebar)
    if not hasattr(bpy.types.WindowManager, 'blendair_current_prompt'):
        bpy.types.WindowManager.blendair_current_prompt = bpy.props.StringProperty(
            name="Current Prompt", default="")
    if not hasattr(bpy.types.WindowManager, 'blendair_status'):
        bpy.types.WindowManager.blendair_status = bpy.props.StringProperty(
            name="Status", default="Ready")

def unregister():
    bpy.utils.unregister_class(BLENDAIR_PT_Sidebar)
    if hasattr(bpy.types.WindowManager, 'blendair_current_prompt'):
        del bpy.types.WindowManager.blendair_current_prompt
    if hasattr(bpy.types.WindowManager, 'blendair_status'):
        del bpy.types.WindowManager.blendair_status
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
            f = ops.operator('blendair.favorite_history', text='', icon=icon_fav)
            f.history_id = str(entry.get('id',''))
            c = ops.operator('blendair.copy_history', text='', icon='COPYDOWN')
            c.history_id = str(entry.get('id',''))
            d = ops.operator('blendair.delete_history', text='', icon='TRASH')
            d.history_id = str(entry.get('id',''))
            g = ops.operator('blendair.go_back_history', text='', icon='LOOP_BACK')
            g.history_id = str(entry.get('id',''))

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
