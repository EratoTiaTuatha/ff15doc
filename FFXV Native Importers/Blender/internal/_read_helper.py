"""
Helper functions for reading certain parts of the
gfxbin, gpubin, and amdl files
"""

import struct


def _read_string(file, number_of_bytes=200):
    """
    Internal use only
    Reads a string of a specific length from the given file
    and returns the bytes converted back to ASCII
    """
    ascii_byte = file.read(1)
    string_value = ascii_byte
    byte_count = 0
    while ascii_byte and ord(ascii_byte) != 0 and byte_count < number_of_bytes:
        ascii_byte = file.read(1)
        string_value += ascii_byte
        byte_count += 1
    return string_value[:-1].decode('ascii', errors='ignore')


def _align(ptr, alignment):
    """
    Internal use only
    Not really sure what this voodoo magic does
    """
    alignment -= 1
    return (ptr + alignment) & ~alignment


def _read_part(file):
    """
    Internal use only
    Unsure exactly what this does
    Seems to detect patterns and read specific number of bytes accordingly
    Returns the read bytes
    """
    ch = struct.unpack("B", file.read(1))[0]
    if ch == 0xCE:
        val = struct.unpack("<L", file.read(4))[0]
    elif ch == 0xCD:
        val = struct.unpack("<H", file.read(2))[0]
    elif ch == 0xCC:
        val = struct.unpack("B", file.read(1))[0]
    elif ch == 0xCA:
        val = struct.unpack("<f", file.read(4))[0]
    elif ch == 0xDE:
        val = struct.unpack("<H", file.read(2))[0]
    elif ch == 0xDC:
        val = struct.unpack("<H", file.read(2))[0]
    else:
        val = ch
        if (val & 0xF0) >> 4 == 9:
            val &= 0xF
    return val


def _read_unknown_count(byte):
    """
    Internal use only
    Not really sure what this does
    Seems to convert a byte to a respective count value
    Returns an integer count value in (0, 1, 4, 7, 10)
    """
    count = 0
    if byte == 0x91:
        count = 1
    elif byte == 0x92:
        count = 4
    elif byte == 0x93:
        count = 7
    elif byte == 0x94:
        count = 10
    return count


def _read_byte_count(data_type):
    """
    Internal use only
    Type is an integer corresponding to a data type
    The integer comes from the GFXBin
    Returns the number of bytes in the given data type
    """
    byte_count = 0
    if data_type == 6:
        byte_count = 2
    elif data_type == 8:
        byte_count = 2
    elif data_type == 12:
        byte_count = 1
    elif data_type == 13:
        byte_count = 1
    elif data_type == 14:
        byte_count = 1
    elif data_type == 16:
        byte_count = 4
    elif data_type == 26:
        byte_count = 2
    return byte_count


def _is_amdl_from_episode_duscae(amdl_file):
    """
    Internal use only
    Checks certain parts of the amdl file to determine if
    it is from Episode Duscae
    """
    is_episode_duscae = True
    amdl_file.seek(160, 0)
    for x in range(112):
        if struct.unpack("<L", amdl_file.read(4))[0] != 0:
            is_episode_duscae = False
            break

    return is_episode_duscae


def _skip_top(gfxbin_file, file_size):
    """
    Internal use only
    Skips the data at the top of the gfxbin file
    """
    lt = []
    unk0 = _read_part(gfxbin_file)
    unk1 = _read_part(gfxbin_file)
    strlen_n = struct.unpack("B", gfxbin_file.read(1))[0] - 0xA0
    stop, p = False, 0
    while not stop and gfxbin_file.tell() < file_size:
        st = _read_string(gfxbin_file)
        if "asset_uri" in st:
            stop = True
            unk0 = struct.unpack("B", gfxbin_file.read(1))[0]
            strlen0 = struct.unpack("B", gfxbin_file.read(1))[0]  # asset_uri
            lt.append({"asset": _read_string(gfxbin_file)})         # asset_uri
            strlen1 = struct.unpack("B", gfxbin_file.read(1))[0]  # ref
            lt.append({"ref": _read_string(gfxbin_file)})           # ref
            unk1 = struct.unpack("B", gfxbin_file.read(1))[0]
            strlen2 = struct.unpack("B", gfxbin_file.read(1))[0]
            lt.append({"gmdl": _read_string(gfxbin_file)})          # gmdl file

            t = gfxbin_file.tell()
            z0 = struct.unpack("B", gfxbin_file.read(1))[0]
            z1 = _read_string(gfxbin_file, 3)

            if z1 == "src":
                unk2 = struct.unpack("B", gfxbin_file.read(1))[0]
                strlen3 = struct.unpack("B", gfxbin_file.read(1))[0]
                lt.append({"src": _read_string(gfxbin_file)})       # gmdl file
                u = gfxbin_file.tell()
                p = _read_part(gfxbin_file)
                lt.append({"count": p})
                gfxbin_file.seek(u, 0)
            else:
                gfxbin_file.seek(t, 0)
                p = _read_part(gfxbin_file)
                lt.append({"count": p})
                gfxbin_file.seek(t, 0)
    return lt
