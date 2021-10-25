"""
For internal use only
Methods that assist in reading bone data from gfxbin
"""

import struct

from ._read_helper import _read_part, _read_string


def _read_bone_dictionary(gfxbin_file):
    """
    Reads bone data from the gfxbin file
    Skips bone names afterwards to prepare file for next method
    Returns a dictionary of { BoneID: BoneName }
    """
    # Key is the Bone ID
    # Value is the Bone Name
    bone_dictionary = {}

    bone_count = struct.unpack("B", gfxbin_file.read(1))[0] & 0xF
    seek_length = bone_count * 9

    # Skips over metadata that precedes the Bone IDs
    # (seems to just be a list of Bone Names)
    gfxbin_file.seek(seek_length, 1)

    # Skip the next 6 floats from this point as they are not relevant here
    for i in range(6):
        _read_part(gfxbin_file)

    # Skip the next 5 bytes as they are also in the way
    gfxbin_file.seek(5, 1)

    bone_name_count = _read_part(gfxbin_file)

    # Read the bone dictionary
    for i in range(bone_name_count):
        bone_name_size = struct.unpack("B", gfxbin_file.read(1))[0] - 0xA0
        bone_name = _read_string(gfxbin_file)
        bone_id = _read_part(gfxbin_file)
        if bone_id > 65535:
            bone_id >>= 16
            if bone_id == 65535:
                # If the bone ID exceeds the size limit
                # we just use the index of the iterator
                bone_dictionary[i] = bone_name
            else:
                bone_dictionary[bone_id] = bone_name
        else:
            # Not sure why we have to use the index of the iterator here
            bone_dictionary[i] = bone_name

    # Skip bone names to prepare file for next method
    _skip_bone_names(gfxbin_file)

    return bone_dictionary


def _skip_bone_names(gfxbin_file):
    """
    Skips past the bone names in the gfxbin file
    as we do not use them
    """
    bone_name_count = _read_part(gfxbin_file)
    for i in range(bone_name_count):
        for j in range(12):
            _read_part(gfxbin_file)
        name_size = struct.unpack("B", gfxbin_file.read(1))[0] - 0xA0
        bone_name = _read_string(gfxbin_file)
