import os

from bpy.app import version


class StateData():
    """
    Class that holds state data for the add-on
    Internal methods are run on init
    File information should be accessed through class properties
    """

    def __init__(self, gfxbin_file_path):
        self.gfxbin_file_path = gfxbin_file_path
        self.gfxbin_file_size = os.path.getsize(gfxbin_file_path)
        self.gpubin_file_path = self._get_gpubin_file_path(gfxbin_file_path)
        self.amdl_file_path = self._get_amdl_file_path(gfxbin_file_path)

        self.gpubin_file_exists = os.path.exists(self.gpubin_file_path)
        self.amdl_file_exists = os.path.exists(self.amdl_file_path)

        self.group_name = self._get_group_name(gfxbin_file_path)
        self.file_name_no_extension = self._get_file_name_no_extension(
            gfxbin_file_path)

        # Checks whether Blender version is 2.8+
        # as some code needs to be adjusted for compatibility
        self.is_new_blender = self._get_is_new_blender()

    def _get_file_name_no_extension(cls, gfxbin_file_path):
        """
        Internal use only
        Use file_name_no_extension to get the stored value
        """
        return gfxbin_file_path.split("\\")[-1].split(".")[0]

    def _get_gpubin_file_path(cls, gfxbin_file_path):
        """
        Internal use only
        Use gpubin_file_path to get the stored value
        """
        f_idx = gfxbin_file_path.rfind("\\")
        path_name = os.path.dirname(gfxbin_file_path)
        gpu_name = path_name + "\\" + \
            gfxbin_file_path[f_idx + 1:-11] + "gpubin"

        if os.path.exists(gpu_name):
            return gpu_name
        else:
            return ""

    def _get_amdl_file_path(cls, gfxbin_file_path):
        """
        Internal use only
        Use amdl_file_path to get the stored value
        """
        path_name = os.path.dirname(gfxbin_file_path)
        p0 = os.path.split(path_name)
        p1 = p0[0]
        f_idx = p1.rfind("\\")
        return p1 + "\\" + p1[f_idx + 1:] + ".amdl"

    def _get_group_name(cls, gfxbin_file_path):
        """
        Internal use only
        Use group_name to get the stored value
        """
        return os.path.dirname(gfxbin_file_path).split("\\")[-2]

    def _get_is_new_blender(cls):
        """
        Internal use only
        Use is_new_blender to get the stored value
        """
        return version >= (2, 80, 0)
