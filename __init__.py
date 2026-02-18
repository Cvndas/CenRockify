bl_info = {
    "name": "CenRockify",
    "author": "Lrodas",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "location": "View3D > Sidebar > Centradigon Tab",
    "description": "Duplicate rocks and setup LODs",
    "category": "Centradigon Tools",
}
rockCollectionName = "PaintedRocksWithLods"


import bpy

# ----------------- Core Functions -----------------

def DupeObject(inputObject):
    newObject = inputObject.copy()
    newObject.data = inputObject.data
    bpy.context.collection.objects.link(newObject)
    return newObject

def MoveToCollection(object, targetCollectionName):
    newCollection = bpy.data.collections.get(targetCollectionName)
    if newCollection is None:
        newCollection = bpy.data.collections.new(targetCollectionName)
        bpy.context.scene.collection.children.link(newCollection)
    for col in object.users_collection:
        col.objects.unlink(object)
    newCollection.objects.link(object)

def SetupModifier(object):
    for modifier in list(object.modifiers):
        if modifier.type == 'NODES' and modifier.node_group:
            if modifier.node_group.name == "RockPainter_V2":
                modifier.show_viewport = True
                modifier.show_render = True
                modifier["Socket_11"] = True
        elif modifier.type == 'DECIMATE':
            object.modifiers.remove(modifier)

def RockPainterLodder():
    activeCollection = bpy.context.collection
    if activeCollection is None:
        print("No active collection")
        return

    objectsWithRockpainter = []
    for obj in activeCollection.objects:
        for modifier in obj.modifiers:
            if modifier.type == 'NODES' and modifier.node_group:
                if modifier.node_group.name == "RockPainter_V2":
                    objectsWithRockpainter.append(obj)
                    modifier.show_viewport = False
                    modifier.show_render = False

    paintedRocksCollection = bpy.data.collections.get(rockCollectionName)
    if paintedRocksCollection:
        for oldRock in list(paintedRocksCollection.objects):
            bpy.data.objects.remove(oldRock, do_unlink=True)

    rockIndex = 0
    for obj in objectsWithRockpainter:
        dupeLod0 = DupeObject(obj)
        dupeLod1 = DupeObject(obj)
        dupeLod0.name = f"Rock_{rockIndex}_LOD0"
        dupeLod1.name = f"Rock_{rockIndex}_LOD1"
        MoveToCollection(dupeLod0, rockCollectionName)
        MoveToCollection(dupeLod1, rockCollectionName)
        SetupModifier(dupeLod0)
        SetupModifier(dupeLod1)
        decimator = dupeLod1.modifiers.new(name="RockLod1Decimate", type='DECIMATE')
        decimator.ratio = 0.1
        rockIndex += 1

# ----------------- Operator & Panel -----------------

class ROCKPAINTER_LODDER_OT_Run(bpy.types.Operator):
    bl_idname = "object.rockpainter_lodder"
    bl_label = "RockPainter LODder"
    bl_description = "Duplicate objects with RockPainter_V2 and setup LODs"

    def execute(self, context):
        RockPainterLodder()
        return {'FINISHED'}

class ROCKPAINTER_LODDER_PT_Panel(bpy.types.Panel):
    bl_label = "RockPainter LODder"
    bl_idname = "VIEW3D_PT_rockpainter_lodder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Centradigon"

    def draw(self, context):
        self.layout.operator("object.rockpainter_lodder", text="Run LOD Setup")

# ----------------- Registration -----------------

classes = [
    ROCKPAINTER_LODDER_OT_Run,
    ROCKPAINTER_LODDER_PT_Panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
