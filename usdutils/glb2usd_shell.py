import hou
from importlib import reload
from usdUtils import glb2usd

reload(glb2usd)

glb_file_path = hou.ui.selectFile(start_directory=hou.getenv('HIP'), title='Select glb file', collapse_sequences=False, file_type=hou.fileType.Gltf)
glbObjAsset = glb2usd.GlbObjAsset(glb_file_path)
glbObjAsset.import_glb()
glb_stage = glb2usd.GlbStageAsset(glbObjAsset)

