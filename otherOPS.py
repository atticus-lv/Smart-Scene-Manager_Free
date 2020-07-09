import bpy
import os


class TransPSR(bpy.types.Operator):
    """Transform selected object(s) to active """
    bl_idname = "object.trans_psr"
    bl_label = "TransPSR"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

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

        if len(objs) == 1:
            self.report({'ERROR'}, ' select 2 more object .')
        else:
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
    """export select obj to blend file dir
ctrl: export as fbx"""
    bl_idname = "object.export_obj"
    bl_label = "export_obj"

    def invoke(self, context,event):
        # 导出所选obj
        try:
            selection = bpy.context.selected_editable_objects
            blend_file_path = bpy.data.filepath
            directory_path = os.path.dirname(blend_file_path) + "\\" + "export_files"
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            form = '.obj'; f = 0
            if event.ctrl:
                form = '.fbx'; f = 1
            directory = directory_path + "\\" + selection[0].name + form
            # print(directory)
            if f == 0:
                bpy.ops.export_scene.obj(filepath=directory, axis_up='Y', axis_forward='-Z',
                                     use_selection=True, use_materials=True, use_uvs=True, use_normals=True)
                self.report({'INFO'}, 'finish! export obj to %s.' % (directory))
            elif f == 1:
                bpy.ops.export_scene.fbx(filepath=directory, object_types = {'ARMATURE','CAMERA','EMPTY','LIGHT','MESH','OTHER'},
                                         use_mesh_modifiers = True,use_mesh_modifiers_render = True,use_subsurf =True,
                                         use_selection=True)
                self.report({'INFO'}, 'finish! export fbx to %s.'% (directory))

        except IndexError as I:
            self.report({'ERROR'}, 'no select object .')
        return {'FINISHED'}


class LightCheck(bpy.types.Operator):
    """change to false color"""
    bl_idname = "view.light_check"
    bl_label = "LightCheck"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.scene.view_settings.view_transform != 'False Color':
            bpy.context.scene.view_settings.view_transform = 'False Color'
        else:
            bpy.context.scene.view_settings.view_transform = 'Filmic'
        return {'FINISHED'}
