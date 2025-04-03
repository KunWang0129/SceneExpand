import numpy as np
import trimesh
from scipy.spatial.transform import Rotation as R
from tools.llm import LLM
from tools.simpleagent import SimpleAgent
from modules.sdl.wall import PlaneMesh
import os
import json

class Object3DBase:
    def __init__(self, name, desc, scene, use_mesh=None):

        self.MAX_WIDTH = scene.MAX_WIDTH
        self.MAX_DEPTH = scene.MAX_DEPTH
        self.MAX_HEIGHT = scene.MAX_HEIGHT
        self.desc = desc
        self.name = name
        self.scene = scene
        self.visual=None
        self.use_mesh = use_mesh
        
        self.child_of = None
        self.only_directional_child = False
        self.children = []
        self.support_objs=[]
        self.possible_support_locs=None
        self.place_relative_params = None
        self.face_towards_obj = None
        self.rot=0
        self.buffer=0.1
        self.placed = False
        self.rotation_set=False
        self.delta_x = 0
        self.delta_y = 0
        self.delta_z = 0
        self.on_floor = None
        self.placed_on_wall = False
        
        
        self.ignore_overlap_llm = LLM(system_desc="You should return a boolean value in JSON format indicating whether the object should be ignored for overlap checks or not. Objects belonging to the following categories need to be ignored for overlap checks: 'windows', 'doors', 'curtains', 'rugs', 'paintings', 'mirrors', 'clocks'. Example output can be like (ignore_overlap:False)", response_format="json", json_keys=['ignore_overlap'])
        self.ignore_overlap=self.ignore_overlap_llm.run(self.desc)['ignore_overlap']
        if self.ignore_overlap:
            self.scene.overlap_exceptions.append(self)
            
        self.scale_agent = SimpleAgent(
            name="scale_agent",
            role="Scale the object to the correct dimensions.",
            description="""
Given the description of the object, output the realistic wdith, depth and height of the object in meters. 
You must respond in JSON format as follows: {{'width': 1.0, 'depth': 0.5, 'height': 1.5}}.
    For example:
    Input: A dining chair
    Your Response: {{'width': 0.5, 'depth': 0.5, 'height': 1.0}}
    Input: A king-size bed
    Your Response: {{'width': 2.0, 'depth': 2.1, 'height': 1.5}}
    Input: A armchair
    Your Response: {{'width': 0.9, 'depth': 0.95, 'height': 1.0}}
    Input: A coffee table
    Your Response: {{'width': 1.0, 'depth': 1.0, 'height': 0.6}}
    Input: A really long dining table
    Your Response: {{'width': 8.0, 'depth': 3.0, 'height': 0.7}}
    Input: A tall bookcase
    Your Response: {{'width': 1.0, 'depth': 0.5, 'height': 2.5}}
    Input: A small nightstand
    Your Response: {{'width': 0.5, 'depth': 0.5, 'height': 0.5}}
    Input: A large Chandelier
    Your Response: {{'width': 0.5, 'depth': 0.5, 'height': 0.8}}
    Input: Wall mounted shelves
    Your Response: {{'width': 1.0, 'depth': 0.5, 'height': 1.0}}
    """,
            concluding_llm=LLM(system_desc="Go through the chat and the realistic width, depth and height of the object in meters. Respond in JSON format!", response_format="json", json_keys=['width', 'depth', 'height']),
            additional_context="tmp/object_scale.txt" if os.path.exists("tmp/object_scale.txt") else None,
        )

    def copy(self, new_name):
        new_obj = Object3D(name=new_name, desc=self.desc, scene=self.scene)
        new_obj.mesh = self.mesh.copy()
        new_obj.visual = self.visual
        new_obj.width = self.width
        new_obj.height = self.height
        new_obj.depth = self.depth
        new_obj.proj_vertices = self.proj_vertices.copy()
        new_obj.place_relative_params = None
        new_obj.face_towards_obj = None
        new_obj.child_of = None
        new_obj.children = []
        new_obj.support_objs = []
        return new_obj        
        
    def save(self, path):
        if self.child_of is not None:
            self.child_of = self.child_of.name if isinstance(self.child_of, Object3D) else self.child_of
            
        np.savez(os.path.join(path, self.name), 
                    name = self.name,
                    desc=self.desc,
                    vertices=self.mesh.vertices, 
                    faces=self.mesh.faces, 
                    visual=self.visual, 
                    width=self.width, 
                    height=self.height, 
                    depth=self.depth, 
                    proj_vertices=self.proj_vertices, 
                    rot=self.rot, 
                    child_of=self.child_of,
                    children=[obj.name for obj in self.children], 
                    support_objs=[obj.name for obj in self.support_objs], 
                    possible_support_locs=self.possible_support_locs, 
                    place_relative_params=self.place_relative_params, 
                    face_towards_obj=self.face_towards_obj.name if self.face_towards_obj is not None else None)

    def init(self):
        if self.use_mesh:
            self.mesh = self.use_mesh
            self.visual = self.mesh.visual
            width, height, depth = self.get_whd(force=True)
            self.width = width
            self.height = height
            self.depth = depth
            self.set_proj_vertices()
            
        elif self.desc is None:
            self.mesh = trimesh.creation.box((1,1,1),np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]))
            self.normalize()
        else:
            if self.desc in self.scene.object_hash:
                path = self.scene.object_hash[self.desc]
            else:
                path = self.scene.retriever.run(self.desc)
                self.scene.object_hash[self.desc] = path
                with open('tmp/object_hash.json', 'w') as f:
                    json.dump(self.scene.object_hash, f)
                    
            self.load_mesh(path)
            self.normalize()
            
    def set_scale(self, dims=None):
        if dims:
            self.scale(dims[0], dims[1], dims[2])
        else:
            # dims = self.scale_llm.run(self.desc)
            dims = self.scale_agent.respond(self.desc)
            self.scale(dims['width'], dims['depth'], dims['height'])

    def float2int(self, x):
        return (1000*x).astype(int)/1000
    
    def get_aabb(self):
        return self.float2int(self.mesh.bounds)

    def get_whd(self, force=False):
        '''
        Returns the width, height and depth of the object.
        '''
        ## returns the width, height and depth of the object in canonical orientation
        if not force and self.width is not None and self.depth is not None and self.height is not None :
            return self.width, self.height, self.depth

        ## returns the dims of axis aligned bounding box of the object
        bounds = self.get_aabb()
        width = bounds[1,0] - bounds[0,0]
        depth = bounds[1,2] - bounds[0,2]
        height = bounds[1,1] - bounds[0,1]
        return width, height, depth

    def get_loc(self):
        bounds = self.get_aabb()
        return self.float2int((bounds[0]+bounds[1])/2)

    def get_proj2D(self):
        '''
        Returns the 2D projection of the object.
        '''
        vertices = self.proj_vertices
        vertices = vertices[:,[0,2]]
        return vertices

    def get_sides(self):
        proj_vertices = self.get_proj2D()
        left_side = (proj_vertices[0], proj_vertices[1])
        right_side = (proj_vertices[2], proj_vertices[3])
        front_side = (proj_vertices[0], proj_vertices[2])
        back_side = (proj_vertices[1], proj_vertices[3])  
        
        return left_side, right_side, front_side, back_side
    
    def get_min_max(self):
        bounds = self.get_aabb()
        xmin,ymin,zmin = bounds[0]
        xmax,ymax,zmax = bounds[1]
        return xmin,ymin,zmin,xmax,ymax,zmax    

    def reinit(self, vertices):
        # vertices = self.float2int(vertices)
        self.mesh = trimesh.Trimesh(vertices=vertices, faces=self.mesh.faces, process=False)

    def set_proj_vertices(self):
        bounds = self.get_aabb()
        v4 = np.array([[bounds[1,0], bounds[0,1], bounds[1,2]]])
        v5 = np.array([[bounds[1,0], bounds[0,1], bounds[0,2]]])
        v6 = np.array([[bounds[0,0], bounds[0,1], bounds[1,2]]])
        v7 = np.array([[bounds[0,0], bounds[0,1], bounds[0,2]]])
        self.proj_vertices = np.vstack((v4,v5,v6,v7))
        
    def normalize_translation(self):
        x,y,z = self.get_loc()
        T = np.array([[1,0,0,-x],[0,1,0,-y],[0,0,1,-z],[0,0,0,1]])
        vertices = self.mesh.vertices
        vertices = vertices@T[:3,:3].T + T[:3,3]
        self.reinit(vertices)
        self.proj_vertices = self.proj_vertices@T[:3,:3].T + T[:3,3]
        self.proj_vertices = self.float2int(self.proj_vertices)
    
    def normalize(self):
        vertices = self.mesh.vertices
        vertices -= vertices.min(axis=0)
        vertices /= vertices.max()
        
        vertices = self.float2int(vertices)
        self.reinit(vertices)
        self.set_proj_vertices()
        
        self.normalize_translation()
        self.width, self.height, self.depth = self.get_whd(force=True)
        
    def load_mesh(self, mesh_path):
        if 'objaverse' in mesh_path:
            from tools.objaverse import get_objaverse_local
            self.mesh = get_objaverse_local(mesh_path.split('/')[-1])
        else:
            self.mesh = trimesh.load(mesh_path, process=False, force='mesh')
        self.visual = self.mesh.visual

    def export(self, output_path):
        try:
            self.mesh.visual = self.visual
        except:
            pass
        return self.mesh.export(output_path)

