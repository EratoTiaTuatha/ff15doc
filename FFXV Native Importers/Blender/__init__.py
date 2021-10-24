import bpy
import time
from XV_Blender.XV_read import *
from XV_Blender.AMDL_Handler import *
from XV_Blender.XV_meshWhipper import *
from XV_Blender.XV_paletteKnife import *
from XV_Blender.XV_boneCruncher import *
from XV_Blender.LordBusiness import microManager


bl_info = {
	"name" : "GFXBIN format",
	"version" : (1, 1, 0),
	"blender" : (2, 80, 0),
    "location": "File > Import-Export",
	"description" : "Import a Luminous Engine model",
	"category" : "Import-Export",
}

def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Luminous Engine (.gfxbin)")

def register():
	bpy.utils.register_class(ImportSomeData)
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
	bpy.utils.unregister_class(ImportSomeData)
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
	register()
	bpy.ops.import_test.some_data('INVOKE_DEFAULT')
