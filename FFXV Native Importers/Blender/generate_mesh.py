import bpy

from .version_helper import (
    get_scene_objects,
    does_collection_exist,
    get_armature
)


def generate_mesh(state, mesh_data):
    mesh = bpy.data.meshes.new(mesh_data.name)
    mesh.from_pydata(mesh_data.VA, [], mesh_data.face_data)

    if state.is_new_blender:
        for i in range(mesh_data.uv_count):
            if i == 0:
                new_name = "map1"
            elif i == 1:
                new_name = "mapLM"
            else:
                new_name = "map" + str(i + 1)
            mesh.uv_layers.new(name=new_name)
    else:
        for i in range(mesh_data.uv_count):
            if i == 0:
                new_name = "map1"
            elif i == 1:
                new_name = "mapLM"
            else:
                new_name = "map" + str(i + 1)
            mesh.uv_textures.new(name=new_name)

    for i in range(mesh_data.uv_count):
        uv_data = mesh_data.UV_data[i]
        uv_dictionary = {i: uv for i, uv in enumerate(uv_data)}
        per_loop_list = [0.0] * len(mesh.loops)

        for loop in mesh.loops:
            per_loop_list[loop.index] = uv_dictionary.get(loop.vertex_index)

        per_loop_list = [uv for pair in per_loop_list for uv in pair]
        mesh.uv_layers[i].data.foreach_set("uv", per_loop_list)

    for i in mesh_data.vertex_colors:
        vertex_colors = mesh_data.vertex_colors[i]
        per_loop_list = [0.0] * len(mesh.loops)

        for loop in mesh.loops:
            if loop.vertex_index < len(vertex_colors):
                per_loop_list[loop.index] = vertex_colors[loop.vertex_index]

        per_loop_list = [colors for pair in per_loop_list for colors in pair]
        new_name = "colorSet"
        if i > 0:
            new_name += str(i)
        mesh.vertex_colors.new(name=new_name)
        mesh.vertex_colors[i].data.foreach_set("color", per_loop_list)

    mesh.validate()
    mesh.update()

    mesh_object = bpy.data.objects.new(mesh_data.name, mesh)

    scene_objects = get_scene_objects()
    state.get_collection().objects.link(mesh_object)
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
        type="ARMATURE", name="Armature")
    mod.use_vertex_groups = True

    armature = bpy.data.objects["Armature"]
    mod.object = armature

    mesh_object.parent = armature


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
