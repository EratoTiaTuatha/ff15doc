"""
Data container classes for holding model information
"""


class ArmatureData():
    """
    Holds armature data for use in reconstructing the Blender armature
    """

    def __init__(self):
        self.parent_IDs = []
        self.bones = []


class BoneData():
    """Holds bone data for use in reconstructing the Blender armature"""

    def __init__(self):
        self.id = 0
        self.name = ""
        self.head_position_matrix = 0


class MeshData():
    """Holds all relevant data for a mesh"""

    def __init__(self):
        self.face_data = []
        self.UV_data = {}
        self.VA = []
        self.bone_ids = []
        self.bone_dictionary = {}
        self.weights = []
        self.name = ""
        self.uv_count = 0


class MeshMetadata():
    """
    Holds metadata about meshes to assist with
    processing the gfxbin file
    """

    def __init__(self):
        self.read_count = 0
        self.face_type = 0
        self.faces_offset = 0
        self.byte_size = 0
        self.vertex_count = 0
        self.chunk_count = 0
        self.mesh_data_start = 0
        self.mesh_total_byte_size = 0
        self.lod_check = 0
        self.extras = []


class MeshExtraMetadata():
    """
    Holds extra metadata to assist with
    processing the meshes in the gfxbin file
    """

    def __init__(self):
        self.counter = []
        self.data = {}
        self.bc = 0
        self.stride = 0
        self.offset = 0
        self.item_count = 0
