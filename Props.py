#-*- coding =utf-8 -*-
import bpy
from bpy.types import Object, Scene, PropertyGroup
from bpy.props import IntProperty,BoolProperty,StringProperty,CollectionProperty,PointerProperty,FloatProperty

from .Ops_Light import getlight


def update_cam(self, context):
    cam = context.scene.camera.ssm_cam
    context.scene.render.resolution_percentage = cam.XYscale
    context.scene.render.resolution_x = cam.Rx
    context.scene.render.resolution_y = cam.Ry
    context.scene.view_settings.exposure = cam.EV


def update_lightgroup(self, context):
    light_list, light_group = getlight()
    for obj in light_list:
        if obj.ssm_light.ShowGroup == False:
            obj.hide_viewport = True
            obj.hide_render = True
        else:
            obj.hide_viewport = False
            obj.hide_render = False


def update_solo(self,context):
    for obj in bpy.data.objects:
        if obj.type == "LIGHT":
            if obj.hide_viewport or obj.hide_render:
                # obj.ssm_light.Solo = False
                pass


class SSM_CameraProps(bpy.types.PropertyGroup):
    StoreEV:BoolProperty(
        name="Store Exposure", default=False,
    )

    EV:FloatProperty(
        name='Exposure', default=0,
        soft_min=-3, soft_max=3,
        precision = 2,
        update = update_cam,
    )

    Rx:IntProperty(
        name='Resolution_x', default=1920,
        update = update_cam,
    )

    Ry:IntProperty(
        name='Resolution_y', default=1080,
        update = update_cam,
    )

    XYscale:IntProperty(
        name ='resolution Percentage',default = 100,
        min =1,soft_min = 50,soft_max =200,
        update = update_cam,
    )


class SSM_LightProps(bpy.types.PropertyGroup):

    Group:StringProperty(
        name ='Group Name',default = '',
        update = update_lightgroup
    )

    GroupStrength:FloatProperty(
        name='GroupStrength', default=1,
        soft_min=0.5, soft_max=2,
    )
    ShowGroup: BoolProperty(
        name='show group', default=False,update = update_lightgroup
    )

    Solo: BoolProperty(
        name='Solo', default=False,update = update_solo
    )


class SSM_PickerMatProps(PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    material: PointerProperty(
        name="Material",
        type=bpy.types.Material)


def PropsADD():
    # EV
    Scene.EV = FloatProperty(name='Exposure', default=0,)
    # Light group
    Scene.SoloGroup=StringProperty(name='Solo Group Name', default='',update = update_lightgroup)

    # props Group
    bpy.types.Object.ssm_cam = bpy.props.PointerProperty(type=SSM_CameraProps)
    bpy.types.Object.ssm_light = bpy.props.PointerProperty(type=SSM_LightProps)

    # props list
    bpy.types.Scene.image_list_index = IntProperty(name="image_list_index", default=0)
    bpy.types.Scene.mat_list_index = IntProperty(name="mat_list_index", default=0)
    # material picker
    bpy.types.Scene.picker_list = CollectionProperty(type=SSM_PickerMatProps)
    bpy.types.Scene.picker_list_index = IntProperty(name="picker_list_index", default=0)


def Proposremove():
    # remove group list
    del bpy.types.Scene.mat_picker
    del bpy.types.Scene.mat_list_index
    del bpy.types.Scene.image_list_index