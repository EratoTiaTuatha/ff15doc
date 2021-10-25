"""
For internal use only
Methods that assist in reading of mesh metadata from gfxbin
"""

import struct

from entities import MeshMetadata, MeshExtraMetadata
from _read_helper import (
    _read_part,
    _read_string,
    _read_unknown_count,
    _read_byte_count
)


def _read_mesh_count(gfxbin_file):
    """Reads and returns number of meshes from the gfxbin file"""
    gfxbin_file.seek(
        11, 1)               # Skip 11 unknown bytes to get to the part we need
    _read_string(gfxbin_file)  # Skip the base name (usually Parts_Base)
    _read_part(gfxbin_file)    # Skip what may be a Count?

    struct.unpack("B", gfxbin_file.read(1))[0] - 0xA0    # Skip Name Size
    _read_string(gfxbin_file)								# Skip Cluster Name
    return _read_part(gfxbin_file)


def _read_mesh_metadata(gfxbin_file):
    """
    Reads relevant mesh matadata from gfxbin file
    Returns metadata as MeshMetadata entity
    """
    # TODO: Come back and remove if not referenced anywhere else
    # mesh_name = file_info.file_name_no_extension + \
    #   "__" + _read_mesh_name(gfxbin_file)

    mesh_metadata = _read_mesh_header(gfxbin_file)

    mesh_metadata.extras.append(
        _read_extra_mesh_metadata(gfxbin_file, True))

    mesh_metadata.extras.append(
        _read_extra_mesh_metadata(gfxbin_file, False))

    _read_mesh_header_end(gfxbin_file, mesh_metadata)

    return mesh_metadata


def _read_mesh_name(gfxbin_file):
    """
    Skip unneeded parts of the file
    Return the name of the next mesh in the file
    """
    name_size = struct.unpack("B", gfxbin_file.read(1))[0] - 0xA0
    mesh_name = _read_string(gfxbin_file)

    gfxbin_file.seek(1, 1)          # Skip the next byte
    count = _read_part(gfxbin_file)  # Not sure what this is a count of

    # Skip unknown parts
    for i in range(count):
        _read_part(gfxbin_file)

    struct.unpack("B", gfxbin_file.read(1))[0]  # Skip byte
    struct.unpack("B", gfxbin_file.read(1))[0]  # Skip byte (0xC2)

    # Skip another 6 times as we don't need these parts
    for i in range(6):
        _read_part(gfxbin_file)

    struct.unpack("B", gfxbin_file.read(1))[0]  # Skip byte 0xC3/03

    # Not too sure what this does
    # Appears to skip more unneeded stuff
    wb = gfxbin_file.tell()
    check = _read_part(gfxbin_file)
    wba = gfxbin_file.tell() - wb
    gfxbin_file.seek(-wba, 1)

    if isinstance(check, float):
        # If the check is a float, we need to skip the next 12 parts
        for i in range(12):
            _read_part(gfxbin_file)

    gfxbin_file.seek(1, 1)  # Skip byte
    return mesh_name


def _read_mesh_header(gfxbin_file):
    """
    Reads the header data of the mesh and stores it in a MeshMetadata entity
    Returns the header data
    """
    metadata = MeshMetadata()
    metadata.read_count = _read_part(gfxbin_file)
    metadata.face_type = struct.unpack("B", gfxbin_file.read(1))[0]
    metadata.faces_offset = _read_part(gfxbin_file)
    metadata.byte_size = _read_part(gfxbin_file)
    metadata.vertex_count = _read_part(gfxbin_file)
    metadata.chunk_count = struct.unpack("B", gfxbin_file.read(1))[0] & 0xF
    gfxbin_file.seek(2, 1)  # Skip next 2 bytes (not sure what these are)
    return metadata


def _read_mesh_header_end(gfxbin_file, metadata):
    """
    Reads the remainder of the mesh header and stores its values
    in the existing MeshMetadata entity
    This is separate to _read_mesh_header due to needing a skip between
    Ideally this should be refactored so this method
    does not mutate the input
    """
    metadata.mesh_data_start = _read_part(gfxbin_file)
    metadata.mesh_total_byte_size = _read_part(gfxbin_file)
    metadata.lod_check = _read_lod_check(gfxbin_file)


