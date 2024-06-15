import hou
import os, time

# This class imports a glb file into Houdini's Obj context using the Glbhierarchy HDA.
# It assumes that Houdini's extraction of textures from the glb file is correct.
# I am aware that there is bug in Houdini. However, this bug has been reported.
# The main focus is on the implementation logic.

class GlbObjAsset:
    def __init__(self, glb_file_path:str, import_bones=False):
        self.glb_file_path = glb_file_path
        self.glb_file = os.path.basename(glb_file_path)
        self.glb_hierarchy = None
        self.import_bones=import_bones
        self.material_info = {} # Dictionary to store material information

    # Renames textures and updates material info. Here I plan on using this as a standard
    # To name all my inported textures with one naming format. 
    # For now my nomenclature is - [asset_name]_[material_name]_[texture_type].ext
    def _rename_tex(self):
        shader = {
                "basecolor": "baseColor",
                "ior":"ior",
                "rough": "roughness",
                "aniso": "anisotropy",
                "anisodir": "anisodir",
                "metallic": "metallic",
                "reflect":"reflectivity",
                "reflecttint":"reflectivityTint",
                "coat":"coat",
                "normal": "normal",
                "displacement": "disp",
                # For sake of completeness, essential textures are focused on for the assignment
                }

        for principledshader in self.gltf_hierarchy.node('materials').children():
            if principledshader.type().name()=='principledshader::2.0':
                material_name = principledshader.name()
                self.material_info[material_name]={"position": principledshader.position()}
                self.material_info[material_name].setdefault("textures", {})
                for parm, suffix in shader.items():
                    if parm=='normal':
                        parm_useTex = principledshader.parm('baseBumpAndNormal_enable')
                        parm_Tex = principledshader.parm('baseNormal_texture')
                    elif parm=='displacement':
                        parm_useTex =principledshader.parm('dispTex_enable')
                        parm_Tex = principledshader.parm('dispTex_texture')
                    else:
                        parm_useTex = principledshader.parm(f'{parm}_useTexture')
                        parm_Tex = principledshader.parm(f'{parm}_texture')
                    if not (parm_useTex and parm_Tex):
                        continue # skip if parameters are not enabled 
                    tex_path = parm_Tex.eval()
                    if not tex_path or not os.path.isfile(tex_path):
                        continue  # skip if texture path is empty or file does not exist
                    file = os.path.basename(tex_path)
                    file_name, file_ext = os.path.splitext(file)
                    file_newName = f'{os.path.splitext(self.glb_file)[0]}_{principledshader.name()}_{suffix}{file_ext}'
                    full_tex_path = '/'.join([os.path.dirname(tex_path), file_newName])
                    os.rename(tex_path, full_tex_path)
                    parm_Tex.set(full_tex_path)
                    self.material_info[material_name]["textures"][suffix] = full_tex_path

   # Imports the glb file and returns the hierarchy node
    def import_glb(self) -> hou.Node:
        self.gltf_hierarchy = hou.node('obj').createNode('gltf_hierarchy', 'glb_sacrificial_node')
        self.gltf_hierarchy.parm('filename').set(self.glb_file_path)
        self.gltf_hierarchy.parm('importnongeo').set(self.import_bones)
        self.gltf_hierarchy.parm('flattenhierarchy').set(1)
        self.gltf_hierarchy.parm('assetfolder').set('$HIP/tex')
        self.gltf_hierarchy.parm('buildscene').pressButton()
        self._rename_tex()
        return self.gltf_hierarchy        

# This class migrates Glb hierarchy object over to Stage context.
# It uses bgeo.sc to keep the assets native to Houdini.

