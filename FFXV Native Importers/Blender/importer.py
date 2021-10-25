"""
Main method for importing the model data
Calls many internal methods in a specific order
The order is important due to movement of the cursor within the files
"""

from .internal._read_bone_dictionary import _read_bone_dictionary
from .internal._read_mesh_metadata import _read_mesh_count, _read_mesh_metadata
from .internal._read_mesh_data import _read_mesh_data
from .internal._read_armature_data import _read_armature_data


def import_mesh_data(state):
    """
    Reads mesh data from the gfxbin and gpubin
    Returns MeshData[]
    """
    gfxbin_file = open(state.gfxbin_file_path, "rb")

    if state.gpubin_file_exists:
        gpubin_file = open(state.gpubin_file_path, "rb")

    mesh_data = []
    bone_dictionary = _read_bone_dictionary(gfxbin_file)

    for i in range(_read_mesh_count(gfxbin_file)):
        mesh_metadata = _read_mesh_metadata(gfxbin_file)

        if mesh_metadata.lod_check == 0 and state.gpubin_file_exists:
            mesh = _read_mesh_data(state, gpubin_file, mesh_metadata)
            if mesh is not None:
                # Shouldn't need bone_dictionary stored per mesh
                # Refactor this later
                mesh_data.bone_dictionary = bone_dictionary
                mesh_data.append()

    gfxbin_file.close()

    if state.gpubin_file_exists:
        gpubin_file.close()

    return mesh_data


def import_armature_data(state):
    """
    Reads armature data from the amdl
    Returns ArmatureData
    """
    if state.amdl_file_exists:
        amdl_file = open(state.amdl_file_path, "rb")
        armature_data = _read_armature_data(amdl_file)
        amdl_file.close()
    else:
        return None
