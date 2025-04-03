from modules.sdl.object import Object3D
import numpy as np
import trimesh
from tools.llm import LLM

class Door(Object3D):
    def __init__(self, name, scene):
        super().__init__(name, None, scene)
        self.door_path = 'assets/additional_assets/door.glb'
    
    def add(self, wall, position):
        if type(wall)==str:
            wall = self.scene.get_object(wall)
        
        # height_llm = LLM(system_desc="Given the height of the walls, what's a reasonable height for a door? Respond in meters following the JSON format like height:2.0", response_format='json')
        # height = float(height_llm.run(self.scene.MAX_HEIGHT)['height'])
        height = np.clip(self.scene.MAX_HEIGHT-1.0, 2.0, 3.5)
        self.mesh = trimesh.load(self.door_path, process=False, force='mesh')
        self.visual = self.mesh.visual
        self.normalize()
        self.scale(width=wall.max_window_width(), height=height, depth=0.03)
        
        self.place_on_wall(wall, horizontal_position=position, vertical_position='bottom')
        self.mesh.visual = self.visual