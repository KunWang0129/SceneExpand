from modules.sdl.object import Object3D
from tools.simpleagent import SimpleAgent
import trimesh
import numpy as np
from tools.dataset import AssetRetriever
import bentoml
from tools.llm import LLM
import os
import random
import json
from tools.text2img import text2img
from PIL import Image, ImageEnhance, ImageDraw

from pydantic import BaseModel, Field
from typing import Optional, Annotated

FUTURE_MODEL_PATH = "/Users/kunalgupta/Documents/datasets/3D-FUTURE-model/"


class ModelDescription(BaseModel):
    desc: Annotated[str, Field(..., description="Description of the 3D asset")]

class RetrievedModelPath(BaseModel):
    path: Optional[str] = Field(None, description="Path to the retrieved 3D model file")

class ModelSize(BaseModel):
    size: Optional[str] = Field(None, description="Size of the 3D model, e.g. small, medium, large")
    
def retrieve_3dfront(desc: Annotated[ModelDescription, "Description of the 3D asset"]) -> RetrievedModelPath:
    try:
        obj = AssetRetriever().run(desc.desc)
    except:
        try:
            obj = AssetRetriever().run(desc.desc)
        except:
            obj = AssetRetriever().run(desc.desc)
    if not obj:
        return RetrievedModelPath(path="Not found")
    dataset_path = FUTURE_MODEL_PATH
    return RetrievedModelPath(path=dataset_path + obj + '/normalized_model.obj')

def retrieve_objaverse(desc: Annotated[ModelDescription, "Description of the 3D asset"]) -> RetrievedModelPath:
    with bentoml.SyncHTTPClient('http://chetak.ucsd.edu:3001') as client:
        result: str = client.retrieve([desc.desc])[0]
    
    if result == '**':
        return RetrievedModelPath(path="Not found")
    assetID, bbox = result.split('|')

    return RetrievedModelPath(path='objaverse/'+assetID)

def retrieve_painting(desc: Annotated[ModelDescription, "Description of the 3D asset"]) -> RetrievedModelPath:
    painting = Painting(desc.desc)
    id = random.randint(0,100000)
    painting.mesh.export('tmp/painting_'+str(id)+'.glb')
    return RetrievedModelPath(path='tmp/painting_'+str(id)+'.glb')

def retrieve_area_rug() -> RetrievedModelPath:
    rugs_path = 'assets/additional_assets/rugs'
    rugs = os.listdir(rugs_path)
    rug = random.choice(rugs)
    path = rugs_path+'/'+rug+'/'+'normalized_model.glb'
    return RetrievedModelPath(path=path)

def retrieve_wall_clock() -> RetrievedModelPath:
    clock_path = 'assets/additional_assets/clock.obj'
    return RetrievedModelPath(path=clock_path)

class Painting:
    def __init__(self, desc):
        self.canvas_path = 'assets/additional_assets/canvas.obj'
        self.canvas = trimesh.load(self.canvas_path, force='mesh',process=False)
        
        vertices = self.canvas.vertices
        vertices -= np.min(vertices, axis=0)
        max_vals = np.max(vertices, axis=0)
        vertices /= np.array([max_vals[0], max_vals[1], 1])
        vertices[:,0] *= 1.0
        vertices[:,1] *= 1.0
        
        desc = LLM(system_desc="Given the request prompt, you are supposed to give a one line desciption to be fed to a text to image generator model. DO NOT write lengthy descriptions!", response_format="text", single_use=True).run(desc)
        texture = text2img(desc)
        texture = texture.transpose(Image.ROTATE_90)
        texture = texture.transpose(Image.ROTATE_90)
        texture = texture.transpose(Image.FLIP_TOP_BOTTOM)
        
        texture = self.resize_image(texture, 512, 512)
        
        uv_coordinates = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        
        self.canvas.visual = trimesh.visual.TextureVisuals(uv=uv_coordinates, image=texture)
        self.mesh_visual = self.canvas.visual
        
        picture_window_path = 'assets/additional_assets/window_tofloor.obj'
        frame = trimesh.load(picture_window_path, force='mesh',process=False)
        vertices = frame.vertices
        
        vertices -= np.min(vertices, axis=0)
        vertices /= np.max(vertices, axis=0)
        vertices[:,0] *= 1.0
        vertices[:,1] *= 1.0
        vertices[:,-1] *= 0.05
        
        frame = trimesh.Trimesh(vertices=vertices, faces=frame.faces, process=False)  
        
        self.mesh = trimesh.util.concatenate([self.canvas, frame])
        self.mesh_visual = self.mesh.visual
        
        self.width = 1.0
        self.height = 1.0
        self.depth = 0.02
        
        vertices = self.mesh.vertices
        vertices -= np.mean(vertices, axis=0)
        
    def resize_image(self, texture, width, height):

        # Step 1: Calculate the New Size
        aspect_ratio = texture.width / texture.height
        if width / height > aspect_ratio:
            # Image is limited by height, so scale height to fit and adjust width accordingly
            new_height = height
            new_width = int(aspect_ratio * height)
        else:
            # Image is limited by width, so scale width to fit and adjust height accordingly
            new_width = width
            new_height = int(width / aspect_ratio)

        # Step 2: Resize the Image
        texture_resized = texture.resize((new_width, new_height), Image.LANCZOS)

        # Step 3: Create a Background Canvas (assuming a white background, change as needed)
        canvas = Image.new('RGB', (width, height), 'black')

        # Step 4: Paste the Image onto the Canvas
        x_offset = (width - new_width) // 2
        y_offset = (height - new_height) // 2
        canvas.paste(texture_resized, (x_offset, y_offset))

        # Apply any additional transformations like rotation or flipping
        canvas = canvas.transpose(Image.ROTATE_90)
        canvas = canvas.transpose(Image.FLIP_TOP_BOTTOM)

        # Enhance brightness
        enhancer = ImageEnhance.Brightness(canvas)
        texture_final = enhancer.enhance(1.5)

        return texture_final
        
        
