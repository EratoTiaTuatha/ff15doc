import struct
import numpy
import os
from helper import isNewBlender, getGpubinFilepath, getAmdlFilepath
from read import rd, readString, getByteCount
from mesh_data import MeshData, SubmeshData

class GfxbinData():
	def __init__(self):
		self.bone_dictionary = {}
		self.mesh_data = []

def importFromGfxbin(gfxbinFilepath):
	gfxbinFile = open(gfxbinFilepath, "rb")
	gpubinFile = open(getGpubinFilepath(gfxbinFilepath), "rb")
	amdlFilepath = getAmdlFilepath(gfxbinFilepath)
	
	data = GfxbinData()

	# Functions must execute in this order as the cursor will be moved accordingly each time
	data.bone_dictionary = readBoneDictionary(gfxbinFile)
	skipBoneNames(gfxbinFile)
	data.mesh_data = readMeshData(gfxbinFile, gpubinFile, amdlFilepath)

	# TODO: Rewrite this to close files correctly
	#scene.gfx.close()
	#if scene.closeGPU:
	#	scene.gpu.close()
	#if scene.closeAMDL:
	#	scene.amdl.close()

def readBoneDictionary(file):
	# Key is the Bone ID
	# Value is the Bone Name
	bone_dictionary = {}

	bone_count = struct.unpack("B", file.read(1))[0] & 0xF
	seek_length = bone_count * 9

	# Skips over metadata that precedes the Bone IDs (seems to just be a list of Bone Names)
	file.seek(seek_length, 1)
	
	# Skip the next 6 floats from this point as they are not relevant here
	for i in range(6):
		rd(file)

	# Skip the next 5 bytes as they are also in the way
	file.seek(5, 1)

	bone_name_count = rd(file)

	# Read the bone dictionary
	for i in range(bone_name_count):
		bone_name_size = struct.unpack("B", file.read(1))[0] - 0xA0
		bone_name = readString(file)
		bone_id = rd(file)
		if bone_id > 65535:
			bone_id >>= 16
			if bone_id == 65535:
				bone_dictionary[i] = bone_name	# If the bone ID exceeds the size limit, we just use the index of the iterator
			else:
				bone_dictionary[bone_id] = bone_name
		else:
			bone_dictionary[i] = bone_name	# Not sure why we have to use the index of the iterator in this case

	return bone_dictionary

def skipBoneNames(file):
	bone_name_count = rd(file)
	for i in range(bone_name_count):
		for j in range(12):
			rd(file)
		name_size = struct.unpack("B", file.read(1))[0] - 0xA0
		bone_name = readString(file)

def readMeshData(gfxbinFile, gpubinFile, amdlFilepath):
	# Get Mesh Count
	gfxbinFile.seek(11, 1)		# Skip 11 unknown bytes to get to the part we need
	readString(gfxbinFile)      # Skip the base name (usually Parts_Base)
	rd(gfxbinFile)				# Skip what may be a Count?

	struct.unpack("B", gfxbinFile.read(1))[0] - 0xA0	# Skip Name Size
	readString(gfxbinFile)								# Skip Cluster Name
	mesh_count = rd(gfxbinFile)

	# Get data for each mesh
	for i in range(mesh_count):
		mesh_data = MeshData()
		# TODO: Refactor this so it can be uncommented
		# TODO: Remove any properties that aren't needed
		#mesh_data.file_name = f_name
		#mesh_data.name = f_name + "__" + rd_meshBegin(file_gfx)
		#mesh_data.group_name = grp	
		#mesh_data.mesh_header = header(file_gfx)
		mesh_data.submeshes.append(getSubmeshData(gfxbinFile, True))
		mesh_data.submeshes.append(getSubmeshData(gfxbinFile, False))
		#mesh_data.mesh_header.readExtra(file_gfx)

		if mesh_data.mesh_header.lod_check == 0:
			mesh_data.faces = getFacesWithCorrectedNormals(gpubinFile, mesh_data)
			wtf(gpubinFile, mesh_data)

			if os.path.exists(amdlFilepath):
				arm = get_arm(scene.scene_objects, scene.groupName)
				scene.skeleton.index_processor(Mesh.weights, Mesh.bone_ids, data.bone_dictionary)
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

