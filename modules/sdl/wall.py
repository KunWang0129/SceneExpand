import numpy as np
import trimesh
from scipy.spatial.transform import Rotation as R
from tools.llm import LLM
from tqdm import tqdm
import os
from tools.clip import clip_image_embedding, clip_text_embedding
from PIL import Image

class PlaneMesh:
    def __init__(self, height, width, res=10, color='white'):
        self.res = res
        self.width = int(width*self.res)
        self.height = int(height*self.res)
        self.color = color
        self.mesh_soup, self.uvs = self.create()
        
        self.mesh = None
        
    def get_wh(self):
        return self.width/self.res, self.height/self.res
    
    def get_face_color(self, faces):
        color = LLM(system_desc="Given a color description, your task is to return the RGB values of the color in the format (R, G, B) as a JSON object. Example: 'red' -> 'R': 255, 'G': 0, 'B': 0", response_format="json", json_keys=['R','G','B']).run(self.color)
        color = [int(color['R']), int(color['G']), int(color['B']), 255]
        face_colors = np.ones((len(faces), 4))*color
        return face_colors
        
    def get_texture(self):
        color = LLM(system_desc="Given a color description, your task is to return the RGB values of the color in the format (R, G, B) as a JSON object. Example: 'red' -> 'R': 255, 'G': 0, 'B': 0", response_format="json", json_keys=['R','G','B']).run(self.color)
        color = [int(color['R']), int(color['G']), int(color['B']), 255]
        image = np.ones((1024, 1024, 4), dtype=np.uint8)
        image *= np.array(color, dtype=np.uint8)
        texture_image = Image.fromarray(image)
        return texture_image
        
    
    def create(self):
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0]
        ])
        
        faces = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ])
        
        uv = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1]
        ])
        base_mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        
        meshes = []
        uvs = []
        for i in range(self.width):
            meshes.append([])
            uvs.append([])
            for j in range(self.height):
                mesh = base_mesh.copy()
                mesh.apply_translation([i, j, 0])
                uv = uv.copy()
                uv[:,0] += i
                uv[:,1] += j
                uvs[i].append(uv)
                meshes[i].append(mesh)
        return meshes, uvs
    
    def get_mesh(self):
        all_meshes = []
        all_uvs = []
        for i in range(self.width):
            for j in range(self.height):
                if self.mesh_soup[i][j] is not None:
                    all_meshes.append(self.mesh_soup[i][j])
                    all_uvs.append(self.uvs[i][j])
        mesh = trimesh.util.concatenate(all_meshes)
        
        vertices = mesh.vertices/self.res
        mesh = trimesh.Trimesh(vertices=vertices, faces=mesh.faces, process=False)
        
        return mesh, np.array(all_uvs).reshape(-1, 2)
    
    def export(self, filename):
        self.get_mesh().export(filename)
        
    def delete_box(self, j, i):
        self.mesh_soup[i][j] = None
        self.uvs[i][j] = None
        
    
    def create_cavity(self, jmin, jmax, imin, imax):
        
        jmin = int(jmin*self.res)
        jmax = int(jmax*self.res)
        imin = int(imin*self.res)
        imax = int(imax*self.res)
        for j in range(jmin, jmax):
            for i in range(imin, imax):
                self.delete_box(j, i)

    def make_space_for_window(self, window):
        buffer = 0.1
        bounds = window.get_aabb()
        jmin,jmax = bounds[0,1]+buffer, bounds[1,1]-buffer
        if self.name == 'left_wall':
            imin, imax = self.get_wh()[0]-bounds[1,2]+buffer, self.get_wh()[0] -bounds[0,2] -buffer
        elif self.name == 'right_wall':
            imin, imax = bounds[0,2]+buffer, bounds[1,2]-buffer
        elif self.name == 'front_wall':
            imin, imax = self.get_wh()[0]-bounds[1,0]+buffer, self.get_wh()[0]-bounds[0,0]-buffer
        else:
            imin, imax = bounds[0,0]+buffer, bounds[1,0]-buffer
        
        self.create_cavity(jmin, jmax, imin, imax)
        
    def max_window_width(self):
        
        bounds = self.get_mesh()[0].bounds
        min, max = bounds[0], bounds[1]
        diff = max-min
        v1 = np.array((diff[0], 0, diff[2]))
        v0 = np.array((min[0], 0, min[2]))
        
        return 0.2*np.linalg.norm(v1-v0)
    
    def rotate_vertices_around_point(self, vertices, rot, point):
        x,y,z = point
        vertices -= np.array([[x,y,z]])
        r = R.from_euler('y', rot, degrees=True).as_matrix()
        vertices = (r@vertices.T).T
        vertices += np.array([[x,y,z]])
        return vertices
    
    def compute_window_coordinates(self, position):
        assert position in ['left', 'middle', 'right', 'full'], 'Must be a string -- one of [left, middle, right].'
        
        mesh = self.build()
        
        min, max = mesh.bounds[0], mesh.bounds[1]
        
        if self.name == 'left_wall':
            if position == 'left':
                pos = [0, 0, 0.8*max[2]]
            elif position == 'middle' or position == 'full':
                pos = [0, 0, 0.5*max[2]]
            elif position == 'right':
                pos = [0, 0, 0.2*max[2]]
            else:
                raise ValueError("Invalid position for window.")
        
        elif self.name == 'right_wall':
            if position == 'left':
                pos = [max[0], 0, 0.2*max[2]]
            elif position == 'middle' or position == 'full':
                pos = [max[0], 0, 0.5*max[2]]
            elif position == 'right':
                pos = [max[0], 0, 0.8*max[2]]
            else:
                raise ValueError("Invalid position for window.")
            
        elif self.name == 'front_wall':
            if position == 'left':
                pos = [0.8*max[0], 0, max[2]]
            elif position == 'middle' or position == 'full':
                pos = [0.5*max[0], 0, max[2]]
            elif position == 'right':
                pos = [0.2*max[0], 0, max[2]]
            else:
                raise ValueError("Invalid position for window.")
            
        elif self.name == 'back_wall':
            if position == 'left':
                pos = [0.2*max[0], 0, 0]
            elif position == 'middle' or position == 'full':
                pos = [0.5*max[0], 0, 0]
            elif position == 'right':
                pos = [0.8*max[0], 0, 0]
            else:
                raise ValueError("Invalid position for window.")
            
        return pos
                
