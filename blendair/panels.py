import bpy

# --- Main Panel --- #

class BLENDAIR_PT_MainPanel(bpy.types.Panel):
    """The main parent panel for the BlendAIr add-on in the sidebar."""
    bl_label = "BlendAIr"
    bl_idname = "BLENDAIR_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendAIr' # This creates the tab in the N-panel

    def draw(self, context):
        layout = self.layout
        # The content of the child panels will be drawn automatically as tabs.
        layout.label(text="AI-Powered Workflow")


# --- Child Panels (Tabs) --- #

class BLENDAIR_PT_PromptPanel(bpy.types.Panel):
    """Panel for the main prompt input."""
    bl_label = "Prompt"
    bl_idname = "BLENDAIR_PT_PromptPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'BLENDAIR_PT_MainPanel' # Nest this panel as a tab

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter your prompt:")
        layout.prop(context.scene, "blendair_prompt", text="")
        layout.operator("execute.prompt", text="Run Prompt")
        layout.label(text=f"Status: {context.scene.blendair_status}")


class BLENDAIR_PT_PromptHistory(bpy.types.Panel):
    """Panel for displaying prompt history."""
    bl_label = "History"
    bl_idname = "BLENDAIR_PT_PromptHistory"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'BLENDAIR_PT_MainPanel'

    def draw(self, context):
        layout = self.layout
        from . import history # Local import to avoid circular dependency issues

        # UI for searching history
        row = layout.row()
        row.prop(context.scene, 'blendair_search_query', text="Search", icon='VIEWZOOM')
        search_query = context.scene.get("blendair_search_query", "")

        # Fetch and filter history
        entries = history.get_prompt_history(user_id='local', project_id='demo', limit=50)
        if search_query:
            filtered = [e for e in entries if search_query.lower() in (e.get('prompt','') + e.get('response','')).lower()]
        else:
            filtered = entries

        # Display history entries
        if not filtered:
            layout.label(text="No history found.")
            return

        for entry in filtered[:20]:
            box = layout.box()
            row = box.row(align=True)

            # Display prompt info
            is_fav = entry.get('favorite', False)
            icon_fav = 'FAVORITE' if is_fav else 'SOLO_OFF'
            row.label(text=entry.get('prompt', 'No Prompt')[:50], icon=icon_fav)

            # Operator buttons
            op_row = row.row(align=True)
            op_row.operator('blendair.restore_history', text='', icon='FILE_REFRESH').history_id = str(entry.get('id',''))
            op_row.operator('blendair.favorite_history', text='', icon=icon_fav).history_id = str(entry.get('id',''))
            op_row.operator('blendair.copy_history', text='', icon='COPYDOWN').history_id = str(entry.get('id',''))
            op_row.operator('blendair.delete_history', text='', icon='TRASH').history_id = str(entry.get('id',''))
