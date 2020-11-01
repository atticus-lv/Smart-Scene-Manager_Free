#-*- coding =utf-8 -*-
import bpy
import bgl
import blf

from bpy.types import Object, Scene, Panel, Operator,Menu
from bpy.props import *

from .Ops_Extra import get_region_size,CN_ON


def set_store_ev(context):
    cam = context.scene.camera.ssm_cam
    cam.StoreEV = True


def set_cam_ev(context):
    cam = context.scene.camera.ssm_cam
    if cam.StoreEV:
        context.scene.render.resolution_x = cam.Rx
        context.scene.render.resolution_y = cam.Ry
        context.scene.view_settings.exposure = cam.EV


def store_scene_ev(context):
    Scene = context.scene
    Scene.EV = context.scene.view_settings.exposure


def get_view(scene):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    if area.spaces[0].region_3d.view_perspective == 'CAMERA':
                        if scene.camera.ssm_cam.StoreEV:
                            bpy.context.scene.view_settings.exposure = scene.camera.ssm_cam.EV
                            break
                    else:
                        # print('scene_ev_set_0')
                        bpy.context.scene.view_settings.exposure = scene.EV
                        break
            break


class SceneSetEV(Operator):
    bl_idname = "object.reset_scene_ev"
    bl_label = "Auto Scene Exposure"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        get_view(context.scene)
        # bpy.app.handlers.depsgraph_update_post.append(get_view)

        return {'FINISHED'}

#reference from Gaffer
def visibleCollections():
    def check_child(c, vis_cols):
        if c.is_visible:
            vis_cols.append(c.collection)
            for sc in c.children:
                vis_cols = check_child(sc, vis_cols)
        return vis_cols

    vis_cols = [bpy.context.scene.collection]

    for c in bpy.context.window.view_layer.layer_collection.children:
        check_child(c, vis_cols)

    return vis_cols


def draw_ev_callback_px(self, context):
    font_id = 0

    text = [
        ['Move mouse to right to increase camera Exposure Value', '向右滑动鼠标提高当前相机曝光值'],
        ["left click: confirm", "左键完成确认"],
        ['EV: ', "曝光强度："],
    ]

    i = 1 if CN_ON(context) else 0

    x,y = get_region_size(context)
    top = 0.85*y
    bottom = 0.15*y
    left = 0.02*x
    # tips
    blf.size(font_id, 12, 100)
    blf.position(font_id, left, top , 0)
    blf.draw(font_id, text[0][i])
    blf.position(font_id, left, top-30, 0)
    blf.draw(font_id, text[1][i])

    blf.size(font_id, 12, 175)
    blf.position(font_id, left+10, bottom +100, 0)
    blf.draw(font_id, text[2][i])
    # parameter
    blf.size(font_id, 12, 150)
    blf.position(font_id, left+10,bottom+60, 0)
    blf.draw(font_id, str(round(context.scene.camera.ssm_cam.EV,3)))


