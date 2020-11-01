#-*- coding =utf-8 -*-
import bpy
import blf
import bgl
from bpy_extras import view3d_utils
from bpy.types import Menu,Panel,Operator,UIList
from bpy.props import *

from .Ops_Extra import viewlayer_fix_291,CN_ON,get_region_size


class PopShaderEditor(Operator):
    """If not English,translate interface between English and your language"""
    bl_idname = "interface.pop_shadereditor"
    bl_label = "Shader Editor"

    def execute(self, context):
        # Modify scene settings
        window = context.scene.render

        ORx = window.resolution_x
        ORy = window.resolution_y

        RX = context.preferences.addons[__package__].preferences.RX
        RY = context.preferences.addons[__package__].preferences.RY

        window.resolution_x = RX
        window.resolution_y = RY
        # window.resolution_percentage = 100

        # Call image editor window
        bpy.ops.render.view_show("INVOKE_DEFAULT")

        # Change area type
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        area.type = "NODE_EDITOR"
        area.ui_type = 'ShaderNodeTree'
        bpy.context.space_data.show_region_ui = False
        # bpy.ops.node.view_all()

        # restore
        window.resolution_x = ORx
        window.resolution_y = ORy

        return {'FINISHED'}


def draw_material_callback_px(self, context):
    font_id = 0

    text = [
        ['Left click to pick material / A to apply current slot material/X to clear Mat','左键拾取材质 / A应用当前槽位材质 / X清除当前区域材质'],
        ['Q and E switch up and down material slot / D to remove current slot / C to clear all slot',"Q,E 上下切换槽位材质 / D 移除当前槽位 / C 清除所有槽位"],
        ["Right click to exit picker mode", "右键完成或者取消"],
        ["Mat","材质"],
        ["Current Mat","当前材质"],
        ["", ""],
    ]

    i = 1 if CN_ON(context) else 0

    # tips
    x, y = get_region_size(context)
    top = 0.85 * y
    bottom = 0.15 * y
    left = 0.015 * x

    blf.size(font_id, 12, 100)
    blf.position(font_id, left, top, 0)
    blf.draw(font_id, text[0][i])
    blf.position(font_id, left, top-20, 0)
    blf.draw(font_id, text[1][i])
    blf.position(font_id, left, top-40, 0)
    blf.draw(font_id, text[2][i])
    # blf.position(font_id, left, top - 60, 0)
    # blf.draw(font_id, text[3][i])
    # blf.position(font_id, left, top - 80, 0)
    # blf.draw(font_id, text[4][i])


class SSM_OT_Material_Picker(Operator):
    '''Check the tooltips that show on the left'''
    bl_idname = "ssm.material_picker"
    bl_label = 'Pick Mat'
    bl_options = {'REGISTER', 'GRAB_CURSOR', 'BLOCKING', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object

    def raycast(self, context, event):
        # Get the mouse position thanks to the event
        self.mouse_pos = event.mouse_region_x, event.mouse_region_y
        # Contextual active object, 2D and 3D regions
        scene = context.scene
        region = context.region
        region3D = context.space_data.region_3d

        viewlayer = viewlayer_fix_291(self,context)

        # The direction indicated by the mouse position from the current view
        self.view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)
        # The view point of the user
        self.view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, self.mouse_pos)
        # The 3D location in this direction
        self.world_loc = view3d_utils.region_2d_to_location_3d(region, region3D, self.mouse_pos, self.view_vector)

        result, self.loc, normal, index, object, matrix = scene.ray_cast(viewlayer, self.view_point, self.view_vector)


        if result:
            for obj in context.selected_objects:
                obj.select_set(False)
            dg = context.evaluated_depsgraph_get()

            eval_obj = dg.id_eval_get(object)
            context.view_layer.objects.active = object.original

            self.Mat_index = eval_obj.data.polygons[index].material_index
            object.original.active_material_index = self.Mat_index
            self.Mat = object.original.active_material


    def modal(self, context, event):
        context.area.tag_redraw()

        # ray cast

        if event.type in { 'WHEELUPMOUSE',
                          'WHEELDOWNMOUSE'}:

            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            self.raycast(context,event)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if self.cursor_set:
                context.window.cursor_modal_restore()
            # restore
            if context.preferences.addons[__package__].preferences.usePop == True:
                # pop up windows
                bpy.ops.interface.pop_shadereditor()

            context.preferences.addons[__package__].preferences.Picker_mode = self.mode
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            return {'CANCELLED'}


        # slot operator

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            bpy.ops.picker.addmat()


        elif event.type == 'Q' and event.value == 'PRESS':
            scn = context.scene

            if scn.picker_list_index == 0:
                scn.picker_list_index = 0
            else:
                scn.picker_list_index -= 1

            return {'RUNNING_MODAL'}

        elif event.type == 'E' and event.value == 'PRESS':
            scn = context.scene
            length = len(scn.picker_list)
            if scn.picker_list_index == length - 1:
                scn.picker_list_index = length - 1
            else:
                scn.picker_list_index += 1

            return {'RUNNING_MODAL'}

        elif event.type == 'D' and event.value == 'PRESS':
            bpy.ops.picker.removemat()
            return {'RUNNING_MODAL'}

        elif event.type in {'C', }:
            bpy.ops.picker.clear_list()
            return {'RUNNING_MODAL'}

        # apply and delete

        elif event.type == 'A' and event.value == 'PRESS':

            scn = context.scene
            item = scn.picker_list[scn.picker_list_index]
            mat = item.material
            mat_obj = bpy.data.materials.get(mat.name, None)

            if mat_obj:
                context.object.active_material = mat_obj

            return {'RUNNING_MODAL'}

        elif event.type in {'X', }:
            context.object.active_material = None
            return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            #use cursor
            self.cursor_set = True
            context.window.cursor_modal_set('EYEDROPPER')
            # add tips
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_material_callback_px, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)

            self.mouse_pos = [0, 0]
            self.dis = 10
            self.loc = [0, 0, 0]

            self.view_point = None
            self.view_vector = None

            self.mode =context.preferences.addons[__package__].preferences.Picker_mode
            context.preferences.addons[__package__].preferences.Picker_mode = True


            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


