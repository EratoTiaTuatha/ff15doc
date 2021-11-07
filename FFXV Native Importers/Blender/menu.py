"""
Menu item for the import functionality
Runs the import and logs the time taken
"""

import time

from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from mathutils import Matrix, Vector

from .state import StateData
from .importer import import_mesh_data, import_armature_data
from .generate_armature import generate_armature
from .generate_mesh import generate_mesh


class ImportOperator(Operator, ImportHelper):
    """Imports gfxbin files into Blender"""
    bl_idname = "import_test.some_data"
    bl_label = "Import gfxbin"
    filename_ext = ".gfxbin"

    def execute(self, context):
        start_time = time.time()
        state = StateData(self.filepath)

        # Import model data to Python Objects
        mesh_data = import_mesh_data(state)
        armature_data = import_armature_data(state)

        print(armature_data)

        # Generate Blender Objects from Python Object Data
        generate_armature(state, armature_data)

        for mesh in mesh_data:
            generate_mesh(state, mesh)

        # Mirror the objects so it isn't back to front
        mirror = Matrix.Scale(-1, 4, Vector([0, 1, 0])).to_4x4()
        for obj in state.get_collection().objects:
            obj.matrix_world *= mirror

        # Report time elapsed
        elapsed = time.time() - start_time
        self.report({'INFO'}, "\n\n" + 'Total Time: ' +
                    str(elapsed) + ' seconds' + "\n\n")

        return {'FINISHED'}
