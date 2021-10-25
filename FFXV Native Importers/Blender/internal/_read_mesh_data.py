"""
For internal use only
Reads all mesh data from the gpubin file
"""

import mathutils

import numpy

from ..entities import MeshData


def _read_mesh_data(file_info, gpubin_file, metadata):
    """
    Reads mesh data from the gpubin file
    Returns MeshData entity
    """
    if metadata.lod_check == 0:
        mesh_data = MeshData()
        _read_faces(file_info, gpubin_file, metadata, mesh_data)
        _read_normals_and_UVs(gpubin_file, metadata, mesh_data)
        return mesh_data
    else:
        return None


def _read_faces(file_info, gpubin_file, metadata, mesh_data):
    """
    Not entirely sure how this one works
    Appears to read some kind of data from the gpubin and reverse it
    to correct normals?
    Adds face data to the given MeshData entity
    """
    gpubin_file.seek(metadata.faces_offset, 0)

    cn = 0
    if metadata.face_type == 1:
        cn = metadata.byte_size // 4
        fi = numpy.fromfile(gpubin_file, dtype='<L', count=cn)
    else:  # 0
        cn = metadata.byte_size // 2
        fi = numpy.fromfile(gpubin_file, dtype='<H', count=cn)

    fi_0 = fi.view().reshape((cn // 3, 3))

    # change winding order so normals are correct (0 1 2 --> 2 1 0)
    if file_info.is_new_blender:
        fi_1 = numpy.flip(fi_0, 1)
    else:
        fi_1 = numpy.fliplr(fi_0)
    fi_1[:, [0, 1]] = fi_1[:, [1, 0]]  # 2 1 0 --> 1 2 0
    fi_2 = fi_1.ravel()

    mesh_data.face_data = tuple(fi_1)


def _read_normals_and_UVs(gpubin_file, metadata, mesh_data):
    gpubin_file.seek(metadata.mesh_data_start, 0)

    byte_count = metadata.vertex_count * metadata.extras[0].stride
    ti_0 = numpy.fromfile(gpubin_file, dtype='B', count=byte_count).reshape(
        (metadata.vertex_count, metadata.extras[0].stride))

    categories = ["BLENDWEIGHT", "BLENDINDICES"]
    for category in categories:
        _process_category_data(metadata.extras[0].data, category)

    for category in metadata.extras[0].data:
        data = metadata.extras[0].data[category]
        position_data = _get_position_data(
            data["start"],
            data["end"],
            metadata.vertex_count,
            data["item_subCount"],
            data["d_type"],
            ti_0)

        if category == "POSITION0":
            position_data[:, [1, 2]] = position_data[:, [2, 1]]
            mesh_data.VA = position_data.tolist()
        elif category == "BLENDINDICES":
            mesh_data.bone_ids = position_data.tolist()
        elif category == "BLENDWEIGHTS":
            mesh_data.weights = position_data.tolist()

    chunk2_start = metadata.mesh_data_start + metadata.extras[1].offset
    byteCount2 = metadata.vertex_count * metadata.extras[1].stride
    gpubin_file.seek(chunk2_start, 0)
    ti_1 = numpy.fromfile(gpubin_file, dtype='B', count=byteCount2).reshape(
        (metadata.vertex_count, metadata.extras[1].stride))

    uv_count = 0
    for type in metadata.extras[1].data:
        z = metadata.extras[1].data[type]
        position_data = _get_position_data(
            z["start"],
            z["end"],
            metadata.vertex_count,
            z["item_subCount"],
            z["d_type"],
            ti_1)

        if type == "NORMAL0":
            Normal_Array0 = position_data[:, 0:3].reshape(
                (metadata.vertex_count, 3))
            Normal_Array0[:, [1, 2]] = Normal_Array0[:, [2, 1]]
            Normal_Array = Normal_Array0.tolist()
        elif type == "TANGENT0":
            pass
        elif type == "TEXCOORD0":
            uv_count += 1
            position_data[:, 1:2] *= -1
            position_data[:, 1:2] += 1
            uvData0 = position_data.tolist()
            mesh_data.UV_data[0] = [mathutils.Vector(x) for x in uvData0]
        elif type == "TEXCOORD1":
            uv_count += 1
            position_data[:, 1:2] *= -1
            position_data[:, 1:2] += 1
            uvData1 = position_data.tolist()
            mesh_data.UV_data[1] = [mathutils.Vector(x) for x in uvData1]
        elif type == "TEXCOORD2":
            uv_count += 1
            position_data[:, 1:2] *= -1
            position_data[:, 1:2] += 1
            uvData2 = position_data.tolist()
            mesh_data.UV_data[2] = [mathutils.Vector(x) for x in uvData2]
        elif type == "TEXCOORD3":
            uv_count += 1
            position_data[:, 1:2] *= -1
            position_data[:, 1:2] += 1
            uvData3 = position_data.tolist()
            mesh_data.UV_data[3] = [mathutils.Vector(x) for x in uvData3]
        elif type == "NORMAL4FACTORS0":
            pass
        elif type == "NORMAL2FACTORS0":
            pass

        mesh_data.uv_count = uv_count


def _process_category_data(data, category):
    """
    Appears to perform some operations and update
    the dictionary of dictionaries accordingly
    This format is awful to work with and should ideally
    be rewritten to use more meaningful data structures
    and this method refactored to not mutate the input
    """
    category_dictionary = {}
    category_count = sum(category in p for p in data)
    id = category_count - 1

    first_match = category + "0"
    last_match = category + str(id)

    new_sub = data[first_match]["item_subCount"] * category_count
    new_end = data[last_match]["end"]

    if category[-1] != "S":
        new_key = category + "S"
    else:
        new_key = category

    a = data[first_match].copy()
    if category_count > 0:
        for x in data.keys():
            if category in x:
                category_dictionary[x] = data[x]
        for i in category_dictionary.keys():
            del data[i]
        data[new_key] = a
        data[new_key]["item_subCount"] = new_sub
        data[new_key]["end"] = new_end


def _get_position_data(start, end, count, subCount, type, data):
    """
    Gets Position Data? based on which type is input
    Returns the position data
    """
    if type == 6:       # NORMAL FACTORS
        pos = data[:, start:end].ravel().view(
            dtype='<H').reshape((count, subCount))  # ?
        positionData = pos.astype(numpy.float64)
        return positionData
    elif type == 8:
        pos = data[:, start:end].ravel().view(
            dtype='<H').reshape((count, subCount))
        return pos
    elif type == 12:
        pos = data[:, start:end].ravel().view(
            dtype='B').reshape((count, subCount))
        positionData = pos.astype(numpy.float64)
        positionData /= 255.0
        return positionData
    elif type == 13:
        pos = data[:, start:end].ravel().view(
            dtype='B').reshape((count, subCount))
        return pos
    elif type == 14:    # Vectors
        pos = data[:, start:end].ravel().view(
            dtype='b').reshape((count, subCount))
        positionData = pos.astype(numpy.float64)
        positionData /= 255.0
        return positionData
    elif type == 16:
        pos = data[:, start:end].ravel().view(
            dtype='<f').reshape((count, subCount))
        positionData = pos.astype(numpy.float64)
        return positionData
    elif type == 20:    # COLOR
        # Original code below makes no sense
        # as the returned value is unassigned
        # updated to behave like case 13 in hopes
        # that this will fix it
        # -----------------------------------
        # pos = data[:, start:end].ravel().view(
        #     dtype='<L').reshape((count, subCount))
        # return positionData
        pos = data[:, start:end].ravel().view(
            dtype='<L').reshape((count, subCount))
        return pos
    elif type == 26:
        pos = data[:, start:end].ravel().view(
            dtype='<f2').reshape((count, subCount))
        positionData = pos.astype(numpy.float64)
        return positionData
    else:
        print("\n\n")
        print("*******************")
        print("unhandled data type")
        print("*******************")
        print("\n\n")
