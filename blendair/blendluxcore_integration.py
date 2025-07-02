"""Setup BlendLuxCore render engine and simple headless render helper."""
import bpy
from pathlib import Path

def ensure_blendluxcore():
    if bpy.context.scene.render.engine != 'LUXCORE':
        bpy.context.scene.render.engine = 'LUXCORE'
        # set basic settings
        bpy.context.scene.luxcore.config.log_level = 'WARNING'


def render_to_file(filepath: str):
    ensure_blendluxcore()
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)


def register():
    pass

def unregister():
    pass
