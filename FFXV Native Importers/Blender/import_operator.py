from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from read_bone_ids import importFromGfxbin

class ImportOperator(Operator, ImportHelper):
	"""Imports gfxbin files into Blender"""
	bl_idname = "import_test.some_data"
	bl_label  = "Import gfxbin"
	filename_ext = ".gfxbin"	
	
	def execute(self, context):
		start_time = time.time()
		
        data = importFromGfxbin(self.filepath)
		
		elapsed = time.time() - start_time
		self.report({'INFO'}, "\n\n" + 'Total Time: ' + str(elapsed) + ' seconds' + "\n\n")
		
		return {'FINISHED'}