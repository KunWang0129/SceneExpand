import bpy
from mathutils import Vector
import trimesh
import os

import trimesh
import json
import os
import numpy as np

def render_custom_view(scene_path, camera_location, target_location, output_file='render.png'):
    def get_whd():
        # Load floor.glb
        floor_path = os.path.join(scene_path, 'output', 'floor.glb')
        floor = trimesh.load(floor_path, force='mesh', process=False)
        bounds = floor.bounds
        d, w = bounds[1, 0], bounds[1, 2]

        # Load back_wall.glb
        back_wall_path = os.path.join(scene_path, 'output', 'back_wall.glb')
        back_wall = trimesh.load(back_wall_path, force='mesh', process=False)
        bounds = back_wall.bounds
        h = bounds[1, 1]
        return d, h, w

    # Clear existing objects (optional)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    bpy.ops.object.select_by_type(type='CAMERA')
    bpy.ops.object.delete()
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()

    output_path = os.path.join(scene_path, 'output')
    # Load all GLB files (except ceiling.glb)
    for file in os.listdir(output_path):
        if file.endswith('.glb') and file != 'ceiling.glb':
            bpy.ops.import_scene.gltf(filepath=os.path.join(output_path, file))

    # Apply smooth shading to all meshes
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()

    w, h, d = get_whd()

    # Create and position the camera
    cam_data = bpy.data.cameras.new('Camera')
    cam_ob = bpy.data.objects.new('Camera', cam_data)
    bpy.context.scene.collection.objects.link(cam_ob)
    cam_ob.location = Vector(camera_location)

    # Function to orient the camera towards the target
    def look_at(obj, point):
        direction = Vector(point) - obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        obj.rotation_euler = rot_quat.to_euler()

    # Use look_at to set camera orientation
    look_at(cam_ob, target_location)
    bpy.context.scene.camera = cam_ob  # Set the camera as active

    # Add an area light
    light_data = bpy.data.lights.new(name='AreaLight', type='AREA')
    light_ob = bpy.data.objects.new(name='AreaLight', object_data=light_data)
    bpy.context.collection.objects.link(light_ob)
    light_ob.location = (w / 2, -d / 2, h)
    light_data.energy = 2000  # Set the energy to increase intensity
    light_data.shape = 'RECTANGLE'
    light_data.size = max(w, d)
    light_data.size_y = max(w, d)

    # Render settings
    render = bpy.context.scene.render
    render.engine = 'BLENDER_EEVEE'
    render.resolution_x = 512
    render.resolution_y = 512
    render.filepath = output_file  # Output path
    render.image_settings.file_format = 'PNG'  # Set output format to PNG
    render.image_settings.color_mode = 'RGBA'  # Use RGBA to support transparency
    render.film_transparent = True  # Enable transparency in the render output

    # Render the scene
    bpy.ops.render.render(write_still=True)

def render_four_corners(scene_path):
    # Get room dimensions
    def get_whd():
        floor_path = os.path.join(scene_path, 'output', 'floor.glb')
        floor = trimesh.load(floor_path, force='mesh', process=False)
        bounds = floor.bounds
        d, w = bounds[1, 0], bounds[1, 2]

        back_wall_path = os.path.join(scene_path, 'output', 'back_wall.glb')
        back_wall = trimesh.load(back_wall_path, force='mesh', process=False)
        bounds = back_wall.bounds
        h = bounds[1, 1]
        return d, h, w

    d, h, w = get_whd()
    
    # Define camera positions (four upper corners) and their target points (opposite corners)
    fac = 1

    corners = [
        ((fac*w, 0, fac*h),  (0, -d, 0)),  # Camera at (0, 0, h) looking at (w, d, 0)
        ((fac*w, -fac*d, fac*h), (0, 0, 0)),  # Camera at (w, 0, h) looking at (0, d, 0)
        ((0, -fac*d, fac*h), (w , 0, 0)),  # Camera at (0, d, h) looking at (w, 0, 0)
        ((0, 0, fac*h),      (w, -d, 0))   # Camera at (w, d, h) looking at (0, 0, 0)
    ]
    # Render each corner view
    for i, (camera_location, target_location) in enumerate(corners):
        output_file = os.path.join(f'tmp/render_corner_{i}.png')
        render_custom_view(scene_path, camera_location, target_location, output_file)
        print(f'Rendered view {i+1} saved to {output_file}')

if __name__ == '__main__':
    scene_path = '/Users/kunalgupta/Documents/sceneprog'
    render_four_corners(scene_path)
