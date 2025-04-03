import json
from modules.sdl.wall import *
from modules.sdl.object import Object3D
from modules.sdl.window import Window
from modules.sdl.door import Door
from modules.utils.retriever import Object3DRetriever
from tools.llm import LLM
import os
import numpy as np
import matplotlib.pyplot as plt

class SceneGraph:
    def __init__(self, name, depth=0):
        self.name = name
        self.depth = depth
        self.children = []
        self.parent = None
        
    def get_object(self, name): 
        all_children, names = self.get_all_children()
        if name in names:
            return all_children[names.index(name)]
        else:
            return None
        
    def add_child(self, n):
        n = SceneGraph(n, self.depth+1)
        n.parent = self.name
        self.children.append(n)
        return n
    
    def remove_child(self, n):
        for child in self.children:
            if child.name == n:
                self.children.remove(child)
                break        
    
    def is_part_of_same_subtree(self, n1, n2):
        # Get the nodes for the given names
        node1 = self.get_object(n1)
        node2 = self.get_object(n2)
        
        if not node1 or not node2:
            return False  # Return False if either node is not found
        
        # Get the ancestors of both nodes
        ancestors1 = self.get_ancestors(node1)
        ancestors2 = self.get_ancestors(node2)
        
        # Check if there is any common ancestor
        return bool(set(ancestors1) & set(ancestors2))
    
    def get_ancestors(self, node):
        ancestors = []
        while node.parent or node.parent != 'root':
            ancestors.append(node.parent.name)
            node = node.parent
        return ancestors
            
    def get_all_children(self):
        items = []
        for child in self.children:
            items.append(child)
            if len(child.children) > 0:
                items.extend(child.get_all_children()[0])
        
        return items, [child.name for child in items]
    
class SceneHelper:
    def __init__(self, scene):
        self.scene = scene
        self.sg = scene.compute_sg()
        self.s = 100
        self.MAX_WIDTH = int(scene.MAX_WIDTH*self.s)
        self.MAX_DEPTH = int(scene.MAX_DEPTH*self.s)
        
    def get_obj_min_max_sg(self, obj):
        sg_obj = self.sg.get_object(obj.name)
        _, children = sg_obj.get_all_children()
        
        xmins=[]
        xmaxs=[]
        zmins=[]
        zmaxs=[]
        
        for child in [obj.name, *children]:
            xmin,_,zmin,xmax,_,zmax = self.scene.get_object(child).get_min_max()
            
            xmins.append(xmin)
            xmaxs.append(xmax)
            zmins.append(zmin)
            zmaxs.append(zmax)
        
        xmin = round(min(xmins)*self.s)
        xmax = round(max(xmaxs)*self.s)
        zmin = round(min(zmins)*self.s)
        zmax = round(max(zmaxs)*self.s)
        
        xmin = np.clip(xmin, 0, self.MAX_WIDTH)
        xmax = np.clip(xmax, 0, self.MAX_WIDTH)
        zmin = np.clip(zmin, 0, self.MAX_DEPTH)
        zmax = np.clip(zmax, 0, self.MAX_DEPTH)
        
        return xmin, xmax, zmin, zmax
        
    def add_object_to_scene(self, scene_space, obj):

        xmin,_,zmin,xmax,_,zmax = obj.get_min_max()
        xmin = round(xmin*self.s)
        xmax = round(xmax*self.s)
        zmin = round(zmin*self.s)
        zmax = round(zmax*self.s)
        
        xmin = np.clip(xmin, 0, self.MAX_WIDTH)
        xmax = np.clip(xmax, 0, self.MAX_WIDTH)
        zmin = np.clip(zmin, 0, self.MAX_DEPTH)
        zmax = np.clip(zmax, 0, self.MAX_DEPTH)
        
        scene_space[zmin:zmax, xmin:xmax] = 1
    
    def scene_to_layout2D(self, scene):
        scene_space = np.zeros((self.MAX_DEPTH, self.MAX_WIDTH))
        
        if isinstance(scene, list):
            for obj in scene:
                self.add_object_to_scene(scene_space, obj)
        else:
            for obj in scene.objects:
                self.add_object_to_scene(scene_space, obj)
        return scene_space
    
    
    def compute_free_space_around_obj_along_sg(self, obj, dir):
        assert dir in ['+x','-x','+z','-z']
        
        scene_minus_obj = self.scene.objects.copy()
        scene_minus_obj.remove(obj)
        for o in self.scene.overlap_exceptions:
            try:
                scene_minus_obj.remove(o)
            except:
                continue
        
        try:
            _, children = self.sg.get_object(obj.name).get_all_children()
        except:
            breakpoint()
        for child in children:
            try:
                scene_minus_obj.remove(self.scene.get_object(child))
            except:
                continue
                            
        for o in self.scene.objects:
            if not o.on_floor:
                try:
                    scene_minus_obj.remove(o)
                except:
                    continue
                
            if o.placed_on_wall:
                try:
                    scene_minus_obj.remove(o)
                except:
                    continue
        
        scene_space = self.scene_to_layout2D(scene_minus_obj)
        xmin, xmax, zmin, zmax = self.get_obj_min_max_sg(obj)
        
        if xmin == self.MAX_WIDTH or zmin == self.MAX_DEPTH or xmax == 0 or zmax == 0:
            return max(self.MAX_WIDTH, self.MAX_DEPTH)
        
        if dir == '+x':
            tmp = scene_space[zmin:zmax, xmax:].copy()
            if xmax == self.MAX_WIDTH:
                return 0
            tmp[:,-1] = 1
            min_dist = np.argmax(tmp, axis=1)
            min_dist = np.min(min_dist)
            
        elif dir == '-x':
            tmp = scene_space[zmin:zmax, :xmin].copy()
            if xmin== 0:
                return 0
            tmp[:,0] = 1
            min_dist = np.argmax(np.flip(tmp, axis=1), axis=1)
            min_dist = np.min(min_dist)
            
        elif dir == '+z':
            tmp = scene_space[zmax:, xmin:xmax].copy()
            if zmax== self.MAX_DEPTH:
                return 0
            tmp[-1,:] = 1
            min_dist = np.argmax(tmp, axis=0)
            min_dist = np.min(min_dist)
            
        elif dir == '-z':
            tmp = scene_space[:zmin, xmin:xmax].copy()
            if zmin == 0:
                return 0
            tmp[0,:] = 1
            min_dist = np.argmax(np.flip(tmp, axis=0), axis=0)
            min_dist = np.min(min_dist)
            
        return min_dist/self.s
    
    def compute_free_space_around_obj(self, obj):
        min_dist_posx = self.compute_free_space_around_obj_along_sg(obj, '+x')
        min_dist_negx = self.compute_free_space_around_obj_along_sg(obj, '-x')
        min_dist_posz = self.compute_free_space_around_obj_along_sg(obj, '+z')
        min_dist_negz = self.compute_free_space_around_obj_along_sg(obj, '-z')
        return min_dist_posx, min_dist_negx, min_dist_posz, min_dist_negz
    
