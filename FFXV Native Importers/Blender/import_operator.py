from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

class ImportOperator(Operator, ImportHelper):
	"""Imports gfxbin files into Blender"""
	bl_idname = "import_test.some_data"
	bl_label  = "Import gfxbin"
	filename_ext = ".gfxbin"	
	
	def execute(self, context):
		filePath = self.filepath

		#scene = microManager(filePath)
		#scene.Taco_Tuesday()
		
		startTime = time.time()
		
		b0 = paint()
		b0.read(scene.gfx)
		b1 = rd_bones1(scene.gfx)
		
		mesh_count = modelHeader(scene.gfx)
		
		for z in range(mesh_count):
			Mesh = creator(scene.gfx, scene.V_28, scene.filename_wo_ext, scene.groupName)
			Mesh.doTheThing(scene.gfx)
			if Mesh.mesh_header.lod_check == 0:
				Mesh.facePuncher(scene.gpu)
				Mesh.FLDSMDFR(scene.gpu)
				if scene.BIND:
					arm = get_arm(scene.scene_objects, scene.groupName)
					scene.skeleton.index_processor(Mesh.weights, Mesh.bone_ids, b0)
					for x in scene.skeleton.wd:
						for p in range(len(scene.skeleton.wd[x]['weights'])):
							vertexWeight = scene.skeleton.wd[x]['weights'][p]
							boneName = scene.skeleton.wd[x]['boneNames'][p]
							vertGroup = Mesh.meshObject.vertex_groups.get(boneName)
							if not vertGroup:
								vertGroup = Mesh.meshObject.vertex_groups.new(name = boneName)
							vertGroup.add([x], vertexWeight, 'ADD')
					mod = Mesh.meshObject.modifiers.new(type="ARMATURE", name="ArmatureMOD")
					mod.use_vertex_groups = True
					mod.object = arm
		
		
		
		
		elapsed = time.time() - t1
		self.report({'INFO'}, "\n\n" + 'Total Time: ' + str(elapsed) + ' seconds' + "\n\n")
		
		scene.gfx.close()
		if scene.closeGPU:  scene.gpu.close()
		if scene.closeAMDL: scene.amdl.close()
		
		return {'FINISHED'}