def _read_lod_check(gfxbin_file):
    """
    Not sure what the LOD check is
    Skips unneeded parts of the mesh header and returns the first LOD
    """
    unknown_byte = struct.unpack("B", gfxbin_file.read(1))[0]
    if unknown_byte != 0:
        gfxbin_file.seek(-1, 1)     # I guess this is important if not zero?

    # Skip byte (may be a count of some sort?)
    struct.unpack("B", gfxbin_file.read(1))[0]

    # Skip next 46 bytes (not sure what these are)
    gfxbin_file.seek(46, 1)
    lod_0 = _read_part(gfxbin_file)
    _read_part(gfxbin_file)          # Skip lod_1 (guess not needed?)
    _read_part(gfxbin_file)          # Skip lod_2 (guess not needed?)

    # Skip next two bytes (0xC2 / 0xC3)
    struct.unpack("H", gfxbin_file.read(2))[0]

    # Skip next part as unneeded (unsure what this is)
    _read_part(gfxbin_file)

    count_byte = struct.unpack("B", gfxbin_file.read(1))[0]
    count = _read_unknown_count(count_byte)
    # Skip next part as unneeded (unsure what this is)
    _read_part(gfxbin_file)
    struct.unpack("B", gfxbin_file.read(1))[0]  # Skip byte (was named zero?)

    # Skip next parts as unneeded (unsure what these are)
    for i in range(count):
        _read_part(gfxbin_file)

    # Skip some extra parts if they exist
    skip_check = struct.unpack("B", gfxbin_file.read(1))[0]
    if skip_check == 0xC2:
        _read_part(gfxbin_file)
        skip_check2 = struct.unpack("B", gfxbin_file.read(1))[0]
        if skip_check2 == 0xC3:
            _read_part(gfxbin_file)
            struct.unpack("B", gfxbin_file.read(1))[
                0]  # Skip the next unknown byte
    else:
        # Next byte wasn't the check byte so go back one byte
        gfxbin_file.seek(-1, 1)

    return lod_0


def _read_extra_mesh_metadata(gfxbin_file, first):
    """
    Reads additional metadata about the mesh from the gfxbin file
    Needs to be called twice as two similar entries per mesh
    'first' should be True on first call to account for differences in bytes
    Returns extra metadata entities
    """
    metadata = MeshExtraMetadata()

    if first:
        metadata.stride = struct.unpack("<H", gfxbin_file.read(2))[0]
        metadata.item_count = struct.unpack("<H", gfxbin_file.read(2))[0] & 0xF
    else:
        metadata.stride = struct.unpack("B", gfxbin_file.read(1))[0]
        metadata.offset = _read_part(gfxbin_file)
        metadata.item_count = struct.unpack("<H", gfxbin_file.read(2))[0] & 0xF

    start = 0
    end = 0

    for i in range(metadata.item_count):
        struct.unpack("B", gfxbin_file.read(1))[
            0] - 0xA0  # Skip name size as not needed
        name = _read_string(gfxbin_file)
        metadata.data[name] = {}
        metadata.data[name]["d_type"] = struct.unpack(
            "B", gfxbin_file.read(1))[0]

        if i < metadata.item_count - 1:
            end = struct.unpack("B", gfxbin_file.read(1))[0]
        else:
            end = metadata.stride

        metadata.counter.append(end)

        if i == 0:
            metadata.bc = end
        else:
            start = metadata.counter[i-1]
            metadata.bc = end - start

        metadata.data[name]["start"] = start
        metadata.data[name]["end"] = end

        tbc = _read_byte_count(metadata.data[name]["d_type"])
        metadata.data[name]["item_subCount"] = metadata.bc // tbc

    # If this is the first record, we need to skip the next two bytes
    if first:
        gfxbin_file.seek(2, 1)

    return metadata
