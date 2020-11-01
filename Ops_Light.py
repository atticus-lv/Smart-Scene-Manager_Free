#-*- coding =utf-8 -*-
import bpy
from bpy.types import Menu,Panel,Operator
from bpy.props import *
from .Ops_ModifyCam import visibleCollections


def getlight():
    light_list = []
    light_group = []
    coll_list = visibleCollections()

    coll_list.pop(0)

    for coll in coll_list:
        for obj in coll.all_objects:
            if obj.type == "LIGHT" and obj.ssm_light.Group != '':
                if obj.users_collection[0].name == coll.name:
                    light_list.append(obj)
                    light_group.append(obj.ssm_light.Group)

    light_group = list(set(light_group))
    light_list = list(set(light_list))

    return light_list, light_group


class ActiveLight(Operator):
    bl_idname = "view.active_light"
    bl_label = "active light"
    bl_options = {'REGISTER', 'UNDO'}
    # bl_options = {'INTERNAL'}

    LightName: bpy.props.StringProperty(name="Light")

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        light = bpy.data.objects[self.LightName]
        context.view_layer.objects.active = light
        light.select_set(True)
        return {'FINISHED'}


class SSM_OT_CreatLightGroup(Operator):
    "Creat light group from select"
    bl_idname = "ssm.creat_light_group"
    bl_label = "creat light group"
    bl_options = {'REGISTER', 'UNDO'}

    groupname: StringProperty(name="Group Name")

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) !=0

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == "LIGHT":
                obj.ssm_light.Group = self.groupname
                obj.ssm_light.ShowGroup = True
                obj.ssm_light.WorldSolo = False

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SSM_OT_RenameLightGroup(Operator):
    '''Rename'''
    bl_idname = "ssm.rename_light_group"
    bl_label = "Rename Group"
    bl_options = {'REGISTER', 'UNDO', }

    LightName: StringProperty(name="Light Name")
    oldname: StringProperty(name="Old Name")
    newname: StringProperty(name="Group name")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_x = 0.5
        row.prop(self, 'newname', text='')

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == "LIGHT" and obj.ssm_light.Group == self.oldname:
                obj.ssm_light.Group = self.newname

        return {'FINISHED'}

    def invoke(self, context, event):
        light = bpy.data.objects[self.LightName]
        self.oldname = light.ssm_light.Group
        self.newname = light.ssm_light.Group

        return context.window_manager.invoke_props_popup(self, event)


class RemoveLightGroup(Operator):
    bl_idname = "view.remove_group"
    bl_label = "Remove Group"
    bl_options = {'REGISTER', 'UNDO'}

    GroupName: StringProperty(name="Groupname")

    def execute(self, context):
        group = self.GroupName
        for obj in bpy.data.objects:
            if obj.type == "LIGHT" and obj.ssm_light.Group == group :
                obj.ssm_light.Group  = ''

        return {'FINISHED'}


class ToggleLightGroup(Operator):
    bl_idname = "view.toggle_group"
    bl_label = "active Group"
    bl_options = {'REGISTER', 'UNDO'}
    # bl_options = {'INTERNAL'}

    LightName: StringProperty(name="Lightdemo")

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        light = bpy.data.objects[self.LightName]
        if light.hide_viewport == False:
            light.hide_viewport = True
        else:
            light.hide_viewport = False

        hide_viewport = light.hide_viewport

        for obj in bpy.data.objects:
            if obj.type == "LIGHT" and obj.ssm_light.Group == light.ssm_light.Group:
                obj.hide_viewport = hide_viewport
                obj.hide_render = hide_viewport

        return {'FINISHED'}


# class SSM_OT_ExtendGroup(Operator):
#     bl_idname = "ssm.extend_group"
#     bl_label = "active Group"
#     bl_options = {'REGISTER', 'UNDO'}
#     # bl_options = {'INTERNAL'}
#
#     LightName: bpy.props.StringProperty(name="Lightdemo")
#
#     @classmethod
#     def poll(cls, context):
#         return context.object
#
#     def execute(self, context):
#         light = bpy.data.objects[self.LightName]
#
#         for obj in bpy.data.objects:
#             if obj.type == "LIGHT" and obj.ssm_light.Group == light.ssm_light.Group:
#                 obj.hide_viewport = hide_viewport
#                 obj.hide_render = hide_viewport
#
#         return {'FINISHED'}


class SSM_OT_SoloGroup(Operator):
    bl_idname = "ssm.solo_group"
    bl_label = "Solo Group"

    LightName: bpy.props.StringProperty(name="Light name")

    def execute(self, context):
        light_list, light_group = getlight()
        l = bpy.data.objects[self.LightName]
        group = l.ssm_light.Group
        context.scene.SoloGroup = group
        for light in light_list:
            if light.ssm_light.Group != group:
                light.ssm_light.ShowGroup = False
            else:
                light.ssm_light.ShowGroup = True

        return {'FINISHED'}


class SSM_OT_SoloSingle(Operator):
    bl_idname = "ssm.solo_single"
    bl_label = "Solo In Group"

    LightName: StringProperty(name="Light name")

    def execute(self, context):
        light_list, light_group = getlight()
        l = bpy.data.objects[self.LightName]
        group = l.ssm_light.Group
        context.scene.SoloGroup = group

        for light in light_list:
            l.ssm_light.Solo = True
            if light.ssm_light.Group == group and light != l:
                l.ssm_light.Solo = False
                light.hide_viewport = True
                light.hide_render = True

        return {'FINISHED'}


class SSM_OT_ResetGroupSolo(Operator):
    bl_idname = "ssm.reset_group_solo"
    bl_label = "Reset Solo"

    def execute(self, context):
        light_list, light_group = getlight()
        for light in light_list:
            if light.ssm_light.ShowGroup == False:
                light.ssm_light.ShowGroup = True

        return {'FINISHED'}

