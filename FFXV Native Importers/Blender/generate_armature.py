"""
Builds a Blender Armature from armature data
imported into the ArmatureData class
"""

import mathutils

import bpy
from rna_prop_ui import rna_idprop_ui_prop_get
from numpy.linalg import inv

from version_helper import does_collection_exist


def generate_armature(state, armature_data):
    if armature_data is None:
        return

    armature_name = state.group_name + "_Armature"

    armature = bpy.data.armatures.new(armature_name)

    if state.is_new_blender:
        armature.display_type = 'STICK'
    else:
        armature.draw_type = 'WIRE'

    armature_object = bpy.data.objects.new(armature_name, armature)
    armature_object.data.name = state.group_name + "_Armature_Data"

    if state.is_new_blender:
        if does_collection_exist(state.group_name):
            bpy.data.collections[state.group_name].objects.link(
                armature_object)
        else:
            bpy.context.scene.collection.objects.link(armature_object)

        bpy.context.view_layer.objects.active = armature_object
        armature_object.show_in_front = True
    else:
        bpy.context.scene.objects.link(armature_object)
        bpy.context.scene.objects.active = armature_object
        bpy.context.object.show_x_ray = True

    bpy.ops.object.mode_set(mode='EDIT')

    for bone in armature_data.bones:
        new_bone = bpy.context.active_object.data.edit_bones.new(bone.name)
        rna_idprop_ui_prop_get(new_bone, "ID", create=True)
        new_bone["ID"] = bone.id

        if bone.id > 0:
            parent_id = armature_data.parent_IDs[bone.id - 1]
            parent_name = armature_data.bones[parent_id].name

            head_position_matrix = inv(bone.head_position_matrix)
            head_position = mathutils.Vector(
                (head_position_matrix[0][3],
                 head_position_matrix[1][3],
                 head_position_matrix[2][3]))

            parent = bpy.context.active_object.data.edit_bones[parent_name]
            parent.tail = head_position

            new_bone.parent = parent
            new_bone.head = head_position
            new_bone.tail = head_position + \
                mathutils.Vector((0.001, 0.001, 0.001))
        else:
            new_bone.head = mathutils.Vector((0, 0, 0))
            new_bone.tail = mathutils.Vector((0, 0, 0.1))

    bpy.ops.object.mode_set(mode='OBJECT')
