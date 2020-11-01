# -*- coding:utf-8 -*-

'''
#Thanks to Osama Arafa's Camera_SwitchMenu, Help me learned to call ops in ops
#Thanks xVan for helping me with the camera'view undo option
#Thanks Bookyakuno for helping me add keymap (https://blenderartists.org/t/keymap-for-addons/685544/19?u=atticus_lv)
'''

bl_info = {
    "name": "Smart Scene Manager",
    "author": "Atticus",
    "version": (0, 1, 7,1),
    "blender": (2, 83, 2),
    "location": "3D View > Object mode > Shortcut 'F' / Side Menu > Edit",
    "description": "An elegant way to set up your scene",
    "doc_url": "https://atticus-lv.github.io/SSM_document/",
    "category": "Object",
}


from .Ui_Menu import *
from .Ops_Cam import *
from .Ops_Move_obj import *
from .Ops_Extra import *
from .Ops_ModifyCam import *
from .Ops_Light import *
from .Ops_ListManager import *
from .Ops_Materials import *
from .Ui_Translations import *

from .Props import *

import bpy
import rna_keymap_ui
from bpy.props import *
from .Ops_Extra import CN_ON


panels = (
    SSM_PT_SideMenu, SSM_PT_SideObjInfo,
        )

def update_categort(self, context):
    message = "Smart Scene Manager : Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass

#
# ___  ____ ____ ____
# |__] |__/ |___ |___
# |    |  \ |___ |
#
#

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    #change draw
    settings:EnumProperty(
        name="enumprop_pref",
        items=[('MENU', 'Menu', ''), ('PROPERTIES', 'Properties', ''), ('KEYMAP', 'Keymap', '')],
        default='MENU'
    )
    category: StringProperty(name="Tab Category",
        description="Choose a name for the category of the panel",
        default="Edit",
        update=update_categort
    )
    # list manager
    list_type:EnumProperty(
        items=[('IMAGE', 'Image', 'Use image manager',"TEXTURE",0), ('MAT', 'Materials', 'Use material manager',"MATERIAL_DATA",1)],
        default='MAT'
    )

    filter_tpye: EnumProperty(
        items=[('NONE', 'None', ''), ('FAKE', 'Fake User', ''), ('NOUSER', 'No User', '')],
        default='NONE'
    )

    LIST_MG: BoolProperty(name="List Manager", default=False)
    Picker_mode: BoolProperty(name="Picker Mode", default=False)

    # menu setting
    PIE_MENU:BoolProperty(name="Enable Pie Menu", default=True)
    SIDE_MENU:BoolProperty(name="Enable Side Menu", default=True)
    SM_sub:BoolProperty(name="Object Data",default=True)

    # Side Panel
    openCam: BoolProperty(default=False)
    openMove: BoolProperty(default=False)

    #light group
    LG: BoolProperty(name="LightGroup", default=False)

    #export setting
    tempdir:StringProperty(name="Temppath",description="Temp Path")
    usecustom:BoolProperty(name="Use Custom",default = False)
    usedate: BoolProperty(name="Date", default=True)
    usetime: BoolProperty(name="Time", default=True)
    usenum: BoolProperty(name="Time", default=True)
    useactiveN: BoolProperty(name="ActiveName", default=True)

    #popwindow setting
    usePop: BoolProperty(name="Use Popup Window",default=False)
    RX: IntProperty(name="Resolution X",default= 1200)
    RY: IntProperty(name="Resolution Y",default= 800)

    #cam setting
    camlens:IntProperty(name="Focal Length",default= 50)
    useCamName:BoolProperty(name="Use Name",default=True)

    #transPSR
    Tp:BoolProperty(name="Location",default=True)
    Ts:BoolProperty(name="Scale",default=False)
    Tr:BoolProperty(name="Rotation",default=False)

    #D2F
    OM:BoolProperty(name="Only Mesh",default=False)


    def draw(self, context):
        CNON = CN_ON(context)
        layout = self.layout

        col = layout.column()
        row = col.row(align=True)
        row.prop(self, 'settings', expand=True)

        col.separator()

        def drawmenu(col):
            pref = context.preferences.addons[__package__].preferences
            col = col.box()
            row = col.row(align=True)

            id = 0 if CNON else 1

            T_list = [
                ["使用侧边栏菜单","Use Side Menu"],
                ['中文手册','Update'],
                ["https://atticus-lv.gitee.io/ssm_document/","https://atticus-lv.github.io/SSM_document/changelog/"],
                ["物体信息面板","Object Info "],
                ["选项卡位置","Tab Category"],
                ["使用饼菜单","Use Pie"],
                ["材质拾取（使用弹窗","Mat Picker(Use pop window)"],
            ]

            row.prop(self, "SIDE_MENU", text='', icon='PRESET')
            row.label(text=T_list[0][id])
            sub = row.row()
            sub.scale_x = 0.5
            sub.operator('wm.url_open',text=T_list[1][id],icon = 'URL').url = T_list[2][id]

            if pref.SIDE_MENU:
                box = col.box()
                row = box.row(align=True)
                row.label(text=T_list[3][id], icon='OBJECT_DATA')
                row.prop(self, "SM_sub", text="")
                row = box.row(align=True)
                row.prop(self, "category", text=T_list[4][id])

            row = col.row(align=True)
            row.prop(self, "PIE_MENU",text='', icon='ANTIALIASED')
            row.label(text=T_list[5][id])

            row = col.row(align=True)
            row.prop(self, 'usePop', text="", icon='TOPBAR')
            row.label(text=T_list[6][id])

            if pref.usePop :
                row = col.row(align=True)
                row.prop(self, "RX")
                row.prop(self, "RY")

            row = col.row(align=True)
            row.prop(self, 'LG', text='', icon="GROUP")
            row.label(text="Light Group (Experimental)")


        def drawProperties(col):

            id = 0 if CNON else 1

            T_list = [
                ["添加相机","Add Cam"],
                ["使用名字","Use Name"],
                ["位置转移","TransPSR"],

            ]

            col.label(text=T_list[0][id], icon='VIEW_CAMERA')
            row = col.row(align=True)
            row.separator();row.separator();row.separator()
            row.prop(self, "camlens")
            row.label(text="mm")
            row.prop(self, T_list[1][id],text = "使用名字")

            #trans psr
            col.label(text=T_list[2][id], icon='CON_LOCLIKE')

            row = col.row(align=True)

            row.separator()
            row.separator()
            row.separator()

            row.prop(self, "Tp",icon ="ORIENTATION_GLOBAL")
            row.prop(self, "Ts",icon = "ORIENTATION_LOCAL")
            row.prop(self, "Tr",icon = "ORIENTATION_GIMBAL")

            row.separator()
            row.separator()
            row.separator()

            #export
            col.label(text="Export", icon='FOLDER_REDIRECT')
            row = col.row(align=True)
            row.prop(self,"tempdir", text="Output Path")
            row.operator('buttons.directory_browse',icon ='FILEBROWSER',text = '')
            row.prop(self, "usecustom", text="",icon ='CHECKMARK')

            row = col.row(align=False)
            row.label(text="Name",)
            row.prop(self, "useactiveN", text="Active Object")
            row.prop(self, "usenum", text="Count")
            row.prop(self, "usedate", text="Date")
            row.prop(self, "usetime", text="Time")


        def drawKeymap(col):
            col = col.box()
            col = col.column()
            # col.label(text="Keymap", icon="KEYINGSET")

            wm = bpy.context.window_manager
            kc = wm.keyconfigs.user
            old_km_name = ""
            get_kmi_l = []
            for km_add, kmi_add in addon_keymaps:
                for km_con in kc.keymaps:
                    if km_add.name == km_con.name:
                        km = km_con
                        break

                for kmi_con in km.keymap_items:
                    if kmi_add.idname == kmi_con.idname:
                        if kmi_add.name == kmi_con.name:
                            get_kmi_l.append((km, kmi_con))

            get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

            for km, kmi in get_kmi_l:
                if not km.name == old_km_name:
                    col.label(text=str(km.name), icon="DOT")
                    pass
                col.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

                old_km_name = km.name


        #Excute
        if context.preferences.addons[__package__].preferences.settings == 'MENU':
            drawmenu(col)

        if context.preferences.addons[__package__].preferences.settings == 'PROPERTIES':
            col = col.box()
            drawProperties(col)

        if context.preferences.addons[__package__].preferences.settings == 'KEYMAP':
            drawKeymap(col)