def getSubmeshData(file, first):
	start = 0
	end = 0
	submesh = SubmeshData()

	if first == True:
		submesh.stride     = struct.unpack("<H", file.read(2))[0]
		submesh.item_count = struct.unpack("<H", file.read(2))[0] & 0xF
	else:
		submesh.stride = struct.unpack("B", file.read(1))[0]
		submesh.offset = rd(file)
		submesh.item_count = struct.unpack("<H", file.read(2))[0] & 0xF
	
	for x in range(submesh.item_count):
		name_size = struct.unpack("B", file.read(1))[0] - 0xA0
		name = readString(file)
		submesh.data[name] = {}
		submesh.data[name]["d_type"] = struct.unpack("B", file.read(1))[0]
		if x < submesh.item_count - 1:
			end = struct.unpack("B", file.read(1))[0]
		else:
			end = submesh.stride
		submesh.counter.append(end)
		
		if x == 0:
			submesh.bc = end
		else:
			start = submesh.counter[x-1]
			submesh.bc = end - start
		
		submesh.data[name]["start"] = start
		submesh.data[name]["end"] = end
		tbc = getByteCount(submesh.data[name]["d_type"])
		submesh.data[name]["item_subCount"] = submesh.bc // tbc

	if first == True:
		file.seek(2, 1)

