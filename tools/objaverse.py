def get_objaverse_model(obj):
    import os
    import subprocess
    import trimesh
    # Path to the Blender executable
    # Update this path according to your Blender installation
    blender_executable_path = '/Applications/Blender.app/Contents/MacOS/Blender'

    # Path to your custom script that you want Blender to run
    script_path = '/Users/kunalgupta/Documents/sceneprog/tools/export_to_blender.py'

    # Constructing the command to run Blender, execute the script, and pass the assetID
    command = [
        blender_executable_path,
        '--python', script_path,  # The path to the script Blender will run
        '--background',  # Run Blender in background mode
        '--',  # This tells Blender to stop processing arguments further; the rest are passed to the script
        obj
    ]
    # Execute the command
    try:
        subprocess.run(command, timeout=10)
    except subprocess.TimeoutExpired:
        print("Blender process exceeded the time limit and was terminated.")
    
    mesh = trimesh.load(f'/Users/kunalgupta/Documents/sceneprog/tmp/{obj}.glb', force='mesh', process=False)
    os.system(f'rm /Users/kunalgupta/Documents/sceneprog/tmp/{obj}.glb')
    return mesh

def get_objaverse_local(obj):
    import trimesh
    path = f'/Users/kunalgupta/Documents/datasets/objaverse/{obj}.glb'
    mesh = trimesh.load(path, force='mesh', process=False)
    return mesh