#
# ____ _    ____ ____ ____
# |    |    |__| [__  [__
# |___ |___ |  | ___] ___]
#
#

classes = (
    # Preferences
    AddonPreferences,
    # Props
    SSM_CameraProps, SSM_LightProps,
    # Menu
    SSM_MT_PieMenu, SSM_MT_Select, SSM_MT_AlignMenu, SSM_PT_SideMenu, SSM_PT_SideObjInfo,
    # Ops_Cam
    ActiveCam, FlipCam, AddViewCam, focusPicker,
    # Ops_ModifyCam
    CamSetEV, SSM_PT_CameraSwitcher, CamList, SceneSetEV,
    # Ops_Move_obj
    OBJECT_OT_Drop2floor, OBJECT_OT_TransPSR, OBJECT_OT_LookAT,
    PANEL_PT_TransPanel, PANEL_PT_D2fPanel,
    # Ops_Extra
    ExportObj, Translater, LightCheck,
    # light group
    ToggleLightGroup, SSM_OT_CreatLightGroup, SSM_OT_RenameLightGroup, SSM_OT_SoloGroup, SSM_OT_ResetGroupSolo,
    RemoveLightGroup,SSM_OT_SoloSingle,ActiveLight,
    # Image Manager
    IMAGE_OT_Remove, SSM_UL_ImageList, SSM_OT_Pack, SSM_OT_RemoveUnused,PopImageEditor,
    #mat
    SSM_OT_Remove_By_Filter, SSM_OT_Material_Picker, SSM_PickerMatProps, SSM_UL_MatList,SSM_OT_Remove_Single_Mat,
    PICKER_OT_AddMat, PICKER_OT_RemoveMat, PICKER_OT_clearList,PICKER_UL_MatList,
    PopShaderEditor,
)

#
# ____ ____ ____ _ ____ ___ ____ ____
# |__/ |___ | __ | [__   |  |___ |__/
# |  \ |___ |__] | ___]  |  |___ |  \
#
#

addon_keymaps = []


def addKeymap():
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'F', 'PRESS')
        kmi.properties.name = "SSM_MT_PieMenu"
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Mesh')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'A', 'PRESS')
        kmi.properties.name = "SSM_MT_Select"
        addon_keymaps.append((km, kmi))


def removeKeymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    PropsADD()
    #add keymap
    addKeymap()
    # add menu
    bpy.types.VIEW3D_MT_camera_add.append(add_cam_menu)
    # translate
    bpy.app.translations.register(__name__, Ui_Translations.translations_dict)


def unregister():
    # translate
    bpy.app.translations.unregister(__name__)
    # remove menu
    bpy.types.VIEW3D_MT_camera_add.remove(add_cam_menu)

    for cls in classes:
        bpy.utils.unregister_class(cls)

    removeKeymap()

    Proposremove()


if __name__ == "__main__":
    register()
