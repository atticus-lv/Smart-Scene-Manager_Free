#camera ops

import bpy







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
                        break
                break
        return {'FINISHED'}

class AddViewCam(bpy.types.Operator):
    """为当前视角添加摄像机
ctrl点击添加正交摄像机"""
    bl_idname = "object.add_view_camera"
    bl_label = "AddCam"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):

        bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
        cam = bpy.context.object

        '''正交摄像机事件'''
        if event.ctrl:
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = 10

        bpy.context.scene.camera = cam
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
            self.report({'INFO'}, 'No scene camera.')

        return {'FINISHED'}
