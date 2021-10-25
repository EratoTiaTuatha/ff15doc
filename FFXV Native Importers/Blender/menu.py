"""
Menu item for the import functionality
Runs the import and logs the time taken
"""

import time

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from state import StateData
from importer import import_mesh_data, import_armature_data
from generate_armature import generate_armature
from generate_mesh import generate_mesh
from version_helper import does_collection_exist


class ImportOperator(Operator, ImportHelper):
    """Imports gfxbin files into Blender"""
    bl_idname = "import_test.some_data"
    bl_label = "Import gfxbin"
    filename_ext = ".gfxbin"

    def execute(self):
        start_time = time.time()
        state = StateData(self.filepath)

        # Import model data to Python Objects
        mesh_data = import_mesh_data(state)
        armature_data = import_armature_data(state)

        # Generate Blender Objects from Python Object Data
        generate_armature(armature_data)

        for mesh in mesh_data:
            generate_mesh(mesh)

            if state.is_new_blender:
                if not does_collection_exist(state.group_name):
                    collect = bpy.data.collections.new(str(state.group_name))
                    bpy.context.scene.collection.children.link(collect)

        # Report time elapsed
        elapsed = time.time() - start_time
        self.report({'INFO'}, "\n\n" + 'Total Time: ' +
                    str(elapsed) + ' seconds' + "\n\n")

        return {'FINISHED'}
