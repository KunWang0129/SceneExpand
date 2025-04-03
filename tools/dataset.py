from tools.llm import LLM
import json
from tqdm import tqdm 
import random
import os
from langchain_openai import OpenAIEmbeddings
from assets.llm_config import LLM_CONFIG    
import numpy as np
import trimesh

CATEGORIES=['null','armchair', 'Lounge Chair / Cafe Chair / Office Chair', 'Pendant Lamp', 'Coffee Table', 'Corner/Side Table', 'Dining Table', 'King-size Bed', 'Nightstand', 'Bookcase / jewelry Armoire', 'Three-Seat / Multi-seat Sofa', 'TV Stand', 'Drawer Chest / Corner cabinet', 'Shelf', 'Wardrobe', 'Footstool / Sofastool / Bed End Stool / Stool', 'Sideboard / Side Cabinet / Console Table', 'Ceiling Lamp', 'Children Cabinet', 'Bed Frame', 'Round End Table', 'Desk', 'Single bed', 'Loveseat Sofa', 'Dining Chair', 'Barstool', 'Lazy Sofa', 'L-shaped Sofa', 'Wine Cabinet', 'Dressing Table', 'Dressing Chair', 'Kids Bed', 'Classic Chinese Chair', 'Bunk Bed', 'Chaise Longue Sofa', 'Lounge Chair / Book-chair / Computer Chair', 'Sideboard / Side Cabinet / Console', 'Bar', 'Three-Seat / Multi-person sofa', 'Double Bed', 'Shoe Cabinet', 'Couch Bed', 'Wine Cooler', 'Tea Table', 'Hanging Chair', 'Folding chair', 'U-shaped Sofa', 'Two-seat Sofa', 'Floor Lamp', 'Wall Lamp']
FUTURE_MODEL_PATH = "/Users/kunalgupta/Documents/datasets/3D-FUTURE-model/"
cat2num={
    'null': 100,
    'armchair': 25,
    'Lounge Chair / Cafe Chair / Office Chair': 25,
    'Pendant Lamp': 25,
    'Coffee Table': 25,
    'Corner/Side Table': 25,
    'Dining Table': 25,
    'King-size Bed': 25,
    'Nightstand': 25,
    'Bookcase / jewelry Armoire': 25,
    'Three-Seat / Multi-seat Sofa': 25,
    'TV Stand': 15,
    'Drawer Chest / Corner cabinet': 15,
    'Shelf': 15,
    'Wardrobe': 15,
    'Footstool / Sofastool / Bed End Stool / Stool': 15,
    'Sideboard / Side Cabinet / Console Table': 15,
    'Ceiling Lamp': 10,
    'Children Cabinet': 10,
    'Bed Frame': 10,
    'Round End Table': 15,
    'Desk': 15,
    'Single bed': 15,
    'Loveseat Sofa': 10,
    'Dining Chair': 10,
    'Barstool': 10,
    'Lazy Sofa': 0,
    'L-shaped Sofa': 10,
    'Wine Cabinet': 10,
    'Dressing Table': 10,
    'Dressing Chair': 10,
    'Kids Bed': 10,
    'Classic Chinese Chair': 10,
    'Bunk Bed': 10,
    'Chaise Longue Sofa': 10,
    'Lounge Chair / Book-chair / Computer Chair': 50,
    'Sideboard / Side Cabinet / Console': 50,
    'Bar': 5,
    'Three-Seat / Multi-person sofa': 0,
    'Double Bed': 0,
    'Shoe Cabinet': 10,
    'Couch Bed': 10,
    'Wine Cooler': 0,
    'Tea Table': 0,
    'Hanging Chair': 10,
    'Folding chair': 0,
    'U-shaped Sofa': 10,
    'Two-seat Sofa': 10,
    'Floor Lamp': 50,
    'Wall Lamp': 2,
}

