import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, FloatProperty, EnumProperty, PointerProperty


def get_pref():
    return bpy.context.preferences.addons[__package__].preferences  # type: ignore


class BlendAirPreferences(AddonPreferences):
    bl_idname = __package__

    llm_provider: EnumProperty(
        name="LLM Provider",
        description="Choose which LLM service to use for prompts.",
        items=[
            ('blendair_cloud', 'Blend(AI)r Cloud', 'Use Blend(AI)r paid cloud service'),
            ('openai', 'OpenAI', 'Use your own OpenAI API key'),
            ('gemini', 'Gemini', 'Use your own Gemini API key'),
            ('huggingface', 'HuggingFace', 'Use your own HuggingFace Inference API key'),
            ('grok', 'Grok', 'Use your own Grok API key'),
            ('deepseek', 'DeepSeek', 'Use your own DeepSeek API key'),
            ('local', 'Local (Ollama/LM Studio)', 'Use a local LLM server'),
        ],
        default='blendair_cloud',
    )
    blendair_api_key: StringProperty(
        name="Blend(AI)r Cloud API Key",
        description="Your pay-as-you-go API key for Blend(AI)r Cloud.",
        subtype="PASSWORD",
        default="",
    )
    openai_api_key: StringProperty(
        name="OpenAI API Key",
        description="Your OpenAI API key.",
        subtype="PASSWORD",
        default="",
    )
    gemini_api_key: StringProperty(
        name="Gemini API Key",
        description="Your Gemini API key.",
        subtype="PASSWORD",
        default="",
    )
    huggingface_api_key: StringProperty(
        name="HuggingFace API Key",
        description="Your HuggingFace Inference API key.",
        subtype="PASSWORD",
        default="",
    )
    local_llm_endpoint: StringProperty(
        name="Local LLM Endpoint",
        description="HTTP endpoint for your local LLM server (e.g., Ollama)",
        default="http://localhost:8000/generate",
    )
    local_llm_model: StringProperty(
        name="Local LLM Model",
        description="Model name for local LLM (Ollama/LM Studio)",
        default="llama3",
    )
    local_llm_context: FloatProperty(
        name="Context Window",
        description="Context window size for local LLM",
        default=4096,
        min=256,
        max=32768,
    )
    local_llm_timeout: FloatProperty(
        name="Timeout (s)",
        description="Request timeout for local LLM",
        default=30.0,
        min=1.0,
        max=300.0,
    )
    grok_api_key: StringProperty(
        name="Grok API Key",
        description="Your Grok API key.",
        subtype="PASSWORD",
        default="",
    )
    deepseek_api_key: StringProperty(
        name="DeepSeek API Key",
        description="Your DeepSeek API key.",
        subtype="PASSWORD",
        default="",
    )
    supabase_url: StringProperty(
        name="Supabase URL",
        description="Your Supabase project URL",
        default="https://YOURPROJECT.supabase.co",
    )
    supabase_key: StringProperty(
        name="Supabase Anon/public key",
        description="Supabase API key",
        subtype="PASSWORD",
        default="",
    )
    mcp_url: StringProperty(
        name="BlenderMCP Server URL",
        description="BlenderMCP server URL",
        default="http://localhost:5000/",
    )
    gesture_threshold: FloatProperty(
        name="Gesture Threshold",
        description="Minimum confidence for gesture recognition",
        default=0.7,
        min=0.0,
        max=1.0,
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Large Language Model Provider:")
        col.prop(self, "llm_provider", text="Provider")
        provider = self.llm_provider
        # Provider-specific fields
        if provider == 'blendair_cloud':
            col.prop(self, "blendair_api_key")
            col.operator("blendair.test_key", text="Test Blend(AI)r Key").provider = 'blendair_cloud'
        elif provider == 'openai':
            col.prop(self, "openai_api_key")
            col.operator("blendair.test_key", text="Test OpenAI Key").provider = 'openai'
            col.prop(self, "local_llm_model", text="Model")
            col.prop(self, "local_llm_context", text="Context Window")
            col.prop(self, "local_llm_timeout", text="Timeout (s)")
        elif provider == 'gemini':
            col.prop(self, "gemini_api_key")
            col.operator("blendair.test_key", text="Test Gemini Key").provider = 'gemini'
        elif provider == 'huggingface':
            col.prop(self, "huggingface_api_key")
            col.operator("blendair.test_key", text="Test HuggingFace Key").provider = 'huggingface'
        elif provider == 'grok':
            col.prop(self, "grok_api_key")
            col.operator("blendair.test_key", text="Test Grok Key").provider = 'grok'
        elif provider == 'deepseek':
            col.prop(self, "deepseek_api_key")
            col.operator("blendair.test_key", text="Test DeepSeek Key").provider = 'deepseek'
        elif provider == 'local':
            col.prop(self, "local_llm_endpoint")
            col.prop(self, "local_llm_model", text="Model")
            col.prop(self, "local_llm_context", text="Context Window")
            col.prop(self, "local_llm_timeout", text="Timeout (s)")
            col.operator("blendair.test_key", text="Test Local LLM").provider = 'local'
        col.separator()
        col.label(text="Supabase Configuration:")
        col.prop(self, "supabase_url")
        col.prop(self, "supabase_key")
        col.operator("blendair.test_supabase", text="Test Supabase")
        col.separator()
        col.label(text="BlenderMCP Server:")
        col.prop(self, "mcp_url")
        col.prop(self, "gesture_threshold")


# registration helpers
class BlendAirTestKeyOperator(bpy.types.Operator):
    bl_idname = "blendair.test_key"
    bl_label = "Test API Key"
    provider: bpy.props.StringProperty()
    def execute(self, context):
        import requests
        prefs = context.preferences.addons[__package__].preferences
        try:
            if self.provider == 'openai':
                key = prefs.openai_api_key
                r = requests.get(
                    'https://api.openai.com/v1/models',
                    headers={'Authorization': f'Bearer {key}'}
                )
                if r.status_code == 200:
                    self.report({'INFO'}, "OpenAI key valid!")
                else:
                    self.report({'ERROR'}, f"OpenAI key invalid: {r.status_code}")
            elif self.provider == 'gemini':
                key = prefs.gemini_api_key
                r = requests.get(
                    f'https://generativelanguage.googleapis.com/v1beta/models?key={key}'
                )
                if r.status_code == 200:
                    self.report({'INFO'}, "Gemini key valid!")
                else:
                    self.report({'ERROR'}, f"Gemini key invalid: {r.status_code}")
            elif self.provider == 'huggingface':
                key = prefs.huggingface_api_key
                r = requests.get(
                    'https://huggingface.co/api/whoami-v2',
                    headers={'Authorization': f'Bearer {key}'}
                )
                if r.status_code == 200:
                    self.report({'INFO'}, "HuggingFace key valid!")
                else:
                    self.report({'ERROR'}, f"HuggingFace key invalid: {r.status_code}")
            elif self.provider == 'anthropic':
                key = getattr(prefs, 'anthropic_api_key', None)
                if not key:
                    self.report({'ERROR'}, "Anthropic key not set")
                    return {'CANCELLED'}
                r = requests.get(
                    'https://api.anthropic.com/v1/models',
                    headers={'x-api-key': key}
                )
                if r.status_code == 200:
                    self.report({'INFO'}, "Anthropic key valid!")
                else:
                    self.report({'ERROR'}, f"Anthropic key invalid: {r.status_code}")
            else:
                self.report({'WARNING'}, f"No test implemented for {self.provider}")
        except Exception as e:
            self.report({'ERROR'}, f"Key test failed: {e}")
        return {'FINISHED'}

class BlendAirTestSupabaseOperator(bpy.types.Operator):
    bl_idname = "blendair.test_supabase"
    bl_label = "Test Supabase"
    def execute(self, context):
        from . import supabase_client
        prefs = context.preferences.addons[__package__].preferences
        supabase_client.set_supabase_creds(prefs.supabase_url, prefs.supabase_key)
        ok = supabase_client.test_supabase()
        if ok:
            self.report({'INFO'}, "Supabase connection successful")
        else:
            self.report({'ERROR'}, "Supabase test failed")
        return {'FINISHED'}

# registration helpers
class BlendAirOnboardingOperator(bpy.types.Operator):
    bl_idname = "blendair.onboarding"
    bl_label = "Welcome to BlendAIr!"
    def execute(self, context):
        context.scene.blendair_onboarding_complete = True
        self.report({'INFO'}, "Onboarding complete!")
        return {'FINISHED'}

operator_classes = [BlendAirTestKeyOperator, BlendAirTestSupabaseOperator, BlendAirOnboardingOperator]

def register():
    for cls in operator_classes:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(BlendAirPreferences)

def unregister():
    for c in reversed(operator_classes):
        bpy.utils.unregister_class(c)
    bpy.utils.unregister_class(BlendAirPreferences)
