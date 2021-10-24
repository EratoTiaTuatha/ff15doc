from bpy.app import version

def isNewBlender():
    return version >= (2, 80, 0)