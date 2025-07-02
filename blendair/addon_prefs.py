import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, FloatProperty, PointerProperty


def get_pref():
    return bpy.context.preferences.addons[__package__].preferences  # type: ignore


class BlendAirPreferences(AddonPreferences):
    bl_idname = __package__

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
    llm_endpoint: StringProperty(
        name="LLM Endpoint",
        description="HTTP endpoint returning Python script for prompt",
        default="http://localhost:8000/generate",
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
        layout.prop(self, "supabase_url")
        layout.prop(self, "supabase_key")
        layout.prop(self, "llm_endpoint")
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
