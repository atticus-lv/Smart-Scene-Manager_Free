# -*- coding:utf-8 -*-

bl_info = {
    "name": "Little Function",
    "author": "Atticus",
    "version": (0, 30),
    "blender": (2, 83, 1),
    "location": " 3D View > Object mode > Shortcut 'F' ",
    "description": "some small useful tool",
    "category": "Interface",
}


from .UI import LF_Menu
from .CamOPS import AddViewCam, FilpCam, ActiveCam,SetCamA,focusPicker
from .D2FOPS import Drop2floor
from .otherOPS import Translater, ExportObj,TransPSR,LightCheck

import bpy

classes = (
    LF_Menu,
    ActiveCam,FilpCam,AddViewCam,SetCamA,focusPicker,
    Drop2floor,
    ExportObj,Translater,TransPSR,LightCheck
)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # menu shortcuts
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
        #km = wm.keyconfigs.addon.keymaps.new(name='Object Mode')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'F', 'PRESS')
        kmi.properties.name = "LF_Menu"
        addon_keymaps.append((km, kmi))


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    # menu shortcuts
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
    #bpy.ops.wm.call_menu_pie(name="LF_Menu")















