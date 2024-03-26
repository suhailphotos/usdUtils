import hou
import os, time

# This class takes the glb file and imports into Houdini's Obj context 
# using the HDA provided by houdini called Glbhierarchy. Although 
# some of the extracted textures are inaccuate by 'Glbhierarchy', 
# it seemed out of the scope of this course. My assumption here is whatever
# houdini has extracted is correct (I have already repored a bug with SideFx)
# And what you looking for is mainly the implemenatation logic.

class GlbObjAsset:
    def __init__(self, glb_file_path:str, import_bones=False):
        self.glb_file_path = glb_file_path
        self.glb_file = os.path.basename(glb_file_path)
        self.glb_hierarchy = None
        self.import_bones=import_bones
        self.shader_node_pos = {}
        self.full_tex_path = None

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
                # For sake of completness I can of course list all the textures 
                # But here i focused on essentials for the assigment
                }

        for principledshader in self.gltf_hierarchy.node('materials').children():
            if principledshader.type().name()=='principledshader::2.0':
                self.shader_node_pos[principledshader.name()]=principledshader.position()
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
                    self.full_tex_path = '/'.join([os.path.dirname(tex_path), file_newName])
                    os.rename(tex_path, self.full_tex_path)
                    parm_Tex.set(self.full_tex_path)


    def import_glb(self) -> hou.Node:
        self.gltf_hierarchy = hou.node('obj').createNode('gltf_hierarchy', 'glb_sacrificial_node')
        self.gltf_hierarchy.parm('filename').set(self.glb_file_path)
        self.gltf_hierarchy.parm('importnongeo').set(self.import_bones)
        self.gltf_hierarchy.parm('flattenhierarchy').set(1)
        self.gltf_hierarchy.parm('assetfolder').set('$HIP/tex')
        self.gltf_hierarchy.parm('buildscene').pressButton()
        self._rename_tex()
        return self.gltf_hierarchy        


# This class takes Glb hierarchy object And migrates it over to Stage context. 
# I have decided to use bgeo.sc in order to keep the assest native to Houdini

class GlbStageAsset:
    def __init__(self, glb_obj_asset: GlbObjAsset):
        self.glb_obj_asset = glb_obj_asset
        self.sop_create_node = self._sop_create()
        self.sop_material_node = self._sop_material()

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
            sop_create_node = hou.node('stage').createNode('sopcreate', f'{file_name}_geo')
            sop_create_node.parm('pathprefix').set(f'/{file_name}/$OS')
            file_sop = hou.node(f'{sop_create_node.path()}/sopnet/create').createNode('file', file_name)
            file_sop.parm('file').set(file_path)
            attr_wrangle = file_sop.createOutputNode('attribwrangle', 'set_path_attrib')
            attr_wrangle.parm('class').set(1)
            attr_wrangle.parm('snippet').set("s@path = re_find('([^/]+)$',s@shop_materialpath)+'/'+s@name;")
            attr_delete = attr_wrangle.createOutputNode('attribdelete', f'{file_name}_cleanup')
            attr_delete.parm('vtxdel').set('* ^N ^uv ^tangentu')
            attr_delete.parm('primdel').set('shop_materialpath')
            attr_delete.parm('dtldel').set('*')
            attr_delete.parm('ptdel').set('* ^P')
            output_sop = attr_delete.createOutputNode('output')
            output_sop.setDisplayFlag(1)
            output_sop.setRenderFlag(1)
            return sop_create_node

    def _sop_material(self):
        file_name = os.path.splitext(self.glb_obj_asset.glb_file)[0]
        material_lib_node = self.sop_create_node.createOutputNode('materiallibrary', f'{file_name}_matLib')
        material_lib_node.parm('matpathprefix').set(f'/{file_name}/{file_name}_matlib/')
