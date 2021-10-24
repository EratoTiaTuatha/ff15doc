class MeshData():
	def __init__(self):
		self.mesh_object = 0
		self.faces = 0
		self.bone_ids = 0
		self.weights = 0
		self.VA = 0
		self.NA = 0
		self.UVs0 = 0
		self.UVs1 = 0
		self.UVs2 = 0
		self.UVs3 = 0
        self.file_name = ""
        self.name = ""
        self.group_name = ""
        self.mesh_header = ""
        self.submeshes = []

class SubmeshData():
	def __init__(self):
		self.counter = []
		self.data = {}
		self.bc = 0
		self.stride = 0
		self.offset = 0
		self.item_count = 0
	
	def read(self, file_h, first = True):
		start = 0
		end = 0
		if first == True:
			self.stride     = struct.unpack("<H",file_h.read(2))[0]
			self.item_count = struct.unpack("<H",file_h.read(2))[0] & 0xF
			#self.item_count = rd(file_h)
		else:
			self.stride = struct.unpack("B",file_h.read(1))[0]
			self.offset = rd(file_h)
			self.item_count = struct.unpack("<H",file_h.read(2))[0] & 0xF
		
		for x in range(self.item_count):
			name_size = struct.unpack("B",file_h.read(1))[0] - 0xA0
			name = readString(file_h)
			self.data[name] = {}
			self.data[name]["d_type"] = struct.unpack("B",file_h.read(1))[0]
			if x < self.item_count - 1:
				end = struct.unpack("B",file_h.read(1))[0]
			else:
				end = self.stride
			self.counter.append(end)
			
			if x == 0:
				self.bc = end
			else:
				start = self.counter[x-1]
				self.bc = end - start
			
			self.data[name]["start"] = start
			self.data[name]["end"] = end
			tbc = getByteCount(self.data[name]["d_type"])
			self.data[name]["item_subCount"] = self.bc // tbc
		if first == True:
			file_h.seek(2,1)