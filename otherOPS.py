import bpy
import os


class PSRreset(bpy.types.Operator):
    """点一下就可以翻译了"""
    bl_idname = "object.PSRreset"
    bl_label = "transfrom PSR to select"

    def execute(self, context):
        active = bpy.context.active_object
        objs = bpy.context.selected_objects

        def get_TL():
            for obj in objs:
                if obj == active:
                    TL = obj.location
                    break
            return TL

        def apply_TL(TL):
            for obj in objs:
                if obj != active:
                    obj.location = TL

        TL = get_TL()
        apply_TL(TL)

        return {'FINISHED'}


class Translater(bpy.types.Operator):
    """点一下就可以翻译了"""
    bl_idname = "interface.simple_translater"
    bl_label = "点击翻译"

    def execute(self, context):
        if bpy.context.preferences.view.use_translate_interface == 0:
            bpy.context.preferences.view.use_translate_interface = 1
        else:
            bpy.context.preferences.view.use_translate_interface = 0
        return {'FINISHED'}


class ExportObj(bpy.types.Operator):
    """将导出所选物体到blend文件目录下（需保存）"""
    bl_idname = "object.export_obj"
    bl_label = "export_obj"

    def execute(self, context):
        # 导出所选obj
        try:
            selection = bpy.context.selected_editable_objects
            blend_file_path = bpy.data.filepath
            directory_path = os.path.dirname(blend_file_path) + "\\" + "export_files"
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            directory = directory_path + "\\" + selection[0].name + ".obj"
            # print(directory)
            bpy.ops.export_scene.obj(filepath=directory, axis_up='Y', axis_forward='-Z',
                                     use_selection=True, use_materials=True, use_uvs=True, use_normals=True)
        except IndexError as I:
            self.report({'INFO'}, 'no select object .')
        return {'FINISHED'}


# class LightCheck(bpy.types.Operator):
#     """Tooltip"""
#     bl_idname = "object.lightcheck"
#     bl_label = "Simple Object Operator"
#
#     def execute(self, context):
#         if bpy.context.scene.view_settings.view_transform != 'False Color':
#             bpy.context.scene.view_settings.view_transform = 'False Color'
#         else:
#              bpy.context.scene.view_settings.view_transform = 'Filmic'
#
#         return {'FINISHED'}