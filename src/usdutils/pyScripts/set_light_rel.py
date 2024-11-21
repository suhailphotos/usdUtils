import hou
from pxr import Usd, Sdf

# Get the current Houdini Node and USD Stage
node = hou.pwd()
stage = node.editableStage()

# Define the light and target paths
light_prim_path ='/lights/pointlight1'
target_prim_path = '/sphere1'

# Get the light prim
light_prim = stage.GetPrimAtPath(light_prim_path)


# Ensure prim exists
if not light_prim:
    raise RuntimeError(f'Prim at path {light_prim_path} does not exist')
    
# Get or create the collection:lightLink:includes relationship
light_link_includes_rel = light_prim.GetRelationship('collection:lightLink:includes')
if not light_link_includes_rel:
    light_link_includes_rel = light_prim.CreateRelationship('collection:lightLink:includes')

# Set the relationship to include only the target
light_link_includes_rel.SetTargets([Sdf.Path(target_prim_path)])

# Get or create the collection:lightLink:includeRoot attribute
include_root_attr = light_prim.GetAttribute('collection:lightLink:includeRoot')
if not include_root_attr:
    include_root_attr = light_prim.CreateAttribute('collection:lightLink:includeRoot', Sdf.ValueTypeNames.Bool)

# Set the attribute to False
include_root_attr.Set(False)

# Print the results for verification
print(f"'collection:lightLink:includes' relationship targets: {light_link_includes_rel.GetTargets()}")
print(f"'collection:lightLink:includeRoot' attribute value: {include_root_attr.Get()}")
