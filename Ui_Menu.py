#-*- coding =utf-8 -*-
import bpy
from bpy.props import *
from bpy.types import Menu,Panel,AddonPreferences
from .Ops_Light import getlight

# shift a menu

def add_cam_menu(self, context):
    # add menu
    if context.mode == 'OBJECT':
        self.layout.operator("object.add_view_camera",icon='VIEW_CAMERA',text = "Add View Cam")

# object menu

def draw_MESH(box, context):
    row = box.row(align=True)
    row.prop(context.object.data, "use_auto_smooth", text="Auto Smooth")
    row.prop(context.object.data, "auto_smooth_angle", text="Angle")
    try:
        row = box.row(align=True)
        row.scale_x = 1.5
        row.prop(context.object.modifiers["Subdivision"], "show_on_cage", text="")
        row.prop(context.object.modifiers["Subdivision"], "show_in_editmode", text="")
        row.prop(context.object.modifiers["Subdivision"], "show_viewport", text="")
        row.prop(context.object.modifiers["Subdivision"], "show_render", text="")
        box.separator()
        box.prop(context.object.modifiers["Subdivision"], "levels", text="Levels Viewport")
    except:
        pass


def draw_CAMERA(box, context):
    box.prop(context.object.data, "lens", text="Lens")
    box.prop(context.object.data, "passepartout_alpha", text="Opacity")
    box.prop(context.object.data.dof, "aperture_fstop", text="F-Stop")
    box.prop(context.object.ssm_cam, "EV", text="EV", slider=True)
    box.label(text='Resolution')

    if context.scene.camera:
        sub = box.row(align=True)
        sub.prop(context.object.ssm_cam, 'Rx', text='X')
        sub.prop(context.object.ssm_cam, 'Ry', text='Y')
        box.prop(context.object.ssm_cam, "XYscale", text="%", slider=True)


def draw_LIGHT(box, context):
    row = box.row(align=True)
    row.prop(context.object.data, "type", text="Type", expand=True)
    box = box.split().column()
    row = box.row(align=True)
    row.prop(context.object.data, "energy", text="")
    row.prop(context.object.data, "color", text="")
    box.separator()
    box.prop(context.object.ssm_light,"Group",text = "Group")


def draw_EMPTY(box, context):
    box.prop(context.object, "empty_display_type", text="")
    box.prop(context.object, "empty_display_size", text="Size")


def draw_CURVE(box, context):
    box.prop(context.object.data, "bevel_depth", text="Depth")
    box.prop(context.object.data, "bevel_resolution", text="Resolution")
    box.prop(context.object.data, "bevel_object", text="")
    box.prop(context.object.data, "use_fill_caps", text="Fill Caps")


def Obj_Info_UI(self,context,pie):
    col = pie.split().column()

    objs = context.selected_objects
    if context.object is not None:
        col.label(text=f'{context.object.name} {context.object.type}  {len(objs)} Selected')

        box = col.split().column()
        row = box.row(align=True)
        row.scale_y = 1.5
        row.scale_x = 1.5
        row.prop(context.object, "show_name", text="", icon='EVENT_N')
        row.prop(context.object, "show_axis", text="", icon='EVENT_X')
        row.prop(context.object, "show_wire", text="", icon='EVENT_W')
        row.prop(context.object, "show_in_front", text="", icon='EVENT_F')
        row.prop(context.object, "display_type", text='', expand=False,)

        col.separator()
        col = col.row(align=False)
        box = col.box()
        box = box.split().column()

        if context.object.type == 'MESH':
            draw_MESH(box,context)

        elif context.object.type == 'CAMERA':
            draw_CAMERA(box,context)

        elif context.object.type == 'LIGHT':
            draw_LIGHT(box,context)

        elif context.object.type == "EMPTY":
            draw_EMPTY(box,context)

        elif context.object.type == "CURVE":
            draw_CURVE(box,context)

# side menu or pie menu part

def UsingPie(self,pie):
    if pie == self.layout.menu_pie():
        return True


