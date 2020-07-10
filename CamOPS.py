#camera ops
import bpy
from bpy_extras import view3d_utils
from math import *

class SetCamA(bpy.types.Operator):
    """set cam passepartout between 0.5/1"""
    bl_idname = "view.setcama"
    bl_label = "Set Cam PP"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            obj = bpy.context.object
            if obj.type == "CAMERA":
                obj = bpy.context.object
                if obj.data.passepartout_alpha == 1:
                    obj.data.passepartout_alpha = 0.5
                else:
                    obj.data.passepartout_alpha = 1
            else:
                self.report({'ERROR'}, 'select camera only.')
        except Exception as e:
            pass

        return {'FINISHED'}


class ActiveCam(bpy.types.Operator):
    """enter select cam"""
    bl_idname = "view.activecam"
    bl_label = "enter select cam"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        objs = bpy.context.selected_objects
        for obj in objs:
            if obj.type == "CAMERA":
                bpy.context.scene.camera = obj
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.spaces[0].region_3d.view_perspective = 'CAMERA'
                        self.report({'INFO'}, 'Active Cam Done.')
                        break
                break
        return {'FINISHED'}


class AddViewCam(bpy.types.Operator):
    """add view cam
ctrl: add ortho cam
shift: add view cam constraint to select obj"""
    bl_idname = "object.add_view_camera"
    bl_label = "AddCam"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # shift event
        if event.shift:
            if len(bpy.context.selected_objects) == 1:
                selectingobj = bpy.context.object
            else :
                self.report({'ERROR'}, 'select one object to look at.')
        # new camera
        bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))

        #set new cam to active
        cam = bpy.context.object

        '''ctrl: ortho cam event'''
        if event.ctrl:
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = 10

        bpy.context.scene.camera = cam
        # add constraint cam
        if event.shift:
            try:
                con = cam.constraints.new(type='DAMPED_TRACK')
                if selectingobj != cam:
                    con.target = selectingobj
                    con.track_axis = 'TRACK_NEGATIVE_Z'
            except Exception as e:
                pass

        '''当前视图复位'''
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region}
                        bpy.ops.view3d.camera_to_view(override)

        return {'FINISHED'}


class FilpCam(bpy.types.Operator):
    """Filp x (SceneCam)
Ctrl : Filp Z
Shift: Filp Y
UNDO : ctrl z """
    bl_idname = "view.filpcam"
    bl_label = "export_obj"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        try:
            cam = bpy.context.scene.camera
            cam.select_set(True)
            if event.ctrl:
                bpy.ops.transform.resize(value=(-1, 1, -1), orient_type='GLOBAL',
                                         orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                         constraint_axis=(True, False, False))
            if event.shift:
                bpy.ops.transform.resize(value=(-1, -1, 1), orient_type='GLOBAL',
                                         orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                         constraint_axis=(True, False, False))

            bpy.ops.transform.resize(value=(-1, 1, 1), orient_type='GLOBAL',
                                     orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                     constraint_axis=(True, False, False))
        except AttributeError as e:
            self.report({'ERROR'}, 'No scene camera.')
            # self.report({'INFO'}, 'No scene camera.')

        return {'FINISHED'}



def raycast(context, event):
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    viewlayer = context.view_layer

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    result, location, normal, index, object, matrix = scene.ray_cast(viewlayer, ray_origin, view_vector)


    print(location)

    return location

def measure(first, second):
    locx = second[0] - first[0]
    locy = second[1] - first[1]
    locz = second[2] - first[2]
    distance = sqrt((locx)**2 + (locy)**2 + (locz)**2)
    return distance


class focusPicker(bpy.types.Operator):
    ''' pick focus
shift: generate empty target(WIP)'''
    bl_idname = "view3d.focus_picker"
    bl_label = "Pick Focus "
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE',
                          'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            #get mouse point location
            Location = raycast(context, event)
            self.report({'INFO'}, 'Focus point: %s.'%(Location))
            try:
                #get cam location
                cam = bpy.context.scene.camera
                focusDis = measure(Location,cam.location)
                print(focusDis)
                cam.data.dof.use_dof = True
                #add target
                if event.shift:
                    target = bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
                    target.location = Location
                    cam.data.dof.focus_object = target
                    focusDis = 0


                cam.data.dof.focus_distance = focusDis
            except Exception as e:
                self.report({'ERROR'}, 'No scene camera !%s'%(e) )

            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}