class SSM_OT_Remove_By_Filter(Operator):
    bl_idname = "ssm.remove_by_filter"
    bl_label = 'Remove By Filter'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pref = context.preferences.addons[__package__].preferences
        for mat in bpy.data.materials:
            if pref.filter_tpye == "None":
                self.report({'INFO'}, "Nothing to remove")
                pass
            elif pref.filter_tpye == "FAKE":
                if mat.use_fake_user == True:
                    bpy.data.materials.remove(mat)
                    self.report({'INFO'}, f'Remove fake user materials')
            elif pref.filter_tpye == "NOUSER":
                if mat.users == 0 and mat.use_fake_user == False:
                    bpy.data.materials.remove(mat)
                    self.report({'INFO'}, f'Remove no user materials')

        return {'FINISHED'}


class SSM_OT_Remove_Single_Mat(Operator):
    bl_idname = "ssm.remove_single_mat"
    bl_label = 'Remove Material'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mat = bpy.data.materials[context.scene.mat_list_index]

        if mat:
            self.report({'INFO'}, f'Delete {mat.name} Done  ')
            bpy.data.materials.remove(mat, do_unlink=True)

        return {'FINISHED'}


class SSM_UL_MatList(UIList):
    bl_idname = "ssm.mat_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon_value=icon)

            row = row.row(align=True)
            row.alignment = 'RIGHT'

            if item.use_fake_user:
                row.label(text="F")
            else:
                row.label(text=str(item.users))

            # row.operator(bpy.data.materials.remove)

        elif self.layout_type in {'GRID'}:
            row = layout.row(align=True)
            row.alignment = 'CENTER'
            row.label(text="", icon_value=layout.icon(mat))


class PICKER_UL_MatList(UIList):
    bl_idname = "picker.mat_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        mat = item.material
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            if mat:
                row.prop(mat, "name", text="", emboss=False, icon_value=layout.icon(mat))

        elif self.layout_type in {'GRID'}:
            row = layout.row()
            if mat:
                row.alignment = 'CENTER'
                row.label(text="", icon_value=layout.icon(mat))


class PICKER_OT_AddMat(Operator):
    bl_idname = "picker.addmat"
    bl_label = 'Add'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scn = context.scene

        item = scn.picker_list.add()

        item.id = len(scn.picker_list)
        item.material = context.object.active_material

        if item.material != None:
            item.name = item.material.name
            self.report({'INFO'}, f'{item.name} add to list')
            scn.picker_list_index = (len(scn.picker_list)-1)
        else:
            scn.picker_list.remove(scn.picker_list_index+1)


        return {'FINISHED'}


class PICKER_OT_RemoveMat(Operator):
    bl_idname = "picker.removemat"
    bl_label = 'Remove'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene

        item = scn.picker_list[scn.picker_list_index]
        if item != None:
            item_name = item.material.name

            self.report({'INFO'}, f'{item_name} removed from list')

        scn.picker_list.remove(scn.picker_list_index)

        if scn.picker_list_index == 0:
            scn.picker_list_index = 0
        else:
            scn.picker_list_index -= 1



        return {'FINISHED'}


class PICKER_OT_clearList(Operator):
    """Clear all items of the list and remove from scene"""
    bl_idname = "picker.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items of the list"
    bl_options = {'INTERNAL'}


    def execute(self, context):

        if bool(context.scene.picker_list):

            context.scene.picker_list.clear()
            self.report({'INFO'}, "All materials removed from list")
        else:
            self.report({'INFO'}, "Nothing to remove")

        return{'FINISHED'}
