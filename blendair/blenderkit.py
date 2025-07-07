"""
BlenderKit integration for BlendAIr: search, preview, and import BlenderKit assets.
"""
import bpy

BLENDERKIT_API_URL = "https://www.blenderkit.com/api/v1/"

class BLENDAIR_PT_BlenderKitPanel(bpy.types.Panel):
    bl_label = "BlenderKit"
    bl_idname = "BLENDAIR_PT_blenderkit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendAIr'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Search BlenderKit Assets:")
        layout.prop(context.scene, "blendair_bkit_query", text="Query")
        layout.operator("blendair.bkit_search", text="Search")
        layout.template_list("BLENDAIR_UL_BKitAssets", "", context.scene, "blendair_bkit_assets", context.scene, "blendair_bkit_asset_index")
        layout.operator("blendair.bkit_import", text="Import Selected")

class BLENDAIR_OT_BKitSearch(bpy.types.Operator):
    bl_idname = "blendair.bkit_search"
    bl_label = "Search BlenderKit"
    bl_description = "Search BlenderKit asset library by query."

    def execute(self, context):
        query = context.scene.blendair_bkit_query
        # Placeholder: fetch assets via BlenderKit API (requires OAuth or user token for full access)
        # For now, just add a dummy asset
        item = context.scene.blendair_bkit_assets.add()
        item.name = f"Result for '{query}'"
        item.asset_id = "dummy_id"
        self.report({'INFO'}, f"Searched for: {query}")
        return {'FINISHED'}

class BLENDAIR_OT_BKitImport(bpy.types.Operator):
    bl_idname = "blendair.bkit_import"
    bl_label = "Import BlenderKit Asset"
    bl_description = "Import the selected BlenderKit asset into the scene."

    def execute(self, context):
        idx = context.scene.blendair_bkit_asset_index
        if idx < 0 or idx >= len(context.scene.blendair_bkit_assets):
            self.report({'ERROR'}, "No asset selected.")
            return {'CANCELLED'}
        asset = context.scene.blendair_bkit_assets[idx]
        # Placeholder: download/import asset by asset.asset_id
        self.report({'INFO'}, f"Imported asset: {asset.name}")
        return {'FINISHED'}

class BLENDAIR_UL_BKitAssets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)

class BlendAirBKitAsset(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    asset_id: bpy.props.StringProperty()