class GlbStageAsset:
    def __init__(self, glb_obj_asset: GlbObjAsset):
        self.glb_obj_asset = glb_obj_asset
        self.material_info = glb_obj_asset.material_info
        self.sop_create_node = self._sop_create()
        self.sop_material_node = self._sop_material()
        self.assign_material_node = self._assign_material_node()
        self.usd_rop_node = self._usd_rop_output()


    # Creates material library node and adds materials based on material info
    def _sop_create(self) -> hou.Node:
        glb_obj = self.glb_obj_asset
        gltf_file_node = glb_obj.gltf_hierarchy.node('geo1').node('gltf1')
        file_cache_node = gltf_file_node.createOutputNode('filecache::2.0', 'sacrificial_file_cache')
        file_cache_node.parm('filemethod').set(1)
        file_cache_node.parm('trange').set(0)
        file_name = os.path.splitext(glb_obj.glb_file)[0]
        file_path = f'$HIP/geo/{file_name}.bgeo.sc'
        file_cache_node.parm('file').set(file_path)
        file_cache_node.parm('execute').pressButton()
        if file_path:
            # Sop create node
            sop_create_node = hou.node('stage').createNode('sopcreate', f'{file_name}_geo')
            sop_create_node.parm('pathprefix').set(f'/{file_name}/$OS')
            
            # File node inside Sop create
            file_sop = hou.node(f'{sop_create_node.path()}/sopnet/create').createNode('file', file_name)
            file_sop.parm('file').set(file_path)
            
            # attribute wrrangle
            attr_wrangle = file_sop.createOutputNode('attribwrangle', 'set_path_attrib')
            attr_wrangle.parm('class').set(1)
            attr_wrangle.parm('snippet').set("s@path = re_find('([^/]+)$',s@shop_materialpath)+'/'+s@name;")
            
            # attribute delete
            attr_delete = attr_wrangle.createOutputNode('attribdelete', f'{file_name}_cleanup')
            attr_delete.parm('vtxdel').set('* ^N ^uv ^tangentu')
            attr_delete.parm('primdel').set('shop_materialpath')
            attr_delete.parm('dtldel').set('*')
            attr_delete.parm('ptdel').set('* ^P')
            
            # Output Sop
            output_sop = attr_delete.createOutputNode('output')
            output_sop.setDisplayFlag(1)
            output_sop.setRenderFlag(1)
            return sop_create_node

    # Creates material library node and adds materials based on material info
    def _sop_material(self):
        file_name = os.path.splitext(self.glb_obj_asset.glb_file)[0]
        material_lib_node = self.sop_create_node.createOutputNode('materiallibrary', f'{file_name}_matLib')
        material_lib_node.parm('matpathprefix').set(f'/{file_name}/{file_name}_matlib/')
        material_info = self.material_info
        for material_name, material_data in material_info.items():
            karma_instance = KarmaMaterial(material_name=material_name, parent=material_lib_node, **material_data)
        return material_lib_node

    def _assign_material_node(self):
        file_name = os.path.splitext(self.glb_obj_asset.glb_file)[0] # I am aware that I have now used it several times (will refactor)
        assign_material_node = self.sop_material_node.createOutputNode('assignmaterial', f'{file_name}_assign_mat')
        material_info = self.material_info
        material_count = len(material_info)
        assign_material_node.parm('nummaterials').set(material_count)
        for index, material_name in enumerate(material_info.keys()):
            geometry_prim_path = f'/{file_name}/{file_name}_geo/{material_name}'
            material_prim_path = f'/{file_name}/{file_name}_matlib/{material_name}'
            assign_material_node.parm(f'primpattern{index+1}').set(geometry_prim_path)
            assign_material_node.parm(f'matspecpath{index+1}').set(material_prim_path)
            assign_material_node.setDisplayFlag(1)
        return assign_material_node

    def _usd_rop_output(self):
        file_name = os.path.splitext(self.glb_obj_asset.glb_file)[0]
        usd_rop_node = self.assign_material_node.createOutputNode('usd_rop', f'{file_name}_usd_rop')
        usd_rop_node.parm('lopoutput').set(f'$HIP/usd/{file_name}.usd')
        usd_rop_node.parm('execute').pressButton()
        return usd_rop_node






# material_info = {
#     "Material1": {
#         "position": hou.Vector2(0, 0),
#         "textures": {
#             "baseColor": "/path/to/baseColor_texture.png",
#             "roughness": "/path/to/roughness_texture.png"
#         }
#     },
#     "Material2": {
#         "position": hou.Vector2(1, 0),
#         "textures": {
#             "baseColor": "/path/to/another_baseColor_texture.png",
#             "normal": "/path/to/normal_texture.png"
#         }
#     }
# }