class LeftWall(PlaneMesh):
    def __init__(self, scene, res=10, color='white'):
        super().__init__(scene.MAX_HEIGHT, scene.MAX_DEPTH, res, color)
        self.scene = scene
        self.color = color
        self.name = 'left_wall'

    def build(self):
        mesh, uvs = self.get_mesh()
        vertices = self.rotate_vertices_around_point(mesh.vertices, 90, [0, 0, 0])
        vertices[:,2] += self.scene.MAX_DEPTH
        mesh = trimesh.Trimesh(vertices=vertices, faces=mesh.faces, process=False)
        texture_image = self.get_texture()
        mesh.visual = trimesh.visual.TextureVisuals(uv=uvs, image=texture_image)
        return mesh
    
    def get_loc(self):
        x=0
        y=self.scene.MAX_HEIGHT/2
        z=self.scene.MAX_DEPTH/2
        return x,y,z
        
class RightWall(PlaneMesh):
    def __init__(self, scene, res=10, color='white'):
        super().__init__(scene.MAX_HEIGHT, scene.MAX_DEPTH, res, color)
        self.scene = scene
        self.color = color
        self.name = 'right_wall'
        
    def build(self):
        mesh,uvs = self.get_mesh()
        vertices = self.rotate_vertices_around_point(mesh.vertices, -90, [0, 0, 0])
        vertices[:,0] += self.scene.MAX_WIDTH
        mesh = trimesh.Trimesh(vertices=vertices, faces=mesh.faces, process=False)
        texture_image = self.get_texture()
        mesh.visual = trimesh.visual.TextureVisuals(uv=uvs, image=texture_image)
        
        return mesh
    
    def get_loc(self):
        x=self.scene.MAX_WIDTH
        y=self.scene.MAX_HEIGHT/2
        z=self.scene.MAX_DEPTH/2
        return x,y,z
    
class FrontWall(PlaneMesh):
    def __init__(self, scene, res=10, color='white'):
        super().__init__(scene.MAX_HEIGHT, scene.MAX_WIDTH, res, color)
        self.scene = scene
        self.color = color
        self.name = 'front_wall'
        
    def build(self):
        mesh,uvs = self.get_mesh()
        vertices = self.rotate_vertices_around_point(mesh.vertices, 180, [0, 0, 0])
        vertices[:,2] += self.scene.MAX_DEPTH
        vertices[:,0] += self.scene.MAX_WIDTH
        mesh = trimesh.Trimesh(vertices=vertices, faces=mesh.faces, process=False)
        texture_image = self.get_texture()
        mesh.visual = trimesh.visual.TextureVisuals(uv=uvs, image=texture_image)
        
        return mesh
    
    def get_loc(self):
        x=self.scene.MAX_WIDTH/2
        y=self.scene.MAX_HEIGHT/2
        z=self.scene.MAX_DEPTH
        return x,y,z
    