class Scene:
    def __init__(self, dims = (5,5,3)):
        self.MAX_WIDTH = dims[0]
        self.MAX_DEPTH = dims[1]
        self.MAX_HEIGHT = dims[2]

        assert self.MAX_WIDTH >= 5 and self.MAX_DEPTH >= 5 and self.MAX_HEIGHT >= 3, "Minimum dimensions for the room should be 5m x 5m x 3m"

        self.objects = []
        self.auxilary_objects = []
        self.overlap_exceptions = []
        self.cache={}
        self.object_hash = {}
        self.retriever = Object3DRetriever()
        
        if os.path.exists('tmp/object_hash.json'):
            with open('tmp/object_hash.json', 'r') as f:
                self.object_hash = json.load(f)
        
    def add_walls(self, wall_color: str, floor_texture: str, ceiling_texture: str):
        
        self.back_wall = BackWall(self, color=wall_color)
        self.left_wall = LeftWall(self, color=wall_color)
        self.right_wall = RightWall(self, color=wall_color)
        self.front_wall = FrontWall(self, color=wall_color)
        self.floor = Floor(self, texture=floor_texture)
        self.ceiling = Ceiling(self, texture=ceiling_texture)
        
        self.walls = [self.back_wall, self.left_wall, self.right_wall, self.front_wall, self.floor, self.ceiling]
        self.wall_occ = {
            'back_wall': {'left':[], 'right':[], 'middle':[]},
            'left_wall': {'left':[], 'right':[], 'middle':[]},
            'right_wall': {'left':[], 'right':[], 'middle':[]},
            'front_wall': {'left':[], 'right':[], 'middle':[]}
            }
        
    def place_window(self, name, wall, type, position='middle', place_curtain=True):
        window = Window(name, scene=self)
        if type == 'floor_to_ceiling':
            window.add_window_floor_to_ceiling(wall)
            assert position == 'full', "Position must be full for floor to ceiling windows."
        elif type == 'picture':
            window.add_window_picture(wall)
            assert position == 'full', "Position must be full for picture windows."
        elif type == 'standard':
            window.add_window_standard(wall, position=position)
        else:
            raise ValueError('Invalid window type. Must be one of floor_to_ceiling, picture or standard.')
        
        if place_curtain:
            window.add_curtain()
        setattr(self, name, window)
        self.auxilary_objects.append(window)
        self.overlap_exceptions.append(window)
    
    def place_door(self, name, wall, position):
        door = Door(name, scene=self)
        door.add(wall, position)
        setattr(self, name, door)
        self.auxilary_objects.append(door)
        self.overlap_exceptions.append(door)
        
    def add(self, name: str, desc=None, dims=None):
        '''
        Add object to the scene. This is used for either initializing a new object based on caption or image or loading an existing object from disk.
        '''
        if desc in self.cache:
            obj = self.cache[desc].copy(name)
            setattr(self, name, obj)
            self.objects.append(getattr(self, name))
        else:
            obj = Object3D(name, desc=desc, scene=self)
            obj.init()
            obj.set_scale(dims)
            setattr(self, name, obj)
            self.objects.append(getattr(self, name))
            self.cache[desc] = getattr(self, name)
        
    def get_object(self, name: str):
        '''
        Returns the object with the given name.
        '''
        try:
            return getattr(self, name)
        except:
            all_object_names = [obj.name for obj in self.objects]
            if name in all_object_names:
                return self.objects[all_object_names.index(name)]
            else:
                return None
        
        

    def export(self, name='output'):
        
        if os.path.exists(name):
            os.system(f'rm -rf {name}')
        os.makedirs(name, exist_ok=True)
            
        if os.path.exists(f'{name}.zip'):
            os.remove(f'{name}.zip')
            
        for obj in self.walls:
            obj.build().export(f'{name}/'+obj.name+'.glb')
            
        for obj in self.auxilary_objects:
            obj.export(f'{name}/'+obj.name+'.glb')
        
        for obj in self.objects:
            try:
                obj.export(f'{name}/'+obj.name+'.glb')
            except:
                breakpoint()
            
    def print(self):
        print('Objects in the scene:')
        for obj in self.objects:
            print(obj.name)
            
    def save(self, save_path='cache/scene.pkl'):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        not_placed = []
        for obj in self.objects:
            if not obj.placed:
                not_placed.append(obj.name)
        
        if len(not_placed) > 0:
            raise Exception(f'Objects {not_placed} have not been placed in the scene. Revise the scene program so that all objects are placed in the scene.')

        import pickle
        ## save the scene graph
        sg = self.compute_sg()
        dims = self.compute_dims()
        weights = self.compute_weights()
        placements = self.compute_placements()
        data = {'sg': sg, 'dims': dims, 'weights': weights, 'wall_occ': self.wall_occ, 'placements': placements}
        
        with open(save_path, 'wb') as f:
            pickle.dump(data, f)
    
    def compute_dims(self):
        dims = {}
        for obj in self.objects:
            dims[obj.name] = obj.get_whd()  
        return dims
    
    def compute_placements(self):
        placements = {}
        for obj in self.objects:
            _,_, front_side, back_side = obj.get_sides()
            front_vec = (front_side[0] + front_side[1])/2 - (back_side[0] + back_side[1])/2
            front_vec = front_vec/np.linalg.norm(front_vec)
            loc = obj.get_loc()
            placements[obj.name] = (np.array([loc[0],loc[2]]), front_vec)
        return placements
    
    def compute_sg(self):
        sg = SceneGraph('root')
        for obj in self.objects:
            if obj.child_of is None or obj.only_directional_child:
                sg.add_child(obj.name)
        
        for lvl1 in sg.children:
            for lvl2_3d in self.get_object(lvl1.name).children:
                lvl2 = lvl1.add_child(lvl2_3d.name)
                for lvl3_3d in lvl2_3d.children:
                    lvl3 = lvl2.add_child(lvl3_3d.name)
                    for lvl4_3d in lvl3_3d.children:
                        lvl4 = lvl3.add_child(lvl4_3d.name)
                        for lvl5_3d in lvl4_3d.children:
                            lvl4.add_child(lvl5_3d.name)
                            
        return sg           
                
    def compute_weights(self):
        all_weights = {'scene': (self.MAX_WIDTH, self.MAX_DEPTH), 'objects': []}
        
        for obj in self.objects:
            if obj.placed_on_wall or obj in self.auxilary_objects:
                continue
            if obj.on_floor:
                all_weights['objects'].append((obj.name, obj.get_loc(), obj.get_whd()[0]*obj.get_whd()[2]))
        return all_weights
            
        