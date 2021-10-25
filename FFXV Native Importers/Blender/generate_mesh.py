import bpy

from .version_helper import (
    get_scene_objects,
    does_collection_exist,
    get_armature
)


def generate_mesh(state, mesh_data):
    mesh = bpy.data.meshes.new(mesh_data.name)
    mesh.from_pydata(mesh_data.VA, [], mesh_data.faces)

    if state.is_new_blender:
        for data in range(mesh_data.uv_count):
            mesh.uv_layers.new(name=mesh_data.name +
                               "_TXUV" + "_0" + str(data))
    else:
        for data in range(mesh_data.uv_count):
            mesh.uv_textures.new(name=mesh_data.name +
                                 "_TXUV" + "_0" + str(data))

    for i in range(mesh_data.uv_count):
        uv_data = mesh_data.UV_data[i]
        uv_dictionary = {i: uv for i, uv in enumerate(uv_data)}
        per_loop_list = [0.0] * len(mesh.loops)

        for loop in mesh.loops:
            per_loop_list[loop.index] = uv_dictionary.get(loop.vertex_index)

        per_loop_list = [uv for pair in per_loop_list for uv in pair]
        mesh.uv_layers[data].data.foreach_set("uv", per_loop_list)

    mesh.validate()
    mesh.update()

    mesh_object = bpy.data.objects.new(mesh_data.name, mesh)

    scene_objects = get_scene_objects()
    if state.is_new_blender:
        if does_collection_exist(mesh_data.file_name):
            bpy.data.collections[mesh_data.file_name].objects.link(
                mesh_object)
        else:
            newCol = bpy.data.collections.new(mesh_data.file_name)
            if does_collection_exist(mesh_data.group_name):
                bpy.data.collections[mesh_data.group_name].children.link(
                    newCol)
            else:
                bpy.context.scene.collection.children.link(newCol)
            bpy.data.collections[mesh_data.file_name].objects.link(
                mesh_object)
    else:
        bpy.context.scene.objects.link(mesh_object)
        for key in scene_objects:
            if key.type == 'ARMATURE' and mesh_data.group_name in key.name:
                mesh_object.parent = key
                break
        mesh_object.select = True

    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

    # Thanks Sai for the fix here
    layer = bpy.context.view_layer
    layer.update()

    weight_data = generate_weight_data(
        mesh_data.weights, mesh_data.bone_ids, mesh_data.bone_dictionary)

    for key in weight_data:
        for i in range(len(weight_data[key]['weights'])):
            vertex_weight = weight_data[key]['weights'][i]
            bone_name = weight_data[key]['boneNames'][i]
            vertex_group = mesh_object.vertex_groups.get(bone_name)
            if not vertex_group:
                vertex_group = mesh_object.vertex_groups.new(
                    name=bone_name)
            vertex_group.add([key], vertex_weight, 'ADD')

    mod = mesh_object.modifiers.new(
        type="ARMATURE", name="ArmatureMOD")
    mod.use_vertex_groups = True

    armature = get_armature(scene_objects, state.group_name)
    mod.object = armature


def generate_weight_data(weights, bone_ids, bone_dictionary):
    """
    An abomination that for whatever reason generates
    more dictionary of dictionaries fuckery
    """
    outer_count = -1
    weight_data = {}

    for weight in weights:
        outer_count += 1
        weight_data[outer_count] = {"boneNames": [], "weights": []}
        inner_count = -1

        for i in weight:
            inner_count += 1
            bone_id = int(bone_ids[outer_count][inner_count])

            if i != 0:
                bone = bone_dictionary[bone_id]
                weight_data[outer_count]["weights"].append(i)
                weight_data[outer_count]["boneNames"].append(bone)

    return weight_data
