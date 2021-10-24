from XV_Blender.XV_boneCruncher import *
from XV_Blender.XV_read import *
import numpy as np
import string
import struct
import bmesh
import bpy
import os

from bpy_extras.io_utils import unpack_list, unpack_face_list




cat_list = ["BLENDWEIGHT", "BLENDINDICES"]

def cat(d, chk):
	c = {}
	g = sum(chk in p for p in d)
	id = g-1
	first_match = chk + "0"
	last_match = chk + str(id)
	new_sub = d[first_match]["item_subCount"] * g
	new_end = d[last_match]["end"]
	if chk[-1]!= "S":
		new_key = chk + "S"
	else:
		new_key = chk
	a = d[first_match].copy()
	if g > 0:
		for x in d.keys():
			if chk in x:
				c[x] = d[x]
		for i in c.keys():
			del d[i]
		d[new_key] = a
		d[new_key]["item_subCount"] = new_sub
		d[new_key]["end"] = new_end




class header():
	def __init__(self, file_h):
		self.f_readCount  = rd(file_h)
		self.face_type    = struct.unpack("B",file_h.read(1))[0]
		self.faces_offset = rd(file_h)
		self.byteSize     = rd(file_h)
		self.vertexCount  = rd(file_h)
		self.chunk_count  = struct.unpack("B",file_h.read(1))[0] & 0xF
		#self.chunk_count = rd(file_h)
		file_h.seek(2,1)
	def readExtra(self, file_h):
		self.mesh_dataStart = rd(file_h)
		self.mesh_totalByteSize = rd(file_h)
		self.lod_check = rd_meshEnd(file_h)




class m():
	def __init__(self, file_h):
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