import sys
from unittest.mock import MagicMock

# This is a mock of the bpy module, used for running tests outside of Blender.
# It prevents ModuleNotFoundError when the add-on's code is imported.

class Mockbpy:
    """A mock class for the bpy module."""
    def __init__(self):
        self.props = MagicMock()
        self.types = MagicMock()
        self.utils = MagicMock()
        self.data = MagicMock()
        self.context = MagicMock()
        self.ops = MagicMock()

        # Mocking the registration system requires faking the 'bl_rna' attribute
        # on base classes that the add-on uses for registration.
        self.types.PropertyGroup.bl_rna = MagicMock()
        self.types.Operator.bl_rna = MagicMock()
        self.types.Panel.bl_rna = MagicMock()
        self.types.UIList.bl_rna = MagicMock()
        self.types.AddonPreferences.bl_rna = MagicMock()
        self.types.Header.bl_rna = MagicMock()
        self.types.Menu.bl_rna = MagicMock()

        # Mock the Scene type, as properties are attached to it.
        self.types.Scene = type('Scene', (object,), {})

# When tests are run, 'import bpy' will now import our mock instead of failing.
sys.modules["bpy"] = Mockbpy()
