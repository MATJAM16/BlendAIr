import bpy
import threading
from .prompts import send_prompt
from .utils import safe_exec, get_supabase, enqueue_job

class BLENDAIR_OT_ExecutePrompt(bpy.types.Operator):
    """Send prompt to LLM and execute the returned Python code."""
    bl_idname = "blendair.execute_prompt"
    bl_label = "Run Prompt"
    bl_description = "Sends the current prompt to the selected LLM and executes the returned code"

    @safe_exec
    def execute(self, context):
        scene = context.scene
        prompt = scene.blendair_prompt
        
        if not prompt:
            self.report({'WARNING'}, "Prompt is empty.")
            return {'CANCELLED'}
            
        scene.blendair_status = "Sending prompt..."

        def _run_in_thread():
            """The actual prompt execution, run in a separate thread to avoid blocking the UI."""
            try:
                code = send_prompt(prompt)
                if code:
                    exec(code, {'bpy': bpy})
                    scene.blendair_status = "Success!"
                else:
                    scene.blendair_status = "No code returned from AI."
            except Exception as e:
                scene.blendair_status = f"Error: {e}"
                print(f"BlendAIr Error: {e}")

        thread = threading.Thread(target=_run_in_thread, daemon=True)
        thread.start()
        self.report({'INFO'}, "Prompt sent. Running in background.")
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
        self.report({'INFO'}, "Result pushed to MCP")
        return {'FINISHED'}


class BLENDAIR_OT_RestoreHistory(bpy.types.Operator):
    bl_idname = "blendair.restore_history"
    bl_label = "Restore Prompt State"
    history_id: bpy.props.StringProperty()
    def execute(self, context):
        from . import history
        entries = history.get_prompt_history(limit=100)
        entry = next((e for e in entries if str(e.get('id')) == self.history_id), None)
        if entry:
            context.scene.blendair_prompt = entry.get('prompt','')
            self.report({'INFO'}, "Prompt restored")
        else:
            self.report({'ERROR'}, "History entry not found")
        return {'FINISHED'}

class BLENDAIR_OT_FavoriteHistory(bpy.types.Operator):
    bl_idname = "blendair.favorite_history"
    bl_label = "Favorite Prompt"
    history_id: bpy.props.StringProperty()
    def execute(self, context):
        from . import history
        try:
            history.update_prompt_favorite(self.history_id, True)
            self.report({'INFO'}, "Favorited!")
        except Exception as e:
            self.report({'ERROR'}, f"Favorite failed: {e}")
        return {'FINISHED'}

class BLENDAIR_OT_CopyHistory(bpy.types.Operator):
    bl_idname = "blendair.copy_history"
    bl_label = "Copy Prompt/Response"
    history_id: bpy.props.StringProperty()
    def execute(self, context):
        from . import history
        entries = history.get_prompt_history(limit=100)
        entry = next((e for e in entries if str(e.get('id')) == self.history_id), None)
        if entry:
            text = f"Prompt: {entry.get('prompt','')}\nResponse: {entry.get('response','')}"
            context.window_manager.clipboard = text
            self.report({'INFO'}, "Copied to clipboard")
        else:
            self.report({'ERROR'}, "History entry not found")
        return {'FINISHED'}

class BLENDAIR_OT_DeleteHistory(bpy.types.Operator):
    bl_idname = "blendair.delete_history"
    bl_label = "Delete Prompt History"
    history_id: bpy.props.StringProperty()
    def execute(self, context):
        from . import history
        try:
            history.delete('prompt_history', {'id': f'eq.{self.history_id}'})
            self.report({'INFO'}, "Deleted history entry")
        except Exception as e:
            self.report({'ERROR'}, f"Delete failed: {e}")
        return {'FINISHED'}

class BLENDAIR_OT_GoBackHistory(bpy.types.Operator):
    bl_idname = "blendair.goback_history"
    bl_label = "Go Back to This Point"
    history_id: bpy.props.StringProperty()
    def execute(self, context):
        from . import history
        from . import ui
        prev = history.go_back()
        if prev:
            ui.prompt_bar_state['text'] = prev.get('prompt', '')
            ui.prompt_bar_state['caret'] = len(ui.prompt_bar_state['text'])
            self.report({'INFO'}, "Restored previous prompt.")
        else:
            self.report({'WARNING'}, "No previous prompt to restore.")
        return {'FINISHED'}