def draw_looks_callback_px(self, context):
    font_id = 0
    # tips
    text = [
        ['Wheel up and down to change contrast looks', '使用滚轮上下滚动切换对比度'],
        [' F: change to false color', ' F：切换到热度图（曝光）'],
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
    blf.position(font_id, left, top - 20, 0)
    blf.draw(font_id, text[1][i])

    # parameter
    blf.size(font_id, 12, 150)
    blf.position(font_id, left + 10, bottom + 100, 0)
    blf.draw(font_id, 'Current Looks: ')
    blf.size(font_id, 12, 150)
    blf.position(font_id, left + 10, bottom + 70, 0)
    blf.draw(font_id, (context.scene.view_settings.look))


Looks = ['Very Low Contrast', 'Low Contrast', 'Medium Contrast',
         'Medium High Contrast', 'High Contrast', 'Very High Contrast', 'None']


class LightCheck(bpy.types.Operator):
    """Check the tooltips that show on the left"""
    bl_idname = "view.light_check"
    bl_label = "LightCheck"
    bl_options = {'REGISTER', 'UNDO'}
    #Import Property
    mode: bpy.props.IntProperty()
    originLook: bpy.props.StringProperty()


    def modal(self, context, event):
        if event.type == "WHEELUPMOUSE":
            self.mode -= 1
            if self.mode < 0:
                self.mode = 6
            context.scene.view_settings.look = Looks[self.mode]

        elif event.type == "WHEELDOWNMOUSE":
            self.mode += 1
            if self.mode > 6 :
                self.mode = 0
            context.scene.view_settings.look = Looks[self.mode]

        elif event.type == 'F' and event.value == 'PRESS' :
            if context.scene.view_settings.view_transform != 'False Color':
                context.scene.view_settings.view_transform = 'False Color'
            else:
                context.scene.view_settings.view_transform = 'Filmic'
            return {'RUNNING_MODAL'}

        elif event.type == 'LEFTMOUSE':
            self.report({'INFO'}, f'Contrast Looks Confirm as: " {context.scene.view_settings.look} "')
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.scene.view_settings.view_transform = self.viewtrans
            context.scene.view_settings.look = self.originLook
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # false color
        # set
        self.mode = Looks.index(context.scene.view_settings.look)
        self.originLook = context.scene.view_settings.look
        self.viewtrans = context.scene.view_settings.view_transform
        # modal / draw
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_looks_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


class CamSetEV(Operator):
    '''Ctrl: reset scene EV while not in camera view'''
    bl_idname = "object.set_cam_ev"
    bl_label = "Set Camera Exposure"
    bl_options = {'REGISTER', 'GRAB_CURSOR', 'BLOCKING', 'UNDO'}

    def update(self,context):
        pass

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None
    # allow navigation
    def modal(self, context, event):
        cam = context.scene.camera
        # radius
        if event.type == 'MOUSEMOVE':
            self.mouseDX = self.mouseDX - event.mouse_x
            self.mouseDY = self.mouseDY - event.mouse_y
            multiplier = 0.001 if event.shift else 0.005
            # multi offset
            offset = self.mouseDX
            cam.ssm_cam.EV -= offset * multiplier

            set_cam_ev(context)

            # reset
            self.mouseDX = event.mouse_x
            self.mouseDY = event.mouse_y

        elif event.type == 'LEFTMOUSE':
            context.window.cursor_modal_restore()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            cam.ssm_cam.EV = self.ev
            set_cam_ev(context)
            context.window.cursor_modal_restore()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if not event.ctrl:
            cam = context.scene.camera
            set_store_ev(context)
            self.ev = cam.ssm_cam.EV
            self.mouseDX = event.mouse_x
            self.mouseDY = event.mouse_y
            self.sceneEV = context.scene.EV

            # icon
            self.cursor_set = True
            context.window.cursor_modal_set('MOVE_X')
            # draw
            if context.area.type == 'VIEW_3D':
                args = (self, context)
                self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_ev_callback_px, args, 'WINDOW','POST_PIXEL')
                context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}

        else:
            bpy.ops.object.reset_scene_ev()

            return {'CANCELLED'}


class ActiveCam(Operator):
    """enter select cam"""
    bl_idname = "view.activecam"
    bl_label = "Switch"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None

    def invoke(self, context, event):
        objs = context.selected_objects
        if len(objs) != 0:
            for obj in objs:
                if obj.type == "CAMERA":
                    bpy.context.scene.camera = obj
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.spaces[0].region_3d.view_perspective = 'CAMERA'
                            set_cam_ev(context)
                            get_view(context.scene)
                            self.report({'INFO'}, 'Active Cam Done.')

                            break
                    break
            # bpy.ops.wm.call_menu(name=CameraSwitcherMenu.bl_idname)
        return {'FINISHED'}


class CamList(Operator):
    """Switch Scene Camera"""
    bl_idname = "view.switch_camera"
    bl_label = "Switch 2 "
    # bl_options = {'INTERNAL'}

    CamName: bpy.props.StringProperty(name="Camera")

    def execute(self, context):
        try:
            # if select cam is scene cam
            context.scene.camera = bpy.data.objects[self.CamName]
        except :
            pass
        context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
        #set ev
        set_cam_ev(context)
        get_view(context.scene)
        return {'FINISHED'}


class SSM_PT_CameraSwitcher(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_category = ''
    bl_label = "Select a camera to enter"
    bl_idname = "SSM_PT_camera_switcher_menu"
    # bl_ui_units_x = 7.5

    @classmethod
    def poll(cls, context):
        for collection in bpy.data.collections:
            for obj in collection.all_objects:
                if obj.type == "CAMERA":
                    return True

    def draw(self, context):
        layout = self.layout
        coll_list = visibleCollections()
        # coll_list.pop(0)
        cam_list = []

        for coll in coll_list:
            for obj in coll.all_objects:
                if obj.type == "CAMERA":
                    cam_list.append(obj)

        cam_list = list(set(cam_list))

        for coll in coll_list:
            col = layout.column()
            row = col.row(align=True)

            num_list = []
            for obj in cam_list:
                if obj.users_collection[0].name == coll.name:
                    num_list.append('c')
                    if obj == context.scene.camera:
                        col.operator("view.switch_camera", icon="VIEW_CAMERA", text=obj.name)
                    else:
                        switch = col.operator("view.switch_camera", icon="OUTLINER_DATA_CAMERA", text=obj.name)
                        switch.CamName = obj.name
            if len(num_list) > 0:
                row.label(text=f"{coll.name}", icon='GROUP')






