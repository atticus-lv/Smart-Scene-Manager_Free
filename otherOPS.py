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

    def invoke(self, context,event):
        active = bpy.context.active_object
        objs = bpy.context.selected_objects
        #GET
        def get_TL():
            for obj in objs:
                if obj == active:
                    TL = obj.location
                    break
            return TL

        def get_TR():
            for obj in objs:
                if obj == active:
                    TR = obj.rotation_euler
                    break
            return TR

        def get_TS():
            for obj in objs:
                if obj == active:
                    TR = obj.scale
                    break
            return TR
        #APPLY
        def apply_TL(TL):
            for obj in objs:
                if obj != active:
                    obj.location = TL

        def apply_TR(TR):
            for obj in objs:
                if obj != active:
                    obj.rotation_euler = TR

        def apply_TS(TS):
            for obj in objs:
                if obj != active:
                    obj.scale = TS


        if len(objs) == 1:
            self.report({'ERROR'}, ' select 2 more object .')
        else:
            TL = get_TL()
            apply_TL(TL)

            if event.ctrl:
                TR = get_TR()
                apply_TR(TR)
            elif event.shift:
                TS =get_TS()
                apply_TS(TS)
            elif event.ctrl and event.shift:
                TR = get_TR()
                apply_TR(TR)
                TS = get_TS()
                apply_TS(TS)

        return {'FINISHED'}


class Translater(bpy.types.Operator):
    """点一下就可以翻译了"""
    bl_idname = "interface.simple_translater"
    bl_label = "点击翻译"
    T = bpy.context.preferences.view.use_translate_interface
    def execute(self, context):
        if T == 0:
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
    """change looks
ctrl: change to false color"""
    bl_idname = "view.light_check"
    bl_label = "LightCheck"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context,event):
        Looks = ['Very Low Contrast', 'Low Contrast', 'Medium Contrast',
                 'Medium High Contrast','High Contrast', 'Very High Contrast','None']

        look = bpy.context.scene.view_settings.look
        CM = bpy.context.scene.view_settings.view_transform
        i = Looks.index(look)
        if i < 6:
            i += 1
        else:
            i = 0

        bpy.context.scene.view_settings.look = Looks[i]

        if event.ctrl:
            if i > 0:
                bpy.context.scene.view_settings.look = Looks[i-1]

            else:
                bpy.context.scene.view_settings.look = Looks[6]

            if CM != 'False Color':
                bpy.context.scene.view_settings.view_transform= 'False Color'

            else:
                bpy.context.scene.view_settings.view_transform = 'Filmic'

        look = bpy.context.scene.view_settings.look
        CM = bpy.context.scene.view_settings.view_transform
        self.report({'INFO'}, 'Color view: %s Look: %s '% (CM,look))

        return {'FINISHED'}
