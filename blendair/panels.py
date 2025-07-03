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
        # LLM provider dropdown
        layout.label(text="LLM Provider:")
        layout.prop(prefs, "llm_provider", text="")
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


classes = [BLENDAIR_PT_MainPanel]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    # Custom scene properties
    bpy.types.Scene.blendair_project = bpy.props.StringProperty(name="Project ID", default="demo")
    bpy.types.Scene.blendair_prompt = bpy.props.StringProperty(name="Prompt", default="Rotate 15 degrees")
    bpy.types.Scene.blendair_use_mcp = bpy.props.BoolProperty(name="Use MCP", default=False)


def unregister():
    del bpy.types.Scene.blendair_project
    del bpy.types.Scene.blendair_prompt
    del bpy.types.Scene.blendair_use_mcp
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
