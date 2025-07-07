"""Pytest configuration for BlendAIr.

This file installs a minimal *fake* version of Blender's ``bpy`` module so that
unit tests can import the add-on package in a plain CPython environment
(GitHub Actions, local pytest, etc.).

Only the pieces of the API that the add-on touches during module import need to
exist. Everything else can be simple no-op stubs.  The goal is *not* to unit-
test Blender itself – just to prevent ``ModuleNotFoundError: bpy`` during test
collection.
"""

from types import ModuleType, SimpleNamespace
import sys

# -----------------------------------------------------------------------------
# Helper factories
# -----------------------------------------------------------------------------

def _void_function(*_args, **_kwargs):
    """A placeholder that does absolutely nothing."""
    return None


def _make_props_module() -> ModuleType:
    """Return a fake ``bpy.props`` module with the common property factories."""
    props_mod = ModuleType("bpy.props")
    # Common property factory functions used by add-ons.
    for _name in (
        "StringProperty",
        "BoolProperty",
        "EnumProperty",
        "PointerProperty",
        "IntProperty",
        "FloatProperty",
    ):
        setattr(props_mod, _name, lambda *_, **__: None)
    return props_mod


def _make_types_module() -> ModuleType:
    """Return a fake ``bpy.types`` module with the base classes."""
    types_mod = ModuleType("bpy.types")

    # Create minimal base classes with a fake ``bl_rna`` attribute so that
    # ``isinstance(cls.bl_rna, bpy.types.BlendRNA)`` checks don’t explode.
    base_cls_names = [
        "PropertyGroup",
        "Operator",
        "Panel",
        "UIList",
        "AddonPreferences",
        "Header",
        "Menu",
    ]
    for _name in base_cls_names:
        _cls = type(_name, (object,), {"bl_rna": SimpleNamespace()})
        setattr(types_mod, _name, _cls)

    # Scene is used for PointerProperty attachments – just needs to exist.
    types_mod.Scene = type("Scene", (object,), {})
    return types_mod


def _make_utils_module() -> ModuleType:
    """Return a fake ``bpy.utils`` module with register/unregister helpers."""
    utils_mod = ModuleType("bpy.utils")
    utils_mod.register_class = _void_function
    utils_mod.unregister_class = _void_function
    return utils_mod


def _install_fake_bpy():
    """Assemble and register the fake ``bpy`` package into ``sys.modules``."""
    bpy_mod = ModuleType("bpy")
    bpy_mod.__dict__.update(
        {
            "props": _make_props_module(),
            "types": _make_types_module(),
            "utils": _make_utils_module(),
            "data": SimpleNamespace(),
            "context": SimpleNamespace(scene=SimpleNamespace()),
            "ops": SimpleNamespace(),
            "app": SimpleNamespace(tempdir="/tmp"),
        }
    )

    # Register the main module and its submodules so that ``importlib`` can find
    # them when statements like ``from bpy import types`` or
    # ``from bpy.props import StringProperty`` are executed.
    sys.modules["bpy"] = bpy_mod
    sys.modules["bpy.props"] = bpy_mod.props
    sys.modules["bpy.types"] = bpy_mod.types
    sys.modules["bpy.utils"] = bpy_mod.utils


# -----------------------------------------------------------------------------
# Pytest entry-point
# -----------------------------------------------------------------------------

_install_fake_bpy()
