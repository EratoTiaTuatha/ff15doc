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
    aByte = file.read(1)
    s = aByte
    c = 0
    while aByte and ord(aByte) != 0 and c < number_of_bytes:
        aByte = file.read(1)
        s += aByte
        c += 1
    return s[:-1].decode('ascii', errors='ignore')


def _align(ptr, alignment):
    """
    Internal use only
    Not really sure what this voodoo magic does
    """
    alignment -= 1
    return (ptr + alignment) & ~(alignment)


def _read_part(file):
    """
    Internal use only
    Unsure exactly what this does
    Seems to detect patterns and read specific number of bytes accordingly
    Returns the read bytes
    """
    val = 0
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


def _read_byte_count(type):
    """
    Internal use only
    Appears to take a type (not sure what kind of type)
    And determine the byte count based on that type
    Returns the byte count
    """
    byte_count = 0
    if type == 6:
        byte_count = 2
    elif type == 8:
        byte_count = 2
    elif type == 12:
        byte_count = 1
    elif type == 13:
        byte_count = 1
    elif type == 14:
        byte_count = 1
    elif type == 16:
        byte_count = 4
    elif type == 26:
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
