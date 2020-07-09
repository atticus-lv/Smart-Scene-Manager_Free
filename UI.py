import bpy
from bpy.types import Menu

class LF_Menu(Menu):
    bl_label = "Little function"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH'}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        #Left
        pie.operator("object.drop2floor")

        #Right
        box = pie.split().column()
        row = box.row(align=False)
        row.scale_y = 1.5
        row.operator("object.add_view_camera")

        #Right box
        row = box.row(align=True)
        row.operator("view3d.view_camera", text="ViewCam")
        row.operator("view3d.camera_to_view", text="Cam2View")
        row = box.row(align=True)
        row.operator("view.activecam", text="EnterCam")
        row.operator("view.filpcam", text="FilpCam")
        row = box.row(align=True)
        row.operator("wm.context_toggle", text="Lock Cam To View").data_path = "space_data.lock_camera"

        # Bottom box
        box = pie.split().column()
        row = box.row(align=False)
        row.scale_y = 1.5
        row.operator("object.export_obj")
        #row.operator("object.export_obj", text='FBX_WIP')

        #top
        box = pie.split().column()
        row = box.row(align=False)
        row.scale_y = 1.5
        row.operator("interface.simple_translater")
        row.operator("object.trans_psr")


        #top Left
        pie.operator("view3d.view_all", text="View All").center = True

        #top  Right
        # box = pie.split().column()
        # row = box.row(align=True)
        # row.scale_y = 1.5
        # row.operator("view3d.view_selected", text="View Selected")
        pie.operator("view3d.view_selected", text="View Selected")

        #left bottom
        pie.operator("render.render")

        # right bottom
        #pie.operator("object.lightcheck")
        box = pie.split().column()
        row = box.row(align=True)
        row.operator("view.setcama")
        row.scale_y = 1.5
        row.operator("view.light_check")

