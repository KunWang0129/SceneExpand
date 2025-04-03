def load_pickled_3d_asset(file_path):
    import gzip
    import pickle
    import bpy
    import numpy as np

    # Open the compressed pickled file
    with gzip.open(file_path, 'rb') as f:
        # Load the pickled object
        loaded_object_data = pickle.load(f)

    # Create a new mesh object in Blender
    mesh = bpy.data.meshes.new(name='LoadedMesh')
    obj = bpy.data.objects.new('LoadedObject', mesh)

    # Link the object to the scene
    bpy.context.collection.objects.link(obj)

    # Set the mesh data for the object
    mesh.from_pydata(
        [[v['x'], v['z'], v['y']] for v in loaded_object_data['vertices']], 
        [], 
        np.array(loaded_object_data['triangles']).reshape(-1, 3)
    )

    # Update the mesh
    mesh.update()

    # UV mapping
    uvs = [[uv['x'], uv['y']] for uv in loaded_object_data['uvs']]
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    uv_layer = mesh.uv_layers.active

    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            uv_layer.data[loop_index].uv = uvs[mesh.loops[loop_index].vertex_index]

    # Ensure the mesh updates with new data
    mesh.update()

    # Material and texture setup
    material = bpy.data.materials.new(name="AlbedoMaterial")
    if len(obj.data.materials) == 0:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material

    # Ensure use of nodes
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled_bsdf = nodes.get("Principled BSDF")

    # Load and assign albedo texture
    albedo_path = f"{'/'.join(file_path.split('/')[:-1])}/albedo.jpg"
    print("Albedo Image Path:", albedo_path)
    albedo_img = bpy.data.images.load(albedo_path)
    albedo_node = nodes.new(type='ShaderNodeTexImage')
    albedo_node.image = albedo_img
    material.node_tree.links.new(albedo_node.outputs["Color"], principled_bsdf.inputs["Base Color"])

    # Load and assign normal map
    normal_path = f"{'/'.join(file_path.split('/')[:-1])}/normal.jpg"
    print("Normal Image Path:", normal_path)
    normal_img = bpy.data.images.load(normal_path)
    normal_map_node = nodes.new(type='ShaderNodeNormalMap')
    normal_tex_node = nodes.new(type='ShaderNodeTexImage')
    normal_tex_node.image = normal_img
    normal_tex_node.image.colorspace_settings.name = 'Non-Color'
    material.node_tree.links.new(normal_tex_node.outputs["Color"], normal_map_node.inputs["Color"])
    material.node_tree.links.new(normal_map_node.outputs["Normal"], principled_bsdf.inputs["Normal"])

    print("Material setup complete with textures.")

    return obj

# Replace 'file_path' with the path to your .gzip file
# obj = load_pickled_3d_asset("path_to_your_file.gzip")

def add_obj_to_blender(assetID):
    dataset_path='/Users/kunalgupta/Documents/Holodeck/data/objaverse_holodeck/09_23_combine_scale/processed_2023_09_23_combine_scale/'
    base_path=f'{assetID}/{assetID}.pkl.gz'
    path = dataset_path+base_path
    load_pickled_3d_asset(path)
    

def export_to_glb(assetID, output_path):
    import bpy

    # Construct the name of the object
    object_name = 'LoadedObject'  # This should match the name given to the object when created

    # Find the object by name
    obj = bpy.data.objects.get(object_name)

    if obj is None:
        print(f"No object found with the name {object_name}.")
        return
    
    cube = bpy.data.objects.get("Cube")
    if cube:
        bpy.data.objects.remove(cube, do_unlink=True)
        print("Default cube has been deleted.")
        
    obj.select_set(True)  # Select the target object

    # Set the object as the active object
    bpy.context.view_layer.objects.active = obj

    # Define the export path
    export_file_path = f"{output_path}/{assetID}.glb"

    # Export the object to GLB format
    bpy.ops.export_scene.gltf(
        filepath=export_file_path,
        export_format='GLB',
        use_selection=True
    )
    print(f"Exported {assetID} to {export_file_path}")
    
    return 



if __name__ == "__main__":
    import sys
    # sys.argv[0] is the script name, arguments start from sys.argv[1]
    # Since '--' is used in the command, Blender passes all after '--' to the script starting from sys.argv[0]
    assetID = sys.argv[-1]  # This will get the first argument after '--'
    add_obj_to_blender(assetID)
    import os
    if not os.path.exists('/Users/kunalgupta/Documents/sceneprog/tmp'):
        os.makedirs('/Users/kunalgupta/Documents/sceneprog/tmp')
    export_to_glb(assetID, '/Users/kunalgupta/Documents/sceneprog/tmp')



# import os
# from tools.objaverse import get_objaverse_model
# from tqdm import tqdm

# objaverse_path = '/Users/kunalgupta/Documents/Holodeck/data/objaverse_holodeck/09_23_combine_scale/processed_2023_09_23_combine_scale/'
# output_path = '/Users/kunalgupta/Documents/datasets/objaverse/'

# bad_assets = []
# for model in tqdm(os.listdir(objaverse_path)):
#     if f"{model}.glb" in os.listdir(output_path) or model == '.DS_Store':
#         continue    

#     try:
#         mesh = get_objaverse_model(model)
#         mesh.export(output_path+model+'.glb')
#     except:
#         bad_assets.append(model)
#         continue