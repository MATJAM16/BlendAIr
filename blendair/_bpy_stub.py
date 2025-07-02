"""A minimal stub of the `bpy` module so the package can be imported
outside Blender (e.g. in CI tests). It only implements the tiny subset
needed by our add-on code. Extend as necessary.
"""
import types
import sys

bpy = types.ModuleType("bpy")
# props sub-module with dummy property factories
props = types.ModuleType("bpy.props")

def _dummy_prop(*args, **kwargs):
    return None

for name in (
    "StringProperty",
    "BoolProperty",
    "FloatProperty",
):
    setattr(props, name, _dummy_prop)

bpy.props = props  # type: ignore

# minimal utils namespace
utils = types.ModuleType("bpy.utils")

def _nop(*args, **kwargs):
    return None

utils.register_class = _nop  # type: ignore
utils.unregister_class = _nop  # type: ignore
bpy.utils = utils  # type: ignore

# dummy context preferences object chain for addon_prefs
class _Prefs:
    addons: dict = {}

class _Context:
    preferences = types.SimpleNamespace(addons={})

bpy.context = _Context()  # type: ignore

# placeholder for ops namespace used in operators
ops = types.ModuleType("bpy.ops")
ops.export_scene = types.SimpleNamespace(obj=_nop)
ops.import_scene = types.SimpleNamespace(obj=_nop)
ops.render = types.SimpleNamespace(render=_nop)

bpy.ops = ops  # type: ignore

# path helper
class _Path:
    @staticmethod
    def abspath(path):
        return "./" + path.strip("/")

bpy.path = _Path()  # type: ignore

# scene placeholder for render engine switching
class _Scene:
    render = types.SimpleNamespace(engine="BLENDER_EEVEE", filepath="")
    luxcore = types.SimpleNamespace(config=types.SimpleNamespace(log_level="INFO"))

class _Data:
    scenes = [_Scene()]

bpy.data = _Data()  # type: ignore
bpy.context.scene = _Scene()  # type: ignore

sys.modules["bpy"] = bpy