class BackWall(PlaneMesh):
    def __init__(self, scene, res=10, color='white'):
        super().__init__(scene.MAX_HEIGHT, scene.MAX_WIDTH, res, color)
        self.scene = scene
        self.color = color
        self.name = 'back_wall'
        
    def build(self):
        mesh,uvs = self.get_mesh()
        mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, process=False)
        texture_image = self.get_texture()
        mesh.visual = trimesh.visual.TextureVisuals(uv=uvs, image=texture_image)
        return mesh
    
    def get_loc(self):
        x=self.scene.MAX_WIDTH/2
        y=self.scene.MAX_HEIGHT/2
        z=0
        return x,y,z
    
class TexturedWall:
    def __init__(self, scene, texture):
        self.texture = texture
        self.scene = scene
        self.textures_path= '/Users/kunalgupta/Documents/datasets/'
        self.res = 3
        self.embeddings_path = 'assets/texture_embeddings.npz'
        if os.path.exists(self.embeddings_path):
            cache = np.load(self.embeddings_path)
            self.embeddings = cache['embeddings']
            self.paths = cache['paths']
        else:
            self.build_textures()
        
    def save(self, path):
        self.mesh = self.build()
        np.savez(os.path.join(path, self.name+'.npz'), mesh=self.mesh)
        
    def build_textures(self):
        print("Did not find embeddings for textures, building now.")
        all_embedings = []
        all_texture_paths = []
        for d in tqdm(os.listdir(self.textures_path)):
            img_path = os.path.join(self.textures_path,d,)
            if not os.path.isdir(img_path):
                continue
            
            img_path = os.path.join(img_path,'texture.png')
            if not os.path.exists(img_path):
                alternate_path = os.path.join(img_path,'texture.jpg')
                if not os.path.exists(alternate_path):
                    continue
                img_path = alternate_path
            embedding = clip_image_embedding(img_path)
            all_texture_paths.append(img_path)
            all_embedings.append(embedding)
            
        all_embedings=np.array(all_embedings)
        np.savez('assets/texture_embeddings.npz',embeddings=all_embedings, paths=all_texture_paths)

        self.embeddings = all_embedings
        self.paths = all_texture_paths
        
    def find_texture(self):
        text_embd = clip_text_embedding(self.texture)
        sims = self.embeddings@text_embd[...,None]
        indices = np.argsort(sims[:,0])[-1]
        path = os.path.join(self.textures_path, self.paths[indices])
        return path
    
    def assign_texture(self, mesh):
        texture_path = self.find_texture()
        texture_image = Image.open(texture_path)
        uv_coordinates = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
        mesh.visual = trimesh.visual.TextureVisuals(uv=uv_coordinates, image=texture_image)
        mesh.visual.uv = mesh.visual.uv * self.res
            
    def build(self):
        mesh = self.create()
        self.assign_texture(mesh)
        return mesh
    
class Floor(TexturedWall):
    def __init__(self, scene, texture='wood'):
        super().__init__(scene, texture)
        self.texture = texture
        self.name = 'floor'
        
    def create(self):
        vertices = np.array([
            [0, 0, 0],
            [self.scene.MAX_WIDTH, 0, 0],
            [self.scene.MAX_WIDTH, 0 , self.scene.MAX_DEPTH],
            [0, 0, self.scene.MAX_DEPTH]
        ])
        
        faces = np.array([
            [0, 2, 1],
            [0, 3, 2]
        ])
        
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        return mesh
    
class Ceiling(TexturedWall):
    def __init__(self, scene, texture='white'):
        super().__init__(scene, texture)
        self.texture = texture
        self.name = 'ceiling'
        
    def create(self):
        vertices = np.array([
            [0, self.scene.MAX_HEIGHT, 0],
            [self.scene.MAX_WIDTH, self.scene.MAX_HEIGHT, 0],
            [self.scene.MAX_WIDTH, self.scene.MAX_HEIGHT , self.scene.MAX_DEPTH],
            [0, self.scene.MAX_HEIGHT, self.scene.MAX_DEPTH]
        ])
        
        faces = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ])
        
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        return mesh
    
