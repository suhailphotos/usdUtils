import pygltflib

def extract_texture(gltf_file):
    gltf = pygltflib.GLTF2().load(gltf_file)

    print(gltf.textures)
