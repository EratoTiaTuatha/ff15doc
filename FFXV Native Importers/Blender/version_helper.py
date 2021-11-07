"""
Helper methods to perform various actions
based on the Blender version
"""

import bpy

is_new_blender = bpy.app.version >= (2, 80, 0)


def get_scene_objects():
    if is_new_blender:
        return bpy.context.view_layer.objects
    else:
        return bpy.context.scene.objects


def does_collection_exist(group_name):
    for collection in bpy.data.collections.items():
        if group_name in collection:
            return True
    return False


def does_armature_exist(scene_objects, group_name):
    exists = True
    for scene_object in scene_objects:
        if scene_object.type == 'ARMATURE' and group_name in scene_object.name:
            exists = False
    return exists


def get_armature(scene_objects, group_name):
    for scene_object in scene_objects:
        if scene_object.type == 'ARMATURE' and group_name in scene_object.name:
            return scene_object
