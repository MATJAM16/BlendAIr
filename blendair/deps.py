import bpy
import subprocess
import sys
from bpy.props import BoolProperty

REQUIRED_PACKAGES = [
    'supabase',
    'blendluxcore',
    'mediapipe',
    'opencv-python',
]

def check_and_prompt_install():
    missing = [pkg for pkg in REQUIRED_PACKAGES if not _is_installed(pkg)]
    if missing:
        def install_cb(self, context):
            for pkg in missing:
                _pip_install(pkg)
            self.report({'INFO'}, "BlendAIr: Installed missing dependencies. Please restart Blender.")
        bpy.context.window_manager.popup_menu(
            lambda self, ctx: self.layout.operator('wm.blendair_install_missing', text=f"Install: {', '.join(missing)}"),
            title="BlendAIr: Missing Python Packages", icon='ERROR')

class BLENDAIR_OT_InstallMissing(bpy.types.Operator):
    bl_idname = "wm.blendair_install_missing"
    bl_label = "Install Missing Packages"
    def execute(self, context):
        for pkg in REQUIRED_PACKAGES:
            if not _is_installed(pkg):
                _pip_install(pkg)
        self.report({'INFO'}, "Installed missing dependencies. Please restart Blender.")
        return {'FINISHED'}

def _is_installed(pkg):
    try:
        __import__(pkg)
        return True
    except ImportError:
        return False

def _pip_install(pkg):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

def register():
    bpy.utils.register_class(BLENDAIR_OT_InstallMissing)

def unregister():
    bpy.utils.unregister_class(BLENDAIR_OT_InstallMissing)
