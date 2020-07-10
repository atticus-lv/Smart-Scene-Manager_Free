import bpy
from mathutils import Vector


class Drop2floor(bpy.types.Operator):
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
        objs = bpy.context.selected_objects
        List = []
        #drop all
        for obj in objs:
            mx = obj.matrix_world
            if len(objs) > 1:
                if obj != bpy.context.object and obj.type == "MESH":
                    minz = [mx @ Vector(corner) for corner in obj.bound_box][0][2]
                    List.append(minz)
                # get active obj Z location
                elif obj == bpy.context.object and obj.type == "MESH" :
                    minz = min((mx @ v.co)[2] for v in obj.data.vertices)
                    List.append(minz)
                    maxz = max((mx @ v.co)[2] for v in obj.data.vertices)
                    LZ = obj.location[2]
                elif obj == bpy.context.object and obj.type != "MESH":
                    maxz = obj.location[2]

        List.sort()
        # drop all 2 floor
        for obj in objs:
            if obj.type == "MESH":
                mx = obj.matrix_world
                mx.translation.z -= List[0]

        if event.shift:
            for obj in objs:
               if obj == bpy.context.object and obj.type == "MESH":
                   obj.location[2] = LZ
               elif obj != bpy.context.object and obj.type == "MESH":
                   mx = obj.matrix_world
                   # drop to select
                   minz = min((mx @ v.co)[2] for v in obj.data.vertices)
                   mx.translation.z -= minz - maxz
               else:
                   pass

        if event.ctrl:
            for obj in objs:
                if obj.type == "MESH":
                    mx = obj.matrix_world
                    minz = min((mx @ v.co)[2] for v in obj.data.vertices)
                    # drop each
                    mx.translation.z -= minz

        return {'FINISHED'}

