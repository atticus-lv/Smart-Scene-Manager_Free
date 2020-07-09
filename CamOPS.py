#camera ops
import bpy


class SetCamA(bpy.types.Operator):
    """set cam passepartout between 0.5/1"""
    bl_idname = "view.setcama"
    bl_label = "Set Cam PP"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.object
        if obj.type == "CAMERA":
            obj = bpy.context.object
            if obj.data.passepartout_alpha == 1:
                obj.data.passepartout_alpha = 0.5
            else:
                obj.data.passepartout_alpha = 1
        else:
            self.report({'ERROR'}, 'select camera only.')
            
        return {'FINISHED'}


class ActiveCam(bpy.types.Operator):
    bl_idname = "view.activecam"
    bl_label = "进入所选摄像机"
    bl_options = {'REGISTER', 'UNDO'}

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
