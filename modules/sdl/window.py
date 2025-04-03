from modules.sdl.object import Object3D
import numpy as np
import trimesh

class Window(Object3D):
    def __init__(self, name, scene):
        super().__init__(name, None, scene)
        
        self.floor_to_ceiling_window_path = 'assets/additional_assets/window_tofloor.obj'
        self.picture_window_path = 'assets/additional_assets/window_picture.obj'
        self.standard_window_path = 'assets/additional_assets/window_dropdown.obj'
        self.curtain_path = 'assets/additional_assets/curtain.glb'
        
        self.header_buffer = 0.5
        self.footer_buffer = 0.5
        self.furniture_clearance = 0.5
        # self.add_curtain = False
        self.window_types = ['floor_to_ceiling', 'picture', 'standard']
        
    def rotate_window(self, wall):
        if wall.name=='back_wall':
            self.set_rotation(0)
        elif wall.name=='left_wall':
            self.set_rotation(90)
        elif wall.name=='front_wall':
            self.set_rotation(180)
        elif wall.name=='right_wall':
            self.set_rotation(270)
        else:
            breakpoint()
            
    def add_window_floor_to_ceiling(self, wall):
        # self.type = 'floor_to_ceiling'
        # self.position = 'full'
        if type(wall)==str:
            wall = self.scene.get_object(wall)
        wall_width, wall_height = wall.get_wh()
        
        def compute_width(width, max_width):
            num = np.round(width/max_width)
            return int((width/num)*100)/100, int(num)

        def assemble_windows(width, height, max_width=1.5):
            width_, num = compute_width(width, max_width)
            mesh = trimesh.load(self.floor_to_ceiling_window_path, process=False)
            vertices = mesh.vertices
            vertices[:,0] *= width_*2
            vertices[:,1] *= height
            mesh = trimesh.Trimesh(vertices=vertices, faces=mesh.faces, process=False)
            meshes = []
            for i in range(num):
                mesh2 = mesh.copy()
                meshes.append(mesh2.apply_translation([width_*i, 0, 0]))
            
            window_mesh = trimesh.util.concatenate(meshes)
            return window_mesh
        
        self.mesh = assemble_windows(wall_width, wall_height, max_width=1.5)
        self.normalize()
        self.scale(width=wall_width, height=wall_height, depth=0.1)
        self.rotate_window(wall)
        pos = wall.compute_window_coordinates('middle')
        self.place_global(x=pos[0], y= wall_height/2, z=pos[2])
        wall.make_space_for_window(self)
        
        self.wall = wall
        self.scene.wall_occ[wall.name]['left'].append(self.name)
        self.scene.wall_occ[wall.name]['right'].append(self.name)
        self.scene.wall_occ[wall.name]['middle'].append(self.name)
        
    def add_window_picture(self, wall):
        # self.type = 'picture'
        # self.position = 'full'
        if type(wall)==str:
            wall = self.scene.get_object(wall)
        wall_width, wall_height = wall.get_wh()
        
        self.mesh = trimesh.load(self.picture_window_path, process=False)
        self.normalize()
        self.scale(width=wall_width-1.5, height=wall_height-1, depth=0.1)
        self.rotate_window(wall)
        pos = wall.compute_window_coordinates('middle')
        self.place_global(x=pos[0], y= wall_height/2, z=pos[2])
        wall.make_space_for_window(self)
        self.wall = wall
        self.scene.wall_occ[wall.name]['left'].append(self.name)
        self.scene.wall_occ[wall.name]['right'].append(self.name)
        self.scene.wall_occ[wall.name]['middle'].append(self.name)
        
    def add_window_standard(self, wall, position):
        if type(wall)==str:
            wall = self.scene.get_object(wall)
        
        wall_width, wall_height = wall.get_wh()
        height = wall_height - self.header_buffer - self.furniture_clearance
        
        self.mesh = trimesh.load(self.standard_window_path, process=False)
        self.normalize()
        self.scale(width=wall.max_window_width(), height=height, depth=0.03)
        self.rotate_window(wall)
        
        pos = wall.compute_window_coordinates(position)
        self.place_global(x=pos[0], y= self.furniture_clearance + self.height/2, z=pos[2])
        wall.make_space_for_window(self)
        
        self.wall = wall
        
        if position=='full':
            self.scene.wall_occ[wall.name]['left'].append(self.name)
            self.scene.wall_occ[wall.name]['right'].append(self.name)
            self.scene.wall_occ[wall.name]['middle'].append(self.name)
        
        else:
            self.scene.wall_occ[wall.name][position].append(self.name)
        
    def add_curtain(self):
        id = np.random.randint(0, 1000)
        curtain = Object3D(f'curtain_{id}', None, self.scene)
        curtain.mesh = trimesh.load(self.curtain_path, process=False, force='mesh')
        curtain.visual = curtain.mesh.visual
        curtain.normalize()
        self.scene.overlap_exceptions.append(curtain)
        wall_width, wall_height = self.wall.get_wh()
        curtain.scale(width=np.min((self.width+0.2, wall_width)) , height=np.min((self.height+0.2,wall_height)), depth=0.3)
        curtain.place_relative(relation='in_front_of', obj=self, dist=0.0)
        curtain.place_global(x=curtain.x, y=self.y, z=curtain.z)
        self.scene.auxilary_objects.append(curtain)
        
        
        