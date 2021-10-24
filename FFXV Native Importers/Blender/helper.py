import os
from bpy.app import version

def isNewBlender():
    return version >= (2, 80, 0)

def getFilenameWithoutExtension(gfxbinFilepath):
    return gfxbinFilepath.split("\\")[-1].split(".")[0]

def getGpubinFilepath(gfxbinFilepath):
    f_idx = gfxbinFilepath.rfind("\\")
    path_name = os.path.dirname(gfxbinFilepath)
    gpu_name = path_name + "\\" + gfxbinFilepath[f_idx + 1:-11] + "gpubin"

    if os.path.exists(gpu_name):
        return gpu_name
    else:
        return ""

def getAmdlFilepath(gfxbinFilepath):
    path_name = os.path.dirname(gfxbinFilepath)
    p0 = os.path.split(path_name)
    p1 = p0[0]
    f_idx = p1.rfind("\\")
    return p1 + "\\" + p1[f_idx + 1:] + ".amdl"