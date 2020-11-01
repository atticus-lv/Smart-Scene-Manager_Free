#-*- coding =utf-8 -*-
import bpy
import os

from bpy.types import Object, Scene, Panel, Operator,Menu,UIList,PropertyGroup
from bpy.props import *

class SSM_UL_ImageList(UIList):
    bl_idname = "ssm.image_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        # 'DEFAULT' and 'COMPACT' layout types should usually use the same draw code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            pass
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            pass

        # Image name and icon
        row = layout.row(align=True)
        row.prop(item, "name", text="", emboss=False, icon_value=icon)

        row = row.row(align=True)
        row.alignment = 'RIGHT'

        if item.use_fake_user:
            row.label(text="F")
        else:
            row.label(text=str(item.users))

        if item.packed_file:
            # row.label(icon='PACKAGE')
            # row.operator("image.unpack", text="", icon='PACKAGE', emboss=False)
            row.label(text="", icon='PACKAGE')


class IMAGE_OT_Remove(Operator):
    bl_idname = "image.remove"
    bl_label = "Remove"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        index = context.scene.image_list_index
        item = bpy.data.images[index]

        bpy.data.images.remove(item)

        return {'FINISHED'}


class SSM_OT_Pack(Operator):
    bl_idname = "ssm.pack"
    bl_label = "Pack and Unpack"
    bl_options = {'REGISTER', 'UNDO'}

    imagename:StringProperty(name="Image Name")

    def execute(self, context):
        img = bpy.data.images[self.imagename]

        if img.packed_file:
            img.unpack()
        else:
            img.pack()

        return {'FINISHED'}


class PopImageEditor(Operator):
    "View"
    bl_idname = "interface.pop_image_editor"
    bl_label = "Image Editor"

    imagename: StringProperty(name="image name")
    sizex:IntProperty(name="x")
    sizey: IntProperty(name="y")

    def execute(self, context):
        # Modify scene settings
        window = context.scene.render

        ORx = window.resolution_x
        ORy = window.resolution_y

        RX = 512
        RY = 512

        window.resolution_x = RX
        window.resolution_y = RY
        # window.resolution_percentage = 100

        # Call image editor window
        bpy.ops.render.view_show("INVOKE_DEFAULT")

        # Change area type
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        area.type = "IMAGE_EDITOR"
        area.ui_type = 'VIEW'
        context.space_data.image = bpy.data.images[self.imagename]
        if self.imagename != "Render Result":
            if max(self.sizex,self.sizey)<= 512:
                bpy.ops.image.view_zoom_ratio(ratio=1)
            elif max(self.sizex,self.sizey) >512 and max(self.sizex,self.sizey) <=1024:
                bpy.ops.image.view_zoom_ratio(ratio=0.5)
            elif max(self.sizex, self.sizey) > 1025 and max(self.sizex, self.sizey) <= 2048:
                bpy.ops.image.view_zoom_ratio(ratio=0.25)
            else:
                bpy.ops.image.view_zoom_ratio(ratio=0.125)

        # restore
        window.resolution_x = ORx
        window.resolution_y = ORy

        return {'FINISHED'}


class SSM_OT_RemoveUnused(Operator):
    bl_idname = "ssm.removeunused"
    bl_label = "Remove Unused"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pref = context.preferences.addons[__package__].preferences
        for img in bpy.data.images:
            if pref.filter_tpye == None:
                pass
            elif pref.filter_tpye =="FAKE":
                if img.use_fake_user == True:
                    bpy.data.images.remove(img)
            elif pref.filter_tpye == "NOUSER":
                 if img.users == 0 and img.use_fake_user == False:
                     bpy.data.images.remove(img)


        return {'FINISHED'}