def Pie_SetCam(self, context, pie):
    col = pie.column()
    box = col.box()
    box = box.split().column()

    row = box.row(align=True)

    row.scale_y = 1.5
    row.operator("object.add_view_camera", icon='VIEW_CAMERA')
    row.scale_x = 1.25
    row.prop(context.space_data, "lock_camera", text="", icon="LOCKED"if context.space_data.lock_camera else "UNLOCKED")
    row.operator("view3d.focus_picker", text='', icon="EYEDROPPER")

    row = box.row(align=True)
    row.scale_y = 1.5
    row.scale_x = 1.5
    row.operator("view3d.view_selected", text="", icon='ZOOM_SELECTED')

    row.scale_x = 1
    row.operator("view.activecam", text="", icon='OUTLINER_DATA_CAMERA')
    row.scale_x = 1.25
    row.popover(panel="SSM_PT_camera_switcher_menu", text="Jump to",)
    row.operator("view3d.camera_to_view",icon='HIDE_OFF', text="")

    row = box.row(align=True)
    row.label(text="Modify Camera")

    row = box.row(align=True)
    row.scale_y = 1.5
    row.operator("object.set_cam_ev", text='EV', icon="LIGHT_SUN")
    row.operator("view.flipcam", icon="ARROW_LEFTRIGHT")

    row = box.row(align=True)
    row.operator("view.light_check", text="LightCheck", icon="IMAGE_ZDEPTH")
    row.operator("interface.simple_translater", icon='OUTLINER_OB_FONT', text='')
    row.operator("render.opengl", icon='RENDER_STILL', text='').animation = True
    row.operator("render.render", icon='SCENE', text='')


def Pie_Move(self, context, pie):
    col = pie.column()

    col.split().column()
    row = col.row(align=True)

    row.scale_y = 2
    row.scale_x = 1.05
    row.operator("object.look_at", icon="ORIENTATION_NORMAL")
    row.separator()


    row.operator("object.trans_psr", icon="CON_LOCLIKE")
    sub = row.split(align=True)
    sub.popover(panel="PANEL_PT_TransPanel", text='', icon='DOWNARROW_HLT')
    row.separator()

    row.operator("object.drop2floor", icon="SORT_ASC")
    sub = row.split(align=True)
    sub.popover(panel = "PANEL_PT_D2fPanel",text='', icon='DOWNARROW_HLT',)


def Side_SetCam(box,context):
    box = box.split().column()
    row = box.row(align=True)
    row.scale_y = 2
    row.operator("object.add_view_camera", icon='VIEW_CAMERA')
    row.scale_x = 1.25
    row.operator("view3d.focus_picker", text='', icon="EYEDROPPER")
    row.prop(context.space_data, "lock_camera", text="",
             icon="LOCKED" if context.space_data.lock_camera else "UNLOCKED")

    row = box.row(align=True)
    row.scale_y = 1.5
    row.scale_x = 1.5
    row.operator("view3d.view_selected", text="", icon='ZOOM_SELECTED')

    row.scale_x = 1.25
    row.operator("view.activecam", text="", icon='OUTLINER_DATA_CAMERA')
    row.scale_x = 1
    row.popover(panel="SSM_PT_camera_switcher_menu", text="Jump to", )
    row.operator("view3d.camera_to_view", icon='HIDE_OFF', text="")

    row = box.row(align=True)
    row.scale_y = 1.5
    # row.operator("screen.userpref_show",text = "",icon = 'PREFERENCES')
    row.operator("object.set_cam_ev", text='EV', icon="LIGHT_SUN")
    row.operator("view.flipcam", icon="ARROW_LEFTRIGHT")
    row = box.row(align=True)
    row.operator("view.light_check", text="LightCheck", icon="IMAGE_ZDEPTH")
    row.operator("interface.simple_translater", icon='OUTLINER_OB_FONT', text='')
    row.operator("render.opengl", icon='RENDER_STILL', text='').animation = True
    row.operator("render.render", icon='SCENE', text='')


def Side_Move(box,context):
    box = box.split().column()
    row = box.row(align=True)
    row.scale_y = 1.5
    row.operator("object.trans_psr", icon="CON_LOCLIKE")
    row.prop(context.preferences.addons[__package__].preferences, "Tp", icon="ORIENTATION_GLOBAL", text='')
    row.prop(context.preferences.addons[__package__].preferences, "Ts", icon="ORIENTATION_LOCAL", text='')
    row.prop(context.preferences.addons[__package__].preferences, "Tr", icon="ORIENTATION_GIMBAL", text='')

    row = box.row(align=True)
    row.scale_y = 1.5
    row.operator("object.look_at", icon="ORIENTATION_NORMAL")

    row.operator("object.drop2floor", icon="SORT_ASC")
    row.prop(context.preferences.addons[__package__].preferences, "OM", icon="MESH_DATA", text='')

    # if context.scene.camera:
    #     col.prop(context.scene.camera, "AF")


def Extra(self,context,pie):
    col = pie.column()
    row = col.row(align=True)
    row.scale_y = 1.5
    # row.operator("interface.simple_translater", icon='OUTLINER_OB_FONT')
    row.operator("object.export_obj", icon="FOLDER_REDIRECT")


