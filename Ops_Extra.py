#-*- coding =utf-8 -*-
import bpy
import os
import time
import blf
import bgl
from bpy_extras import view3d_utils
from bpy.types import Menu,Panel,Operator
from bpy.props import *


def viewlayer_fix_291(self,context):
    if bpy.app.version >= (2,91,0):
        return context.view_layer.depsgraph
    else:
        return context.view_layer

#import
def get_region_size(context):
    region = context.region
    cx = region.width // 2
    cy = region.height // 2
    return region.width,region.height


def CN_ON(context):
    if context.preferences.view.use_translate_interface == True:
        return  bpy.app.translations.locale == 'zh_CN'
#import

class Translater(Operator):
    """If not English,translate interface between English and your language"""
    bl_idname = "interface.simple_translater"
    bl_label = "Translate"
    
    def execute(self, context):
        if context.preferences.view.use_translate_interface == 0:
            context.preferences.view.use_translate_interface = 1
        else:
            context.preferences.view.use_translate_interface = 0
        return {'FINISHED'}


class ExportObj(Operator):
    """export select obj to blend file dir
ctrl: export as fbx"""
    bl_idname = "object.export_obj"
    bl_label = "export_obj"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context,event):
        # 导出所选obj
        pref = context.preferences.addons[__package__].preferences
        active = context.object
        selection = context.selected_editable_objects

        datenow = str(time.strftime("%m-%d", time.localtime()))
        timenow = str(time.strftime("%H_%M", time.localtime()))
        blend_name = bpy.path.basename(context.blend_data.filepath)[:-6]

        if context.blend_data.filepath != '':
            try:
                blendpath = context.preferences.addons[__package__].preferences.tempdir
                # right path
                if not pref.usecustom :
                    blendpath = bpy.data.filepath

                directory_path = os.path.dirname(blendpath) + "\\" + f"{blend_name}_export"
                try :
                    if not os.path.exists(directory_path):
                        os.makedirs(directory_path)
                except:
                    self.report({'ERROR'}, 'File Path Error')

                postfix = f'{blend_name}'

                if pref.usenum:
                    postfix = postfix + '_' + str(len(selection))
                if pref.useactiveN:
                    postfix = postfix +'_' + active.name
                if pref.usedate:
                    postfix = postfix + '_' + datenow
                if pref.usetime:
                    postfix = postfix + '_' + timenow

                form = '.obj'
                if event.ctrl:
                    form = '.fbx'

                directory = directory_path +"\\" + postfix + form


                if form == '.obj':
                    bpy.ops.export_scene.obj(filepath=directory, axis_up='Y', axis_forward='-Z',
                                         use_selection=True, use_materials=True, use_uvs=True, use_normals=True)
                    self.report({'INFO'}, 'finish! export obj to %s.' % (directory))
                elif form == '.fbx':
                    bpy.ops.export_scene.fbx(filepath=directory, object_types = {'ARMATURE','CAMERA','EMPTY','LIGHT','MESH','OTHER'},
                                             use_mesh_modifiers = True,use_mesh_modifiers_render = True,use_subsurf =True,
                                             use_selection=True)
                    self.report({'INFO'}, 'finish! export fbx to %s.'% (directory))

            except IndexError as I:
                self.report({'ERROR'}, 'no select object .')
        else:
            self.report({'ERROR'}, 'Save your file first.')

        return {'FINISHED'}