class AssetRetriever:
    def __init__(self):
        
        if not os.path.exists('assets/cat2model.json'):
            with open(FUTURE_MODEL_PATH+'model_info.json','r') as file:
                model_info = json.load(file)
                
            cat2model = {}
            for model in model_info:
                if model['category'] not in cat2model:
                    cat2model[model['category']] = []
                cat2model[model['category']].append(model['model_id'])
                        
            for cat in CATEGORIES:
                random.shuffle(cat2model[cat])

            with open('assets/cat2model.json','w') as file:
                json.dump(cat2model, file)
        
        else:
            with open('assets/cat2model.json','r') as file:
                cat2model = json.load(file)

        self.cat2model = cat2model
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=LLM_CONFIG['api_key'])
        
        if not os.path.exists('assets/embeddings.npz'):
            self.build()
        
        data = np.load('assets/embeddings.npz')
        self.all_embeddings = data['all_embeddings']
        self.all_models = data['all_models']
        self.all_ratios = data['all_ratios']    
        
    def build_descs(self):
        system_desc="""
        Respond with in a JSON format containing a one line description of the main object present in the image as well as identifying whether there are any other artifacts/smaller items/decor present in the image other than the main object.
        You should pay attention to the objects broad categery i.e. armchair, sofa, etc as well as its color - red, blue, orange, material - leather, wooded, stye - minimalist, modern. 
        A typical output should like like: {{"caption": "Chic nesting coffee tables with gold frames and white marble tops, adding a touch of luxury and versatility to any living space.", "details":True}}.
        """
        myllm = LLM(system_desc=system_desc, image_input=True, response_format="json")

        if os.path.exists('assets/model2description.json'):
            with open('assets/model2description.json','r') as file:
                MODEL_TO_DESCRIPTION = json.load(file)
        else:
            MODEL_TO_DESCRIPTION = {}

        MAX_ATTEMPTS = 100

        for cat in CATEGORIES:
            target_number = cat2num[cat]
            print("Doing for ", cat)
            
            for i in tqdm(range(cat2num[cat])):
                
                model = self.cat2model[cat][i]   
                if model in MODEL_TO_DESCRIPTION:
                    target_number -= 1
                    continue
                image_path = FUTURE_MODEL_PATH + model + '/image.jpg'
                result = myllm.run("Describe this image", image_path=image_path)
                if result['details']:
                    continue
                elif result['caption'] in MODEL_TO_DESCRIPTION.values():
                    continue
                else:
                    MODEL_TO_DESCRIPTION[model] = result['caption']
                    target_number -= 1

                with open('assets/model2description.json','w') as file:
                    json.dump(MODEL_TO_DESCRIPTION, file)
                
                if target_number == 0 or i == MAX_ATTEMPTS:
                    break
        
        self.MODEL_TO_DESCRIPTION = MODEL_TO_DESCRIPTION
        
    def build(self):
        if os.path.exists('assets/model2description.json'):
            with open('assets/model2description.json','r') as file:
                self.MODEL_TO_DESCRIPTION = json.load(file)
        else:
            self.build_descs()
            
        from_scratch=True
        if os.path.exists('assets/embeddings.npz'):
            data = np.load('assets/embeddings.npz')
            all_embeddings = data['all_embeddings']
            all_models = data['all_models'].tolist()
            all_ratios = data['all_ratios']
            from_scratch=False
            
        else:        
            all_embeddings = []
            all_models = []
            all_ratios = []

        for model, desc in tqdm(self.MODEL_TO_DESCRIPTION.items()):
            if model in all_models:
                continue
            path = FUTURE_MODEL_PATH + model + '/normalized_model.obj'
            mesh = trimesh.load(path, process=False, force='mesh')
            
            bounds = mesh.bounds
            width = bounds[1,0] - bounds[0,0]
            depth = bounds[1,2] - bounds[0,2]
            height = bounds[1,1] - bounds[0,1]
            x0 = depth/width
            y0 = height/width
            
            emb = np.array(self.embeddings.embed_query(desc))
            all_models.append(model)
            if from_scratch:
                all_ratios.append(np.array([x0, y0]))
                all_embeddings.append(emb)
                
            else:
                all_ratios = np.vstack((all_ratios, np.array([x0, y0])))
                all_embeddings = np.vstack((all_embeddings, emb))
            
        np.savez('assets/embeddings.npz', all_embeddings=all_embeddings, all_models=all_models, all_ratios=all_ratios)
        
    def compute_ratio_sim(self, query):
        dims = ScaleObj().run(query)
        w,d,h = dims['width'], dims['depth'], dims['height']
        x0 = d/w
        y0 = h/w
        target_ratio = np.array([x0, y0])
        ratio_sim = -np.linalg.norm(self.all_ratios - target_ratio, axis=1)
        return ratio_sim
    
    def run(self, query):
        emb = np.array(self.embeddings.embed_query(query))
        similarity = np.dot(self.all_embeddings, emb)
        ratio_sim = self.compute_ratio_sim(query)
        
        score = similarity + 0.045*ratio_sim  ## above 0.05, ratio_sim tends to dominate
        best_match_index = np.argmax(score)
        
        model = self.all_models[best_match_index]
        
        # path = FUTURE_MODEL_PATH + model + '/image.jpg'
        # os.system(f'cp {path} image.jpg')
        return model
    
class ScaleObj:
    def __init__(self):
        from tools.llm import LLM
        self.llm = LLM(system_desc="You are a large language model based assistant, your job is to scale the object to the given dimensions. You only answer in the way following examples do. Anyother type of response is strictly forbidden. Return the values in meters.")
        self.reset()
        os.makedirs('tmp/', exist_ok=True)
        
    def reset(self):
        self.prompt = """
User Input: A dining chair
Your Response: ```{''height'':1.0, 'width':0.5, 'depth':0.5}```
User Input: A king-size bed
Your Response: ```{'height':1.5, 'width':2.0, 'depth':2.1}```
User Input: A armchair
Your Response: ```{'height':1.0, 'width':0.9, 'depth':0.95}```
User Input: A coffee table
Your Response: ```{'height':0.6, 'width':1.0, 'depth':1.0}```
User Input: A really long dining table
Your Response: ```{'height':0.7, 'width':8.0, 'depth':3.0}```
User Input: A tall bookcase
Your Response: ```{'height':2.5, 'width':1.0, 'depth':0.5}```
User Input: A small nightstand
Your Response: ```{'height':0.5, 'width':0.5, 'depth':0.5}```
User Input: A large Chandelier
Your Response: ```{'height':0.8, 'width':0.5, 'depth':0.5}```
"""
    def run(self, query):
        self.prompt = f"{self.prompt}\n. User Input: {query}\n"
        self.prompt += "Your response:"
        return self._sanitize_output(self.llm.run(self.prompt))
    
    def _sanitize_output(self, text: str):
        import ast
        return ast.literal_eval(str(text.split("```")[1]))
