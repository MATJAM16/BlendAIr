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
        description="Optional MCP server to fetch project context",
        default="http://localhost:9876",
    )
    gesture_threshold: FloatProperty(
        name="Gesture Threshold",
        description="Confidence threshold for gesture recognition",
        default=0.7,
        min=0.0,
        max=1.0,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "llm_provider")
        if self.llm_provider == 'blendair_cloud':
            layout.prop(self, "blendair_api_key")
            layout.operator('wm.url_open', text="Get API Key (BlendAIr Cloud)").url = "https://your-blendair-payment-portal.com"
        elif self.llm_provider == 'openai':
            layout.prop(self, "openai_api_key")
            layout.label(text="Get your key at https://platform.openai.com/")
        elif self.llm_provider == 'gemini':
            layout.prop(self, "gemini_api_key")
            layout.label(text="Get your key at https://ai.google.dev/")
        elif self.llm_provider == 'huggingface':
            layout.prop(self, "huggingface_api_key")
            layout.label(text="Get your key at https://huggingface.co/settings/tokens")
        elif self.llm_provider == 'grok':
            layout.prop(self, "grok_api_key")
            layout.label(text="Get your key at https://grok.x.ai/")
        elif self.llm_provider == 'deepseek':
            layout.prop(self, "deepseek_api_key")
            layout.label(text="Get your key at https://platform.deepseek.com/")
        elif self.llm_provider == 'local':
            layout.prop(self, "local_llm_endpoint")
        layout.separator()
        layout.prop(self, "supabase_url")
        layout.prop(self, "supabase_key")
        layout.prop(self, "mcp_url")
        layout.prop(self, "gesture_threshold")


# registration helpers
classes = [BlendAirPreferences]

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