def Image_Manager(layout,context):
    pref = context.preferences.addons[__package__].preferences
    index = context.scene.image_list_index
    image = bpy.data.images[index]
    sx = image.size[0]
    sy = image.size[1]

    layout.row()
    layout.template_list(
        "ssm.image_list", "The list",
        bpy.data, "images",
        context.scene, "image_list_index", )

    col = layout.column()

    sub = col.split(factor=0.75, align=True)
    sub.scale_y = 1.5


    showimage = sub.operator("interface.pop_image_editor", text=f"{image.name}", icon="TEXTURE")
    showimage.imagename = image.name
    showimage.sizex = sx
    showimage.sizey = sy

    sub.operator("ssm.pack", text="Unpack" if image.packed_file else "Pack",
                 icon='PACKAGE' if image.packed_file else 'UGLYPACKAGE').imagename = image.name

    row = col.row(align=True)
    row.label(text=f"Source: {image.source} Size: {sx}x{sy}·{image.depth}bits",)

    row = col.row(align=True)
    row.scale_y = 1.5

    if image.source in {'FILE',"SEQUENCE","MOVIE"} :
        row.prop(image, "filepath", text="")
        row.operator("image.reload", text="", icon='FILE_REFRESH')
        row.prop(image, "use_fake_user", text='')

        row.separator()
        row.operator("image.remove", text="", icon="PANEL_CLOSE")

    sub = col.split(factor = 0.2,align=True)
    sub.scale_y = 1.5
    # filter
    sub.prop(pref, 'filter_tpye', text="", icon="FILTER")
    sub.operator("ssm.removeunused",text = "Remove")


    # for image in bpy.data.images:
    #     if image.name != "Render Result":
    #         row = col.row(align =True)
    #         row.label(text=image.name,icon = 'FILE_IMAGE')
    #         row.separator()
    #
    #         full_path = bpy.path.abspath(image.filepath, library=image.library)
    #         normal_path = os.path.normpath(full_path)
    #         row.label(text=normal_path)
    #         row.separator()
    #
    #         row.label(text="Pack" if image.packed_file else "UnPack")
    #         row.separator()
    #
    #         row.prop(image,"use_fake_user",text ='')
    #         row.separator()
    #
    #         remove = row.operator("image.remove",text = '',icon ="PANEL_CLOSE")
    #         remove.imagename = image.name


def Mat_Manager(layout,context):
    pref = context.preferences.addons[__package__].preferences
    # List
    col = layout.column()
    col.prop(pref, "Picker_mode",icon="EYEDROPPER" if pref.Picker_mode else "MATERIAL_DATA")
    if not pref.Picker_mode:
        col = layout.column()
        row = col.row(align=True)
        row.template_list(
            "ssm.mat_list", "All Mat",
            bpy.data, "materials",
            context.scene, "mat_list_index", )

        col.operator("ssm.remove_single_mat", text="Remove Select", icon="PANEL_CLOSE")

        row = col.row(align=True)
        row.scale_y = 1.5
        sub = row.split(factor=0.2, align=True)
        sub.prop(pref, 'filter_tpye', text="", icon="FILTER")
        sub.operator("ssm.remove_by_filter", text="Remove by Filter")

        row = col.row(align=True)
        row.label(text='Active Material')
        row = col.row(align=True)
        row.template_ID_preview(
            context.object, "active_material",
            new="material.new",
            rows=4, cols=4
        )

    # Picker mode

    else:
        col = layout.column()
        row = col.row(align=True)

        row.template_list(
            "picker.mat_list", "Mat list",
            context.scene, "picker_list",
            context.scene, "picker_list_index", )

        subcol = row.column(align = True)
        subcol.operator("picker.addmat",text ="",icon = "ADD")
        subcol.operator("picker.removemat", text="", icon="REMOVE")
        subcol.operator("picker.clear_list",text ="",icon = "PANEL_CLOSE")

        # picker view
        if len(context.scene.picker_list)>0:
            col.template_ID_preview(
                context.scene.picker_list[context.scene.picker_list_index], "material",
                rows=3, cols=3
            )

    col = layout.column()
    col.scale_y =1.5
    col.operator('ssm.material_picker', text='>>Pick Material<<', icon="EYEDROPPER")