def getFacesWithCorrectedNormals(gpubinFile, mesh_data):
	gpubinFile.seek(mesh_data.mesh_header.faces_offset, 0)
		
	cn = 0
	if mesh_data.mesh_header.face_type == 1:
		cn = mesh_data.mesh_header.byteSize // 4
		fi = numpy.fromfile(gpubinFile, dtype = '<L', count = cn)
	else: # 0
		cn = mesh_data.mesh_header.byteSize // 2
		fi = numpy.fromfile(gpubinFile, dtype = '<H', count = cn)
	
	fi_0 = fi.view().reshape((cn // 3, 3))
	
	# change winding order so normals are correct (0 1 2 --> 2 1 0)
	if isNewBlender():
		fi_1 = numpy.flip(fi_0,1)
	else:
		fi_1 = numpy.fliplr(fi_0)
	fi_1[:, [0, 1]] = fi_1[:, [1, 0]]  # 2 1 0 --> 1 2 0
	fi_2 = fi_1.ravel()
	
	return tuple(fi_1)

def wtf(gpubinFile, mesh_data):
	gpubinFile.seek(mesh_data.mesh_header.mesh_dataStart,0)
	mesh_data.byte_count = mesh_data.mesh_header.vertexCount * mesh_data.m0.stride
	ti_0 = np.fromfile(gpubinFile, dtype = 'B', count = mesh_data.byte_count).reshape((mesh_data.mesh_header.vertexCount, mesh_data.m0.stride))
	
	for x in cat_list: cat(mesh_data.m0.data, x)
	for p in mesh_data.m0.data:
		g = mesh_data.m0.data[p]
		chunc = data_paver(g["start"], g["end"], mesh_data.mesh_header.vertexCount, g["item_subCount"], g["d_type"], ti_0)
		if p == "POSITION0":
			chunc[:,[1,2]] = chunc[:,[2,1]]
			mesh_data.VA = chunc.tolist()
		elif p == "BLENDINDICES":
			mesh_data.bone_ids = chunc.tolist()
		elif p == "BLENDWEIGHTS":
			mesh_data.weights = chunc.tolist()
	
	chunk2_start = mesh_data.mesh_header.mesh_dataStart + mesh_data.m1.offset
	byteCount2 = mesh_data.mesh_header.vertexCount * mesh_data.m1.stride
	gpubinFile.seek(chunk2_start,0)
	ti_1 = np.fromfile(gpubinFile, dtype = 'B', count = byteCount2).reshape((mesh_data.mesh_header.vertexCount, mesh_data.m1.stride))
	
	uv_count = 0
	for j in mesh_data.m1.data:
		z = mesh_data.m1.data[j]
		chunc = data_paver(z["start"], z["end"], mesh_data.mesh_header.vertexCount, z["item_subCount"], z["d_type"], ti_1)
		if j == "NORMAL0":
			Normal_Array0 = chunc[:,0:3].reshape((mesh_data.mesh_header.vertexCount, 3))
			Normal_Array0[:,[1,2]] = Normal_Array0[:,[2,1]]
			Normal_Array = Normal_Array0.tolist()
		elif j == "TANGENT0":
			pass
		elif j == "TEXCOORD0":
			uv_count += 1
			chunc[:,1:2] *= -1
			chunc[:,1:2] += 1
			uvData0 = chunc.tolist()
			mesh_data.UVs0 = [mu.Vector(x) for x in uvData0]
		elif j == "TEXCOORD1":
			uv_count += 1
			chunc[:,1:2] *= -1
			chunc[:,1:2] += 1
			uvData1 = chunc.tolist()
			mesh_data.UVs1 = [mu.Vector(x) for x in uvData1]
		elif j == "TEXCOORD2":
			uv_count += 1
			chunc[:,1:2] *= -1
			chunc[:,1:2] += 1
			uvData2 = chunc.tolist()
			mesh_data.UVs2 = [mu.Vector(x) for x in uvData2]
		elif j == "TEXCOORD3":
			uv_count += 1
			chunc[:,1:2] *= -1
			chunc[:,1:2] += 1
			uvData3 = chunc.tolist()
			mesh_data.UVs3 = [mu.Vector(x) for x in uvData3]
		elif j == "NORMAL4FACTORS0":
			pass
		elif j == "NORMAL2FACTORS0":
			pass
	
	mesh = bpy.data.meshes.new(mesh_data.name)
	mesh.from_pydata(mesh_data.VA, [], mesh_data.faces)
	if mesh_data.V_28:
		for g in range(uv_count): mesh.uv_layers.new(name = mesh_data.name + "_TXUV" + "_0" + str(g))
	else:
		for g in range(uv_count): mesh.uv_textures.new(name = mesh_data.name + "_TXUV" + "_0" + str(g))
	
	
	#https://blenderartists.org/t/importing-uv-coordinates/595872/5
	UVS = 0
	for g in range(uv_count):
		if   g == 0: UVS = mesh_data.UVs0
		elif g == 1: UVS = mesh_data.UVs1
		elif g == 2: UVS = mesh_data.UVs2
		elif g == 3: UVS = mesh_data.UVs3
		vi_uv = {i: uv for i, uv in enumerate(UVS)}
		per_loop_list = [0.0] * len(mesh.loops)
		for loop in mesh.loops:
			per_loop_list[loop.index] = vi_uv.get(loop.vertex_index)
		per_loop_list = [uv for pair in per_loop_list for uv in pair]
		mesh.uv_layers[g].data.foreach_set("uv", per_loop_list)
	
	
	mesh.validate()
	mesh.update()
	
	mesh_data.meshObject = bpy.data.objects.new(mesh_data.name, mesh)
	
	
	scn_objs = get_objects(mesh_data.V_28)
	if mesh_data.V_28:
		if collectionExists(mesh_data.file_name):
			bpy.data.collections[mesh_data.file_name].objects.link(mesh_data.meshObject)
		else:
			newCol = bpy.data.collections.new(mesh_data.file_name)
			if collectionExists(mesh_data.group_name):
				bpy.data.collections[mesh_data.group_name].children.link(newCol)
			else:
				bpy.context.scene.collection.children.link(newCol)
			bpy.data.collections[mesh_data.file_name].objects.link(mesh_data.meshObject)
	else:
		bpy.context.scene.objects.link(mesh_data.meshObject)
		for x in scn_objs:
			if x.type == 'ARMATURE' and mesh_data.group_name in x.name:
				mesh_data.meshObject.parent = x
				break
		mesh_data.meshObject.select = True
	
	mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
	
	# Changed the commented line out for the fixed script as per sai's instructions
	#bpy.context.scene.update()
	layer = bpy.context.view_layer
	layer.update()