class Object3D(Object3DBase):
    def __init__(self, name, desc, scene, use_mesh=None):
        super().__init__(name=name, desc=desc, scene=scene, use_mesh=use_mesh)

    def scale(self, width, depth, height):
        self.normalize()
        cw, ch, cl = self.get_whd(force=True)

        scale_factor_w = width/cw
        scale_factor_h = height/ch
        scale_factor_d = depth/cl

        vertices = self.mesh.vertices*np.array([scale_factor_w, scale_factor_h, scale_factor_d])
        self.reinit(vertices)
        self.proj_vertices = self.proj_vertices*np.array([scale_factor_w, scale_factor_h, scale_factor_d])

        width, height, depth = self.get_whd(force=True)
        ## sets the width, height and depth of the object in canonical orientation
        self.width = width
        self.height = height
        self.depth = depth

    def set_location(self, x, y, z):
        ## first move to origin and then move to desired location
        self.normalize_translation()
        vertices = self.mesh.vertices
        vertices = vertices + np.array([[x,y,z]])
        self.reinit(vertices)
        self.proj_vertices += np.array([[x,y,z]])
        self.x, self.y, self.z = self.get_loc()
        self.placed = True
        
    def displace(self, delta_x=0, delta_y=0, delta_z=0, update_delta=True):
        if update_delta:
            self.delta_x += delta_x
            self.delta_y += delta_y
            self.delta_z += delta_z
        
        self.set_location(self.x+delta_x, self.y+delta_y, self.z+delta_z)
        self.notify()
        
    def rotate_vertices_around_point(self, vertices, rot, point):
        x,y,z = point
        vertices -= np.array([[x,y,z]])
        r = R.from_euler('y', rot, degrees=True).as_matrix()
        vertices = (r@vertices.T).T
        vertices += np.array([[x,y,z]])
        return vertices
    
    def set_rotation(self, rot):
        rot = rot%360
        # assert rot in [0, 45, 90, 135, 180, 225, 270, 315]
        tmp = rot
        rot = rot-self.rot
        vertices = self.mesh.vertices
        loc = self.get_loc()
        vertices = self.rotate_vertices_around_point(vertices, rot, loc)
        self.reinit(vertices)
        self.proj_vertices = self.rotate_vertices_around_point(self.proj_vertices, rot, loc)
        self.rot = tmp
        self.rotation_set=True
        
        
    def face_towards(self, obj):
        assert isinstance(obj, Object3D) or isinstance(obj, PlaneMesh) or obj in ['left_wall', 'right_wall', 'front_wall', 'back_wall'], 'obj should be an instance of Object3D or a string - "left_wall", "right_wall", "front_wall", "back_wall"' 

        if obj == 'left_wall':
            rot = -90
        elif obj == 'right_wall':
            rot = 90
        elif obj == 'front_wall':
            rot = 0
        elif obj == 'back_wall':
            rot = 180

        elif type(obj) == tuple:
            v2 = np.array(obj)
            v2 = np.array([v2[0], 0, v2[1]])
            v1 = self.get_loc()
            rel = v2-v1
            rel /= np.linalg.norm(rel)
            rot = np.arctan2(rel[0],rel[1])*180/np.pi
            rot = np.round(rot/45)*45
        else:
            v2 = obj.get_loc()
            v1 = self.get_loc()
            rel = v2-v1
            rel /= np.linalg.norm(rel)
            rot = np.arctan2(rel[0],rel[2])*180/np.pi
            rot = np.round(rot/45)*45
            
        self.set_rotation(rot)
        
        if isinstance(obj, Object3D):
            self.face_towards_obj = obj
            if self not in obj.children:
                self.only_directional_child = True
            self.child_of = obj
            self.notify()

    def update(self):
        if self.place_relative_params is not None:   ## If placed using relative
            self.place_relative(**self.place_relative_params)
            self.displace(delta_x=self.delta_x, delta_y=self.delta_y, delta_z=self.delta_z, update_delta=False)
        elif self.face_towards_obj is not None:  ## If this was placed using global
            self.face_towards(self.face_towards_obj)
            
        self.notify()
            
    def notify(self):
        for child in set(self.children):
            child.update()

    def place_support_objs_naive(self):
        N = len(self.support_objs)
        right_side, left_side, front_side, back_side = self.get_sides()
        right = np.mean(right_side,axis=0)
        left = np.mean(left_side,axis=0)
        vector = right - left
        locs = [left + i * vector / (N + 1) for i in range(1, N + 1)]
        y = self.get_whd()[1]
        for i, obj in enumerate(self.support_objs):
            obj.normalize_translation()
            obj.set_location(locs[i][0], y+obj.height/2, locs[i][1])
            
    def place_support_objs(self):
        def get_max_dims_of_supported_objs():
            max_dims = np.zeros(2)
            for obj in self.support_objs:
                w,_,d = obj.get_whd()
                max_dims = np.maximum(max_dims, np.array([w,d]))
            return max_dims

        w,d = get_max_dims_of_supported_objs()
        
        # picker = LLM(system_desc="If the object described is a Bookshelf or Shelf (note, cabinets are different), then you should return True else False. Your response should in the the JSON format like this - {{'open_shelves':True}}", response_format='json')
       
        sr = SupportRegions(self.mesh)
        try:
            self.possible_support_locs = sr.compute_locs_on_top(w,d)
            for i, obj in enumerate(self.support_objs):
                obj.normalize_translation()
                obj.place_global(x=self.possible_support_locs[i][0], y=self.possible_support_locs[i][1]+obj.height/2, z=self.possible_support_locs[i][2])
        except:
            self.place_support_objs_naive()
            
    def get_side_dirs(self, obj):
        right_side, left_side, front_side, back_side = obj.get_sides()
        cen = obj.get_loc()[[0,2]]
        x_hat = np.mean(right_side,axis=0) - cen
        x_hat = x_hat/np.linalg.norm(x_hat)
        z_hat = np.mean(front_side,axis=0) - cen
        z_hat = z_hat/np.linalg.norm(z_hat)
        return x_hat, z_hat

    def place_relative(self, relation, obj, dist=0, sideways_shift=0, face_towards=None, delta_x=0, delta_y=0, delta_z=0):
        
        if type(obj) == str:
            obj = self.scene.get_object(obj)
        
        if not self.rotation_set and face_towards:
            if type(face_towards) == str:
                face_towards = self.scene.get_object(face_towards)
            else:
                face_towards = face_towards
            
        assert isinstance(obj, Object3D), 'obj should be an instance of Object3D, alternatively, you may want to use place_global method.'
        assert relation in ['left_of', 'right_of', 'in_front_of', 'behind_of', 'on_top_of', 'right_adj', 'left_adj'], 'relation should be one of the following - "left_of", "right_of", "in_front_of", "behind_of", "on_top_of", "right_adj", "left_adj"'
        assert type(dist) == float or type(dist) == int, 'dist should be a float or an int'
        assert type(sideways_shift) == float or type(sideways_shift) == int, 'sideways_shift should be a float or an int'
        assert face_towards is None or isinstance(face_towards, Object3D) or type(face_towards) == str or isinstance(face_towards, PlaneMesh), 'face_towards should be either None or an instance of Object3D or a string - "left_wall", "right_wall", "front_wall", "back_wall"'
        
        if face_towards is not None and type(face_towards) == str and face_towards not in ['left_wall', 'right_wall', 'front_wall', 'back_wall']:
            try:
                face_towards = self.scene.get_object(face_towards)
            except:
                pass

        self.child_of = obj.name
        if relation == 'on_top_of':
            if self not in self.scene.overlap_exceptions:
                self.scene.overlap_exceptions.append(self)

        if self.place_relative_params is None:
            self.place_relative_params = {'relation':relation, 'obj':obj.name, 'dist':dist, 'sideways_shift':sideways_shift, 'face_towards':face_towards, 'delta_x':self.delta_x, 'delta_y':self.delta_y, 'delta_z':self.delta_z}
            if self not in obj.children:
                obj.children.append(self)

        width, height, depth = self.get_whd()
        w0, h0, l0 = obj.get_whd()
        x_hat, z_hat = self.get_side_dirs(obj)
        dist= np.abs(dist)
        __dist = dist

        if not self.rotation_set and face_towards is None:
            rot = obj.rot
            self.set_rotation(rot)
        
        if relation == 'on_top_of':
            if self not in obj.support_objs:
                obj.support_objs.append(self)
            obj.place_support_objs()
        else:
            self.on_floor = True
            if relation == 'right_of':
                dist += (w0/2 + width/2)
                x,z = obj.get_loc()[[0,2]] + dist*x_hat
                sd = sideways_shift*z_hat
                x += sd[0]
                z += sd[1]
            elif relation == 'left_of':
                dist += (w0/2 + width/2)
                x,z = obj.get_loc()[[0,2]] - dist*x_hat
                sd = sideways_shift*z_hat
                x += sd[0]
                z += sd[1]
            elif relation == 'in_front_of':
                dist += (l0/2 + depth/2)
                x,z = obj.get_loc()[[0,2]] + dist*z_hat
                sd = sideways_shift*x_hat
                x += sd[0]
                z += sd[1]
            elif relation == 'behind_of':
                dist += (l0/2 + depth/2)
                x,z = obj.get_loc()[[0,2]] - dist*z_hat
                sd = sideways_shift*x_hat
                x += sd[0]
                z += sd[1]
            elif relation == 'right_adj':
                dist += (w0/2 + width/2)
                x,z = obj.get_loc()[[0,2]] + dist*x_hat
                sd = (sideways_shift + l0/2 - depth/2)*(-z_hat)
                x += sd[0]
                z += sd[1]
            elif relation == 'left_adj':
                dist += (w0/2 + width/2)
                x,z = obj.get_loc()[[0,2]] - dist*x_hat
                sd = (sideways_shift + l0/2 - depth/2)*(-z_hat)
                x += sd[0]
                z += sd[1]
                
            self.set_location(x, height/2, z)
        
        if face_towards is not None:
            self.face_towards(face_towards)

        def obj_buffer_computation_along_a_dir(obj, dir):
        
            def is_point_inside_bounding_box(pt, v1, v2, v3, v4):
                # Extracting the x and y coordinates of the vertices
                x_coords = [v1[0], v2[0], v3[0], v4[0]]
                y_coords = [v1[1], v2[1], v3[1], v4[1]]

                # Finding the minimum and maximum coordinates
                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)

                # Checking if the point lies within the bounding box
                return min_x <= pt[0] <= max_x and min_y <= pt[1] <= max_y

            def fraction_of_line_segment_covered(pt1, pt2, v1, v2, v3, v4, res = 1000):
                count=0
                for i in range(res):
                    pt = pt1 + (i/res)*(pt2-pt1)
                    if is_point_inside_bounding_box(pt, v1, v2, v3, v4):
                        count+=1
                return int((count/res)*100)/100
            
            pos1 = obj.get_loc()[[0,2]]
            dir = dir/np.linalg.norm(dir)
            pos2 = pos1 + dir*5
        
            covered = fraction_of_line_segment_covered(pos1, pos2, *obj.get_proj2D())
            return covered*5

        if relation in ['left_of', 'right_of', 'in_front_of', 'behind_of']:
            
            dist=__dist
            dir = obj.get_loc()[[0,2]] - self.get_loc()[[0,2]]
            self.set_location(obj.x, self.y, obj.z)
            if relation == 'right_of':
                dist += (w0/2 + obj_buffer_computation_along_a_dir(self, dir))
                x,z = obj.get_loc()[[0,2]] + dist*x_hat
                sd = sideways_shift*z_hat
                x += sd[0]
                z += sd[1]
            elif relation == 'left_of':
                dist += (w0/2 + + obj_buffer_computation_along_a_dir(self, dir))
                x,z = obj.get_loc()[[0,2]] - dist*x_hat
                sd = sideways_shift*z_hat
                x += sd[0]
                z += sd[1]
            elif relation == 'in_front_of':
                dist += (l0/2 + + obj_buffer_computation_along_a_dir(self, dir))
                x,z = obj.get_loc()[[0,2]] + dist*z_hat
                sd = sideways_shift*x_hat
                x += sd[0]
                z += sd[1]
            elif relation == 'behind_of':
                dist += (l0/2 + + obj_buffer_computation_along_a_dir(self, dir))
                x,z = obj.get_loc()[[0,2]] - dist*z_hat
                sd = sideways_shift*x_hat
                x += sd[0]
                z += sd[1]
            
            self.set_location(x, height/2, z)
        
        self.notify()

    def place_global(self, x=None, y='floor', z=None, delta_x=0.0, delta_y=0.0, delta_z=0.0, face_towards=None):
        
        assert x is not None and y is not None and z is not None
        if type(x) == str:
            assert x in ['left_wall', 'right_wall', 'center'], 'x should be either a float or a string. Accepted strings are "left_wall", "center" and "right_wall"'
        if type(y) == str:
            assert y in ['floor', 'ceiling'], 'y should be either a float or a string. Accepted strings are "floor" and "ceiling"'
        if type(z) == str:
            assert z in ['front_wall', 'back_wall','center'], 'z should be either a float or a string. Accepted strings are "front_wall", "center" and "back_wall"'
        
        rot_set=False
        if face_towards is not None and type(face_towards) == str and face_towards not in ['left_wall', 'right_wall', 'front_wall', 'back_wall']:
            ## convert string to scene object
            print("Found using string for object,", face_towards)
            try:
                face_towards = self.scene.get_object(face_towards)
            except:
                pass
            rot_set=True
        assert face_towards is None or isinstance(face_towards, Object3D) or face_towards in ['left_wall', 'right_wall', 'front_wall', 'back_wall'], 'face_towards should be either None or an instance of Object3D or one of the four walls - "left_wall", "right_wall", "front_wall", "back_wall"'
        assert type(delta_x) == float or type(delta_x) == int, 'delta_x should be a float or an int'
        assert type(delta_y) == float or type(delta_y) == int, 'delta_y should be a float or an int'
        assert type(delta_z) == float or type(delta_z) == int, 'delta_z should be a float or an int'
            
        
        if face_towards in ['left_wall', 'right_wall', 'front_wall', 'back_wall']:
            self.face_towards(face_towards)
            rot_set=True
        
        delta_x = np.abs(delta_x)
        delta_y = np.abs(delta_y)
        delta_z = np.abs(delta_z)
        
        if y == 'floor':
            self.on_floor = True
            
        if x == 'left_wall':
            if face_towards is None and not rot_set:
                self.face_towards('right_wall')
                rot_set=True
            x = self.get_whd(force=True)[0]/2 + delta_x + self.buffer
        elif x == 'right_wall':
            if face_towards is None and not rot_set:
                self.face_towards('left_wall')
                rot_set=True
            x = self.MAX_WIDTH - self.get_whd(force=True)[0]/2 - delta_x - self.buffer
        elif x == 'center':
            x = self.MAX_WIDTH/2 + delta_x
            
        if y == 'floor':
            y = self.get_whd(force=True)[1]/2 + delta_y
        elif y == 'ceiling':
            y = self.MAX_HEIGHT - self.get_whd(force=True)[1]/2 - delta_y
        
        if z == 'back_wall':
            if face_towards is None and not rot_set:
                self.face_towards('front_wall')
                rot_set=True
            z = self.get_whd(force=True)[2]/2 + delta_z + self.buffer
        elif z == 'front_wall':
            if face_towards is None and not rot_set:
                self.face_towards('back_wall')
                rot_set=True
            z = self.MAX_DEPTH - self.get_whd(force=True)[2]/2 - delta_z - self.buffer
        elif z == 'center':
            z = self.MAX_DEPTH/2 + delta_z
            
        self.set_location(x, y, z)
        if isinstance(face_towards, Object3D):
            self.face_towards(face_towards)
            rot_set=True

        self.notify()

    def place_seats_around_round_arrangement(self, list_of_seats=[]):
        assert type(list_of_seats) == list, 'Input should be a list of objects of type Object3D or leave it as an empty list'
        assert len(list_of_seats) > 0, 'Input list should not be empty'
        
        radius = 0.2
        assert radius > 0, 'Radius should be float greater than 0'
        
        N = len(list_of_seats)
        ang_diff = 360/(N)
        rot = []
        for i in range(N):
            rot.append(ang_diff*i)
        x, y, z = self.get_loc()
        
        w0, h0, l0 = self.get_whd()
        
        buffer = w0+list_of_seats[0].get_whd()[0]
        radius += buffer/2
        for i, seat in enumerate(list_of_seats):
            seat.place_global(x=x+radius*np.sin(np.radians(rot[i])), y='floor', z=z-radius*np.cos(np.radians(rot[i])))
            seat.face_towards(self)
    
    def place_seats_rectangular_arrangement(self, first_longer_side=[], second_longer_side=[], first_shorter_side=[], second_shorter_side=[]):
        assert type(first_longer_side) == list and type(second_longer_side) == list and type(first_shorter_side) == list and type(second_shorter_side) == list, 'All inputs should be lists containing objects of type Object3D, provide empty list if no seats are to be placed.'
        
        dist_between_chairs = 0.1
        dist_from_table = 0.5
        need_to_change=False
        new_width=self.get_whd()[0]
        new_depth=self.get_whd()[2]
        
        if len(first_longer_side)>0 and len(first_longer_side)*(first_longer_side[0].get_whd()[0]+dist_between_chairs) > self.get_whd()[0]:
            new_width = len(first_longer_side)*(first_longer_side[0].get_whd()[0]+dist_between_chairs)
            need_to_change=True
            
        if len(second_longer_side)>0 and len(second_longer_side)*(second_longer_side[0].get_whd()[0]+dist_between_chairs) > self.get_whd()[0]:
            width = len(second_longer_side)*(second_longer_side[0].get_whd()[0]+dist_between_chairs)
            need_to_change=True
            if width > new_width:
                new_width = width
                
        if len(first_shorter_side)>0 and len(first_shorter_side)*(first_shorter_side[0].get_whd()[0]+dist_between_chairs) > self.get_whd()[2]:
            new_depth = len(first_shorter_side)*(first_shorter_side[0].get_whd()[0]+dist_between_chairs)
            need_to_change=True
        
        if len(second_shorter_side)>0 and len(second_shorter_side)*(second_shorter_side[0].get_whd()[0]+dist_between_chairs) > self.get_whd()[2]:
            depth = len(second_shorter_side)*(second_shorter_side[0].get_whd()[0]+dist_between_chairs)
            need_to_change=True
            if depth > new_depth:
                new_depth = depth
        
        if need_to_change:
            with open('tmp/object_scale.txt','a') as f:
                f.write(f"For the object named {self.name} with description {self.desc}, use the following dimensions: width={new_width}, depth={new_depth}, height={self.get_whd()[1]}\n")
        
        def compute_sideways_coordinates(length, N, seat_width):
            S = (length - N * seat_width) / (N+1)
            return [(seat_width / 2 + S) + i * (seat_width + S) -length/2 for i in range(N)]
        
        total_length = self.get_whd()[0]
        total_width = self.get_whd()[2]
        
        if len(first_longer_side) > 0:
            sideways_coordinates_first_longer_side = compute_sideways_coordinates(total_length, len(first_longer_side), first_longer_side[0].get_whd()[0])
            for seat in first_longer_side:
                seat.place_relative(relation='in_front_of', obj=self, dist=dist_from_table, sideways_shift=int(100*sideways_coordinates_first_longer_side.pop(0))/100)
                seat.set_rotation(self.rot-180)
        
        if len(second_longer_side) > 0:
            sideways_coordinates_second_longer_side = compute_sideways_coordinates(total_length, len(second_longer_side), second_longer_side[0].get_whd()[0])
            for seat in second_longer_side:
                seat.place_relative(relation='behind_of', obj=self, dist=dist_from_table, sideways_shift=int(100*sideways_coordinates_second_longer_side.pop(0))/100)
                seat.set_rotation(self.rot)
            
        if len(first_shorter_side) > 0:
            sideways_coordinates_first_shorter_side = compute_sideways_coordinates(total_width, len(first_shorter_side), first_shorter_side[0].get_whd()[0])
            for seat in first_shorter_side:
                seat.place_relative(relation='right_of', obj=self, dist=dist_from_table, sideways_shift=int(100*sideways_coordinates_first_shorter_side.pop(0))/100)
                seat.set_rotation(self.rot-90)
            
        if len(second_shorter_side) > 0:
            sideways_coordinates_second_shorter_side = compute_sideways_coordinates(total_width, len(second_shorter_side), second_shorter_side[0].get_whd()[0])
            for seat in second_shorter_side:
                seat.place_relative(relation='left_of', obj=self, dist=dist_from_table, sideways_shift=int(100*sideways_coordinates_second_shorter_side.pop(0))/100)
                seat.set_rotation(self.rot+90)
              
    def displace_on_wall(self, wall):
        delta = self.get_whd()[2]/2 + 0.05
        if wall.name=='back_wall':
            self.displace(delta_z=delta)
        elif wall.name=='left_wall':
            self.displace(delta_x=delta)
        elif wall.name=='front_wall':
            self.displace(delta_z=-delta)
        elif wall.name=='right_wall':
            self.displace(delta_x=-delta)
        else:
            breakpoint()
              
    def place_on_wall(self, wall, horizontal_position='middle', vertical_position='middle'):
        assert horizontal_position in ['middle', 'left', 'right'], 'position should be one of the following - "middle", "left", "right"'
        assert vertical_position in ['top', 'bottom', 'middle'], 'position should be one of the following - "top", "bottom", "middle"'
        
        if type(wall)==str:
            wall = self.scene.get_object(wall)
        
        self.placed_on_wall = True
        
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
        
        pos = wall.compute_window_coordinates(horizontal_position)
        if vertical_position == 'middle':
            height = np.min((self.MAX_HEIGHT-1.5, 2)) + self.height/2
            delta_y = 0.0
        elif vertical_position == 'top':
            height = 'ceiling'
            delta_y = 0.4
        else:
            height = 'floor'
            delta_y = 0.0
            
        self.place_global(x=pos[0], y=height, z=pos[2], delta_y=delta_y)
        if wall.name=='back_wall':
            self.face_towards('front_wall')
        elif wall.name=='left_wall':
            self.face_towards('right_wall')
        elif wall.name=='front_wall':
            self.face_towards('back_wall')
        elif wall.name=='right_wall':
            self.face_towards('left_wall')
        else:
            breakpoint()
        self.displace_on_wall(wall)
        
        self.scene.wall_occ[wall.name][horizontal_position].append(self.name)
        