def Light_Group(layout,context):

    col = layout.column()
    light_list, light_group = getlight()

    row1 = col.row(align=True)
    row1.scale_y = 1.5
    row1.operator("ssm.creat_light_group", text="Creat")
    row1.operator("ssm.reset_group_solo", text="Reset Solo")

    for group in light_group:
        sub = col.split(factor=0.75)
        row = sub.row(align=True)

        sologroup = row.operator("ssm.solo_group", text=f"", icon="EVENT_S")
        renameop = row.operator("ssm.rename_light_group", text=f"{group}")
        remove = row.operator("view.remove_group", text="", icon="PANEL_CLOSE")
        remove.GroupName = group
        toggle = sub.operator("view.toggle_group", text="Toggle")

        box = col.box()
        for light in light_list:

            if light.ssm_light.Group == group:
                sologroup.LightName = light.name
                renameop.LightName = light.name

                toggle.LightName = light.name

                row = box.row(align=True)

                sololight = row.operator("ssm.solo_single", text=f"", icon="EVENT_S")
                sololight.LightName = light.name

                active = row.operator("view.active_light", text=light.name, icon="RESTRICT_SELECT_OFF")
                active.LightName = light.name
                row.separator()
                row.scale_x = 1.1
                row.prop(light, 'hide_viewport', icon='HIDE_OFF', text='')
                row.prop(light, 'hide_render', icon='RESTRICT_RENDER_OFF', text='')


class SSM_PT_SideObjInfo(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SSM'
    bl_label = 'Object Data'

    @classmethod
    def poll(cls, context):
        if context.preferences.addons[__package__].preferences.SIDE_MENU:
            return context.object is not None

    def draw(self, context):
        if context.preferences.addons[__package__].preferences.SM_sub:
            layout = self.layout
            pie = layout
            Obj_Info_UI(self,context,pie)


class SSM_PT_SideMenu(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SSM'
    bl_label = 'Smart Scene Manager'


    @classmethod
    def poll(cls, context):
        return context.preferences.addons[__package__].preferences.SIDE_MENU

    def draw(self,context):
        pref = context.preferences.addons[__package__].preferences
        layout = self.layout

        col = layout.column(align = False)
        col.scale_y=1.25
        col.scale_x = 1.25


        col.prop(pref,"openCam",text = "Set Camera",icon ="TRIA_DOWN"if pref.openCam else "TRIA_RIGHT" )
        if pref.openCam:
            box = col.box()
            Side_SetCam(box,context)
            col.separator()

        col.prop(pref, "openMove", text="Move Object", icon="TRIA_DOWN"if pref.openMove else "TRIA_RIGHT")
        if pref.openMove:
            box = col.box()
            Side_Move(box,context)
            col.separator()

        col.prop(pref,"LIST_MG",icon ="TRIA_DOWN"if pref.LIST_MG else "TRIA_RIGHT")
        if pref.LIST_MG:
            col = layout.column(align = False)
            row =col.row(align =True)
            row.prop(pref, "list_type",expand =True)
            box = col.box()

            if pref.list_type =="IMAGE":
                Image_Manager(box, context)
            else:
                Mat_Manager(box, context)
            col.separator()

        col.prop(pref, "LG", icon="TRIA_DOWN" if pref.LG else "TRIA_RIGHT")
        if pref.LG:
            col = layout.column(align=False)
            Light_Group(col,context)
            col.separator()

        col = layout.column()
        Extra(self, context, col)


class SSM_MT_PieMenu(Menu):
    bl_label = "Pie Menu"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH'} and context.preferences.addons[__package__].preferences.PIE_MENU

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        objs = context.selected_objects
        #LEFT
        pie.operator("object.export_obj", icon="FOLDER_REDIRECT")
        #Right
        Pie_SetCam(self, context, pie)
        # Bottom
        pie.popover(panel="SSM_PT_SideObjInfo", text="Object", icon='OBJECT_DATA')
        # top
        Pie_Move(self, context, pie)
        # top Left
        pie.separator()
        # top  Right
        pie.separator()
        # left bottom
        pie.operator('ssm.material_picker', icon='MATERIAL')
        # right bottom
        pie.separator()

# select menu

class SSM_MT_AlignMenu(Menu):
    bl_label = "Align View"

    def draw(self,context):
        layout = self.layout
        layout.operator('view3d.view_selected')
        layout.operator_enum("view3d.view_axis", "type").align_active = True
        # layout.menu("VIEW3D_MT_select_%s" % mode_string.lower())


class SSM_MT_Select(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("mesh.select_less", text="Select Less")
        # 6 - RIGHT
        pie.operator("mesh.select_more", text="Select More")
        # 2 - BOTTOM
        pie.menu("OBJECT_MT_selectloopselection", text="Select Loops")
        # 8 - TOP
        pie.operator("mesh.select_all", text="Select All").action = 'TOGGLE'
        # 7 - TOP - LEFT
        pie.operator("mesh.select_prev_item", text="Select Previous")
        # 9 - TOP - RIGHT
        pie.operator("mesh.select_next_item", text="Select Next")
        # 1 - BOTTOM - LEFT
        pie.operator("mesh.select_all", text="Invert Selection").action = 'INVERT'
        # 3 - BOTTOM - RIGHT
        pie.menu("SSM_MT_AlignMenu")