class ObjectDatabase:
    def __init__(self):
        self.retriever = SimpleAgent('retriever', role="Checks for the availability of the object in the database", description="""You are an agent that checks for the availability of the objects in the database. \
            You should intelligently select the right tool in order to retrieve the object correctly.  
            Following are some guidelines on when to use a particular function. 
            Firstly, for indoor furniture such as sofa, bed, cabinets, lamps, chandiliers, plants, lamps and decor etc you can use the retrieve_3dfront function. 
            Rest, you can use the retrieve_objaverse function to get the 3D models of the items. For wall art/paintings/2D images, use the retrieve_painting function. 
            For specific assets like area rugs and wall clocks, you can use the respective functions.
            Note that you should call the tool seperately for each object, the tools cannot output multiple objects at once.
            """,
            concluding_llm = LLM(single_use=True, system_desc="You should go through the chat and return a JSON file for each object mentioning whether the said object is available or not. Example response can be like objname:No, objname:Yes", response_format="json",),
            context=None)

        self.retriever.add_tool(retrieve_3dfront, "retrieve_3dfront", "Retrieve 3D models of items, primarily indoor furniture")
        self.retriever.add_tool(retrieve_painting, "retrieve_painting", "Retrieve 3D models of wall art/paintings/2D images")
        self.retriever.add_tool(retrieve_area_rug, "retrieve_area_rug", "Retrieve 3D models of area rugs")
        self.retriever.add_tool(retrieve_wall_clock, "retrieve_wall_clock", "Retrieve 3D models of wall clocks")
        self.retriever.add_tool(retrieve_objaverse, "retrieve_objaverse", "Last resort for retrieving 3D models of items")
    
    def run(self, desc: str):
        return self.retriever.respond(desc)
    
    
class Object3DRetriever:
    def __init__(self):
        self.retriever = SimpleAgent('retriever', role="Retrieve path for 3D assets", description="""You are an agent that returns the path for 3D assets based on the user input. \
            You should intelligently select the right tool in order to retrieve the object correctly. 
            Following are some guidelines on when to use a particular function. 
            Firstly, for indoor furniture such as sofa, bed, cabinets, lamps, chandiliers, plants, lamps and decor etc, you can use the retrieve_3dfront function. Rest, you can use the retrieve_objaverse function to get the 3D models of the items. For wall art/paintings/2D images, use the retrieve_painting function. 
            For specific assets like area rugs and wall clocks, you can use the respective functions.
            In case you are unable to find the object, try using some other tool.
    Following are some example descriptions:
    'A low-profile, rectangular, glass coffee table'
    'A chair'
    'A large vase with flowers'
    'A small end table'
    'A simple two seater sofa'
    'Modern armchair in a light cream color'
    'A small but wide cabinet'
    'A beautiful painting of a horse'
    'A gaming laptop'
    """, 
    concluding_llm = LLM(single_use=True, system_desc="You should go through the chat and return the path of the 3D object as a JSON object. example response can be like path:<put path here>", response_format="json",json_keys=['path']),
    context=None)
        self.retriever.add_tool(retrieve_3dfront, "retrieve_3dfront", "Retrieve 3D models of items, primarily indoor furniture")
        self.retriever.add_tool(retrieve_painting, "retrieve_painting", "Retrieve 3D models of wall art/paintings/2D images")
        self.retriever.add_tool(retrieve_area_rug, "retrieve_area_rug", "Retrieve 3D models of area rugs")
        self.retriever.add_tool(retrieve_wall_clock, "retrieve_wall_clock", "Retrieve 3D models of wall clocks")
        self.retriever.add_tool(retrieve_objaverse, "retrieve_objaverse", "Last resort for retrieving 3D models of items")
    
    def run(self, desc: str):
        return self.retriever.respond(desc)['path']

        
        