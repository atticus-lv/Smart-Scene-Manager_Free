import bpy


class Drop2floor(bpy.types.Operator):
    """drop all 2 floor
ctrl : drop each 2 floor
shift : drop 2 active
(alt: only mesh object)"""
    bl_idname = "object.drop2floor"
    bl_label = "D2F"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):

        objs = bpy.context.selected_objects
        active = bpy.context.active_object
        vertex_List = []; other_List=[]; mesh_List=[]; other_Z = []
        # orgin location OL # no mesh location NML # maxz(1)

        # drop all
        for obj in objs:
            mx = obj.matrix_world
            if obj.type == "MESH":
                minz = min((mx @ v.co)[2] for v in obj.data.vertices)
                if obj == active:
                    minz = min((mx @ v.co)[2] for v in obj.data.vertices)
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

        try:
            vertex_List.sort()
        except IndexError as e:
            active.location[2] = 0


        for obj in objs:
            mx = obj.matrix_world
            mx.translation.z -= vertex_List[0]
            # move mesh
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


            if obj in other_List and len(other_List) != 0:
                # move not-mesh
                if event.alt :
                    mx.translation.z += vertex_List[0]
                if event.shift:
                    if obj == active:
                        obj.location[2]= NOL
                    else:
                        if event.alt:
                            mx.translation.z -= vertex_List[0]
                        else:
                            obj.location[2] = maxz
                if event.ctrl:
                    obj.location[2] =0
                    if event.alt:
                        obj.location[2] = other_Z[other_List.index(obj)]

        return {'FINISHED'}
