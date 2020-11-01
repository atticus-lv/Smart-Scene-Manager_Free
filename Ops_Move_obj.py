#-*- coding =utf-8 -*-
import bpy

class OBJECT_OT_Drop2floor(bpy.types.Operator):
    """drop all 2 floor
ctrl : drop each 2 floor
shift : drop 2 active"""
    bl_idname = "object.drop2floor"
    bl_label = "D2F"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        OM = context.preferences.addons[__package__].preferences.OM
        objs = context.selected_objects
        active = context.active_object
        vertex_List = []; other_List=[]; mesh_List=[]; other_Z = []
        # get location ### origin location OL # no mesh location NML # maxz(1)
        for obj in objs:
            mx = obj.matrix_world
            if obj.type == "MESH":
                minz = min((mx @ v.co)[2] for v in obj.data.vertices)
                if obj == active:
                    OL = obj.location[2]
                    maxz = max((mx @ v.co)[2] for v in obj.data.vertices)
                mesh_List.append(obj)
                vertex_List.append(minz)

            elif obj.type != "MESH" :
                NMZ = obj.location[2]
                other_List.append(obj)
                other_Z.append(NMZ)
                if obj == active:
                    NOL = obj.location[2]
                    maxz = NOL

        vertex_List.sort()

        try:
            for obj in objs:
                mx = obj.matrix_world
                mx.translation.z -= vertex_List[0]
                #apply location to mesh object
                if obj in mesh_List:
                    minz = min((mx @ v.co)[2] for v in obj.data.vertices)
                    if event.shift :
                        if obj == active:
                            obj.location[2] = OL
                        else:
                            minz = min((mx @ v.co)[2] for v in obj.data.vertices)
                            mx.translation.z -= minz - maxz
                    if event.ctrl:
                        mx.translation.z -= minz
                #apply location to not mesh object
                if obj in other_List and len(other_List) != 0:
                    # move not-mesh
                    if OM :
                        mx.translation.z += vertex_List[0]
                    if event.shift:
                        if obj == active:
                            obj.location[2]= NOL
                        else:
                            if OM:
                                obj.location[2] = other_Z[other_List.index(obj)]
                            else:
                                obj.location[2] = maxz
                    elif event.ctrl:
                        obj.location[2] =0
                        if OM:
                            obj.location[2] = other_Z[other_List.index(obj)]
        #only select not mesh object
        except IndexError as e:
            other_Z.sort()
            for obj in objs:
                if len(vertex_List) == 0:
                    obj.location[2] -= other_Z[0]
                    if event.shift:
                        obj.location[2] = NOL
                    elif event.ctrl:
                        obj.location[2] = 0
                else:
                    obj.location[2] = 0

        return {'FINISHED'}


class OBJECT_OT_LookAT(bpy.types.Operator):
    """select objects look at active object
shift: add look-at  constrains"""
    bl_idname = "object.look_at"
    bl_label = "Track"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        active = context.active_object
        activename = active.name
        objs = context.selected_objects

        if len(objs) < 2:
            self.report({'ERROR'}, ' select 2 object .')
        else:
            for obj in objs:
                if not event.shift:
                    # method  from gaffer/operation/class GAFFER_OT_aim_light
                    if obj != active:
                        obj_loc = obj.matrix_world.to_translation()
                        direction = active.location - obj_loc
                        # point obj '-Z' and use its 'Y' as up
                        rot_quat = direction.to_track_quat('-Z', 'Y')
                        if obj.rotation_mode == 'QUATERNION':
                            obj.rotation_quaternion = rot_quat
                        else:
                            obj.rotation_euler = rot_quat.to_euler()

                if event.shift:
                    if obj != active:
                        # add constrain
                        con = obj.constraints.new(type='DAMPED_TRACK')
                        con.name = f"Look at {activename}"
                        con.target = active
                        con.track_axis = 'TRACK_NEGATIVE_Z'

        return {'FINISHED'}


class OBJECT_OT_TransPSR(bpy.types.Operator):
    """Transform selected object(s) to active"""
    bl_idname = "object.trans_psr"
    bl_label = "TransPSR"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        active = context.active_object
        objs = context.selected_objects

        def get_PSR():
            PSR = [active.location, active.scale, active.rotation_euler]
            return PSR

        def apply_PSR(PSR, index):
            for obj in objs:
                if obj != active:
                    if index == 0:
                        obj.location = PSR[index]
                    elif index == 1:
                        obj.scale = PSR[index]
                    elif index == 2:
                        obj.rotation_euler = PSR[index]
        # main
        if len(objs) < 2 :
            self.report({'ERROR'}, ' select 2 more object .')
        else:
            if context.preferences.addons[__package__].preferences.Tp :
                apply_PSR(get_PSR(),0)

            if context.preferences.addons[__package__].preferences.Ts:
                apply_PSR(get_PSR(),1)

            if context.preferences.addons[__package__].preferences.Tr:
                apply_PSR(get_PSR(),2)

        return {'FINISHED'}


class PANEL_PT_TransPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_idname = "PANEL_PT_TransPanel"
    bl_label = 'TransPSR'
    bl_region_type = 'HEADER'
    bl_category = ''

    def draw(self,context):
        row = self.layout.column().split().column().row(align=True)
        pref = context.preferences.addons[__package__].preferences
        row.prop(pref, "Tp", icon="ORIENTATION_GLOBAL", text='')
        row.prop(pref, "Ts", icon="ORIENTATION_LOCAL", text='')
        row.prop(pref, "Tr", icon="ORIENTATION_GIMBAL", text='')


class PANEL_PT_D2fPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_idname = "PANEL_PT_D2fPanel"
    bl_label = 'D2F'
    bl_region_type = 'HEADER'
    bl_category = ''

    def draw(self,context):
        row = self.layout.column().split().column().row(align=True)
        row.prop(context.preferences.addons[__package__].preferences, "OM", icon="MESH_DATA",text = '')