class SupportRegions:
    def __init__(self, mesh):
        self.mesh = mesh
        self.ground_clearance = 0.2
        self.buffer = 0.03
        self.cluster=4
        self.get_support_points()
        
    def get_support_points(self):
        points, face_idx = self.mesh.sample(50000, return_index=True)
        normals = self.mesh.face_normals[face_idx]
        up = np.array([0, 1, 0])
        points = points[normals.dot(up) > 0.98]
        points = points[points[:, 1] > self.ground_clearance]
        self.points = points
            
    def points_at_height(self, height):
        return self.points[(self.points[:, 1] > height - self.buffer) & (self.points[:, 1] < height + self.buffer)]
    
    def find_heights(self):
        # Reshape data for KMeans
        data = np.array(self.points[:, 1]).reshape(-1, 1)
        from sklearn.cluster import KMeans
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=self.cluster, random_state=0)
        kmeans.fit(data)
        
        support_info = []
        for i in range(self.cluster):
            idxs = kmeans.labels_ == i
            points = self.points[idxs]
            if points.shape[0] == 0:
                continue
            avg_height = points[:, 1].mean()
            prob = len(points)/len(self.points)
            if prob <0.05:
                continue
            support_info.append((points, avg_height, prob))
                    
        support_info = sorted(support_info, key=lambda x: -x[1])
        return support_info
        
    def rectangular_bounds_for_points(self, points):
        return np.array([points.min(axis=0)+0.1, points.max(axis=0)-0.1])
    
    def remove_points_overlapping_with_bounds(self, points, bounds):
        return points[~np.all(points >= bounds[0], axis=1) & ~np.all(points <= bounds[1], axis=1)]
    
    def compute_bounds_area(self, bounds):
        w = bounds[1][0] - bounds[0][0]
        d = bounds[1][2] - bounds[0][2]
        return w*d
    
    def subdivide_rectangle(self, bounds, w, d):
        """
        a --- b
        |     |
        |     |
        c --- d
        """
        pa = np.array([bounds[0][0], bounds[0][2]])
        pb = np.array([bounds[1][0], bounds[0][2]])
        pc = np.array([bounds[0][0], bounds[1][2]])
        pd = np.array([bounds[1][0], bounds[1][2]])
        
        # Calculate the lengths of the rectangle's sides
        length_x = np.linalg.norm(pb - pa)
        length_y = np.linalg.norm(pc - pa)

        # Determine the number of partitions along each dimension
        num_partitions_x = max(int(length_x // w),1)
        num_partitions_y = max(int(length_y // d),1)
        
        # Calculate the vectors along the rectangle's sides
        x_vector = (pb - pa) / num_partitions_x
        y_vector = (pc - pa) / num_partitions_y

        # Create list to store subdivided region coordinates
        regions = []

        # Generate coordinates for each subdivided region
        for i in range(num_partitions_x):
            for j in range(num_partitions_y):
                # Calculate the vertices of each sub-region
                bottom_left = pa + i * x_vector + j * y_vector
                bottom_right = bottom_left + x_vector
                top_left = bottom_left + y_vector
                top_right = bottom_right + y_vector

                # Append the coordinates of the region
                regions.append([bottom_left, bottom_right, top_right, top_left])

        return regions
    
    def possible_locations(self, regions):
        locs = []
        for region in regions:
            for r in region['regions']:
                x,z = np.array(r).mean(axis=0)
                locs.append((np.array([x, region['height'], z]), region['prob']))
                
        def probabilistic_sort(items_probs):
            # Separate items and probabilities
            items, probabilities = zip(*items_probs)
            
            # Generate random scores based on the probabilities
            random_scores = -np.log(np.random.rand(len(probabilities))) / probabilities
            
            # Sort items by these scores
            sorted_items = [item for _, item in sorted(zip(random_scores, items))]
            
            return sorted_items

        return probabilistic_sort(locs)

    def compute_locs_on_top(self, w, d):
        support_info = self.find_heights()
        
        top_bounds = [self.rectangular_bounds_for_points(support_info[0][0])]
        top_height = [support_info[0][1]]
        top_prob = [support_info[0][2]]
        
        for i, data in enumerate(support_info[1:]):
            points, _, _ = data
            points = self.remove_points_overlapping_with_bounds(points, top_bounds[-1])
            if len(points)==0:
                continue
            
            bounds = self.rectangular_bounds_for_points(points)
            if self.compute_bounds_area(bounds) < w*d:
                continue
            
            top_bounds.append(bounds)
            top_height.append(data[1])
            top_prob.append(data[2])
        
        subdivided_regions=[]
        for i in range(len(top_bounds)):
            bounds = top_bounds[i]
            regions = self.subdivide_rectangle(bounds, w, d)
            if len(regions)==0:
                continue
            subdivided_regions.append({'regions': regions, 'height': top_height[i], 'prob': top_prob[i]/len(regions)})
            
        return self.possible_locations(subdivided_regions)
    
    def compute_locs_inside(self, w, d):
        support_info = self.find_heights()
        
        subdivided_regions = []
        for i, data in enumerate(support_info):
            points, height, prob = data
            bounds = self.rectangular_bounds_for_points(points)
            regions = self.subdivide_rectangle(bounds, w, d)
            if len(regions)==0:
                continue
            subdivided_regions.append({'regions': regions, 'height': height, 'prob': prob/len(regions)})
        return self.possible_locations(subdivided_regions)