class KarmaMaterial:
    def __init__(self, material_name: str, position: hou.Vector2, textures: dict, parent: hou.LopNode):
        self.material_name = material_name
        self.position = position
        self.textures = textures
        self.mtlxstandard_surface = None
        self.parent_mat_lib = parent
        self.karma_material_node = self.parent_mat_lib.createNode('subnet', self.material_name)
        self.karma_material_node.setPosition(self.position)
        self.suboutput = hou.node(f'{self.karma_material_node.path()}/suboutput1')
        self.suboutput.setName('Material_Outputs_and_AOVs')
        self.subinput = hou.node(f'{self.karma_material_node.path()}/subinput1')
        self.subinput.setName('inputs')
        self._import_material()
        self.karma_material_node.setMaterialFlag(1)

    def _import_material(self):
        self.mtlxstandard_surface = hou.node(self.karma_material_node.path()).createNode('mtlxstandard_surface')
        self.suboutput.setInput(0, self.mtlxstandard_surface, 0)
        
        # Position mtlxstandard_surface
        suboutput_pos = self.suboutput.position()
        mtlx_std_sur_pos = suboutput_pos - hou.Vector2([2.5,0])
        self.mtlxstandard_surface.setPosition(mtlx_std_sur_pos)

        # Position subinput node
        subinput_pos = self.subinput.position()
        self.subinput.setPosition(subinput_pos - hou.Vector2([2.5, 0]))

        # Texture Maps lookup table to map file name suffix to node input 
        materalX_tex_name_lookup = {
                "baseColor": "base_color",
                "ior":"specular_IOR",
                "roughness": "specular_roughness",
                "anisotropy": "subsurface_anisotropy",
                "anisodir": "anisodir", # need to revist
                "metallic": "metalness",
                "reflectvity":"specular",
                "reflectivityTint":"specular_color",
                "coat":"coat_color",
                "normal": "normal",
                "displacement": "disp", # need to re-visit
                }

        for index, (uv_texture, file_path) in enumerate(self.textures.items()):
            usd_uv_texture = hou.node(self.karma_material_node.path()).createNode('usduvtexture::2.0', uv_texture)
            
            # set file & color space
            usd_uv_texture.parm('file').set(file_path)
            if uv_texture == 'baseColor':
                usd_uv_texture.parm('sourceColorSpace').set('sRGB')
            else:
                usd_uv_texture.parm('sourceColorSpace').set('raw') # This logic needs to be improved to take into account the nuances of each type


            # set position of the node, make connections and add normal node if needed 
            usd_uv_texture_output = usd_uv_texture.outputIndex('rgb')
            mtlsurface_input = self.mtlxstandard_surface.inputIndex(materalX_tex_name_lookup[uv_texture])

            if uv_texture == 'normal':
                
                # Normal creation
                normal_map = hou.node(self.karma_material_node.path()).createNode('mtlxnormalmap', 'normal_map')
                normal_map_pos = subinput_pos - hou.Vector2([0, float(index)*2.5])
                normal_map_output = normal_map.outputIndex('out')
                normal_map_input = normal_map.inputIndex('in')
                normal_map.setPosition(normal_map_pos)
                normal_map.setInput(normal_map_input, usd_uv_texture, usd_uv_texture_output)
                

                usd_uv_texture_pos = normal_map_pos - hou.Vector2([2.5, 0])
                usd_uv_texture.setPosition(usd_uv_texture_pos)
                self.mtlxstandard_surface.setInput(mtlsurface_input, normal_map, normal_map_output)
            elif uv_texture == 'displacement':
                pass # For now skipping displacement. But here as a placeholder for future
            else:
                usd_uv_texture_pos = subinput_pos - hou.Vector2([0, float(index)*2.5])
                usd_uv_texture.setPosition(usd_uv_texture_pos)
                self.mtlxstandard_surface.setInput(mtlsurface_input, usd_uv_texture, usd_uv_texture_output)




