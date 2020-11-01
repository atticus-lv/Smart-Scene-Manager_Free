#-*- coding =utf-8 -*-
import bpy
import bgl
import blf

from bpy_extras import view3d_utils
from math import *
from bpy.types import Object, Scene, Panel, Operator,Menu
from bpy.props import *

from .Ops_Extra import get_region_size,CN_ON,viewlayer_fix_291


def init_cam(cam):
    cam.ssm_cam.StoreEV = True
    cam.ssm_cam.Rx = 1920
    cam.ssm_cam.Ry = 1080
    cam.ssm_cam.LockXY = True


def measure(first, second):
    locx = second[0] - first[0]
    locy = second[1] - first[1]
    locz = second[2] - first[2]
    distance = sqrt((locx)**2 + (locy)**2 + (locz)**2)
    return distance


def draw_filp_callback_px(self, context):
    font_id = 0

    text = [
        ['Press x,y,z or 1,2,3 to flip', '按 x、y、z 或者 1、2、3 来翻转相机'],
        ["left click: confirm", "左键完成确认"],
        ['Filp Status:', "翻转状态"],
        ["Flip", "翻转"],
        ["Origin", "不变"]
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
    if context.object.scale[0] < 0:
        blf.draw(font_id, text[3][i]+' X')
    else:
        blf.draw(font_id, text[4][i]+' X')

    blf.position(font_id, left+10, bottom+30, 0)
    if context.object.scale[1] < 0:
        blf.draw(font_id, text[3][i]+' Y')
    else:
        blf.draw(font_id, text[4][i]+' Y')

    blf.position(font_id, left+10,bottom, 0)
    if context.object.scale[2] < 0:
        blf.draw(font_id, text[3][i]+' Z')
    else:
        blf.draw(font_id, text[4][i]+' Z')


def draw_distance_callback_px(self, context):
    font_id = 0
    x,y = self.mouse_pos

    blf.size(font_id, 12, 120)
    blf.position(font_id, x + 30, y, 0)
    blf.draw(font_id,str(round(self.dis,2))+' m')


class AddViewCam(Operator):
    """add view cam
ctrl: add ortho cam
shift: inherit the last camera's setting"""
    bl_idname = "object.add_view_camera"
    bl_label = "Add View Cam"
    bl_options = {'REGISTER', 'UNDO'}

    length: bpy.props.IntProperty(name='Length(mm)',description="Camera length",
        default=50,min=1, soft_max=250,)

    Sname: bpy.props.BoolProperty(name="Enable Cam Name",description="A bool property",
        default=False)

    Ortho: bpy.props.BoolProperty(name="Ortho camera",description="A bool property",
        default=False)

    Oscale: bpy.props.FloatProperty(name='Ortho_scale',description="Camera length",
        default=5,min=0, soft_max=15,)


    def execute(self, context):
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        #Add cam
        bpy.ops.object.camera_add()
        camName = context.object.name;cam = bpy.data.objects[camName]
        bpy.context.scene.camera = cam

        cam.data.lens = self.length
        cam.show_name = self.Sname
        cam.data.show_name = True

        init_cam(cam)

        if self.Ortho:
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = self.Oscale
        else:
            cam.data.type = 'PERSP'

        #Reset camera view # 感谢小凡哥的帮助
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        area.spaces[0].region_3d.view_perspective = 'PERSP'
                        override = {'area': area, 'region': region}
                        bpy.ops.view3d.camera_to_view(override)
                break

        return {'FINISHED'}

    def invoke(self, context, event):



        lens = context.preferences.addons[__package__].preferences.camlens
        Uname = context.preferences.addons[__package__].preferences.useCamName
        #inherit the last camera
        if not event.shift:
            self.length = lens
            self.Sname = Uname
            self.Ortho = False
            self.Oscale = 5
        # ortho camera
        if event.ctrl:
            self.length = lens
            self.Sname = Uname
            self.Oscale = 5
            self.Ortho = True

        return self.execute(context)


class FlipCam(Operator):
    """Flip SceneCam
Press x,y,z or 1,2,3 to flip camera
left click: confirm"""
    bl_idname = "view.flipcam"
    bl_label = "Flip"
    bl_options = {'REGISTER', 'UNDO'}

    oscale:bpy.props.FloatVectorProperty()

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None

    def modal(self, context, event):

        PRESS =(event.value == 'PRESS')

        if (event.type == 'X'and PRESS) or (event.type == 'ONE' and PRESS):
            context.object.scale[0] *= -1

        elif (event.type == 'Y'and PRESS) or (event.type == 'TWO' and PRESS):
            context.object.scale[1] *= -1

        elif (event.type == 'Z'and PRESS) or (event.type == 'THREE' and PRESS):
            context.object.scale[2] *= -1

        elif event.type == 'LEFTMOUSE':
            self.report({'INFO'}, 'Confirm Flip.')
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.object.scale = self.oscale
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.oscale = context.object.scale
        cam = context.scene.camera
        # cam.select_set(True)
        context.view_layer.objects.active = cam
        #set modal
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_filp_callback_px, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class focusPicker(Operator):
    '''pick focus, left click to confirm
confirm with shift: generate empty target'''
    bl_idname = "view3d.focus_picker"
    bl_label = "Pick Focus "
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None

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

        self.camera.data.dof.use_dof = True
        if result:
            self.dis = measure(self.camera.location, self.loc)
            self.camera.data.dof.focus_distance = self.dis


    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in { 'WHEELUPMOUSE',
                          'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            self.raycast(context,event)

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.raycast(context,event)
            if event.shift:

                bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
                target = bpy.context.object
                target.name = "FocusTG" + " 4 " + self.camera.name

                target.location = self.loc
                self.camera.data.dof.focus_object = target

            context.window.cursor_modal_restore()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if self.cursor_set:
                context.window.cursor_modal_restore()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            self.cursor_set = True
            context.window.cursor_modal_set('EYEDROPPER')

            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_distance_callback_px, args, 'WINDOW', 'POST_PIXEL')

            self.mouse_pos = [0, 0]
            self.dis = 10
            self.loc = [0, 0, 0]
            self.camera = context.scene.camera
            self.view_point = None
            self.view_vector = None

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


