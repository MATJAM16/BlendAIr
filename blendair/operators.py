import bpy
import requests
import textwrap
from .utils import enqueue_job, get_supabase
from .addon_prefs import get_pref


class BLENDAIR_OT_ExecutePrompt(bpy.types.Operator):
    """Send prompt to LLM endpoint and execute returned code"""
    bl_idname = "blendair.execute_prompt"
    bl_label = "Execute Prompt"

    prompt: bpy.props.StringProperty(name="Prompt", default="Rotate 15 degrees")

    def execute(self, context):
        prefs = get_pref()
        try:
            resp = requests.post(prefs.llm_endpoint, json={"prompt": self.prompt}, timeout=30)
            resp.raise_for_status()
            code = resp.json().get("script", "")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to fetch script: {e}")
            return {'CANCELLED'}
        # Basic sandbox: dedent and disallow import os, subprocess
        safe_code = textwrap.dedent(code)
        if any(bad in safe_code for bad in ["import os", "import subprocess", "open("]):
            self.report({'ERROR'}, "Unsafe code detected")
            return {'CANCELLED'}
        # schedule code execution
        enqueue_job({"func": exec, "args": (safe_code,)})
        self.report({'INFO'}, "Prompt queued")
        return {'FINISHED'}


class BLENDAIR_OT_UploadModel(bpy.types.Operator):
    bl_idname = "blendair.upload_model"
    bl_label = "Upload Current Model"

    def execute(self, context):
        supabase = get_supabase()
        if not supabase:
            self.report({'ERROR'}, "Supabase not configured")
            return {'CANCELLED'}
        temp_path = bpy.path.abspath("//temp_export.obj")
        bpy.ops.export_scene.obj(filepath=temp_path, use_selection=False)
        data = open(temp_path, "rb").read()
        supabase.storage.from_("input_models").upload("model.obj", data, upsert=True)
        self.report({'INFO'}, "Model uploaded")


class BLENDAIR_OT_DownloadModel(bpy.types.Operator):
    bl_idname = "blendair.download_model"
    bl_label = "Download Latest Model"

    def execute(self, context):
        supabase = get_supabase()
        if not supabase:
            self.report({'ERROR'}, "Supabase not configured")
            return {'CANCELLED'}
        try:
            res = supabase.storage.from_("output_models").download("model.obj")
            path = bpy.path.abspath("//downloaded.obj")
            with open(path, "wb") as f:
                f.write(res)
            bpy.ops.import_scene.obj(filepath=path)
            self.report({'INFO'}, "Model downloaded & imported")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Download failed: {e}")
            return {'CANCELLED'}


class BLENDAIR_OT_Render(bpy.types.Operator):
    bl_idname = "blendair.render"
    bl_label = "Render with LuxCore"

    def execute(self, context):
        from .blendluxcore_integration import render_to_file
        path = bpy.path.abspath("//render.png")
        enqueue_job({"func": render_to_file, "args": (path,)})
        self.report({'INFO'}, "Render queued")
        return {'FINISHED'}


class BLENDAIR_OT_MCPFetch(bpy.types.Operator):
    bl_idname = "blendair.mcp_fetch"
    bl_label = "Fetch Context via MCP"

    def execute(self, context):
        from .mcp_client import BlenderMCPClient
        client = BlenderMCPClient()
        ctx = client.get_context(project_id="demo")
        print("Fetched context:", ctx)
        return {'FINISHED'}


class BLENDAIR_OT_MCPUpdate(bpy.types.Operator):
    bl_idname = "blendair.mcp_update"
    bl_label = "Push Result to MCP"

    def execute(self, context):
        from .mcp_client import BlenderMCPClient
        client = BlenderMCPClient()
        client.push_result(job_id="demo", payload={"status": "done"})
        return {'FINISHED'}
        return {'FINISHED'}


classes = [
    BLENDAIR_OT_ExecutePrompt,
    BLENDAIR_OT_UploadModel,
    BLENDAIR_OT_DownloadModel,
    BLENDAIR_OT_Render,
    BLENDAIR_OT_MCPFetch,
    BLENDAIR_OT_MCPUpdate,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
