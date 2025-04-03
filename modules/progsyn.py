import os
import numpy as np
from tqdm import tqdm
from tools.llm import LLM
from assets.llm_config import LLM_CONFIG
from langchain_openai import OpenAIEmbeddings
from modules.utils.codegen import CodeDebugger

OVERALL_TEMPLATE = """You are part of a system that designs layouts for interior spaces. The scene is contained within a prisim with four walls plus the floor and ceiling. The four walls are called the left_wall, right_wall, front_wall and back_wall. """

class ProgramSynthesizer: 
    def __init__(self):
        self.scene_pickle_path = 'cache/scene.pkl'
        self.program_path = 'cache/program.py'
        self.input_path = 'cache/input.txt'
        
        self.topk=5
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=LLM_CONFIG['api_key'])
        description=OVERALL_TEMPLATE+"Given the input query, write a scene program"
        self.llm = LLM(system_desc=description, response_format="code")
        self.debugger = CodeDebugger()
        
        self.layout_draft = LLM(system_desc="Given the input, generate a brief layout of the various objects in the scene.", response_format="text")
        self.ref = 'rag/generator.py'
        with open(self.ref, 'r') as f:
            self.reference_code = f.read()
            
        with open('rag/scene_api.py', 'r') as f:
            self.apis = f.read()
        
        self.SCENE_SAVE = """
scene.save()        
"""     
        self.CSR_SAVE = """
csr.save()
scene.save()
"""
    def save_program(self, program):
        with open(self.program_path, 'w') as f:
            f.write(program)
            
    def extract_header_and_code(self):
        
        if os.path.exists('assets/code_embds.npz'):
            data = np.load('assets/code_embds.npz')
            return data['embds'], data['headers'], data['codes'], data['constraints']
        
        parts = self.reference_code.split('##@##')[1:]
        headers = []
        codes = []
        embds = []
        constraints = []
        for i in tqdm(range(len(parts))):
            if i % 2 == 0:
                header = parts[i]
                headers.append(header)
                embds.append(self.embeddings.embed_query(header))
            else:
                prog = parts[i].split('##$##')
                code = prog[0]
                const = prog[1]
                codes.append(code)
                constraints.append(const)
                
        embds = np.array(embds)
        np.savez('assets/code_embds.npz', embds=embds, headers=headers, codes=codes, constraints=constraints)
        
        return embds, headers, codes, constraints

    def retrieve_context(self, input):
        embd = self.embeddings.embed_query(input)
        embds, headers, codes, constraints = self.extract_header_and_code()
        import numpy as np
        similarities = np.dot(embd, embds.T)
        most_similar = np.argsort(similarities)[::-1][:self.topk]
        context = ""
        for idx in most_similar:
            context += "\n"+headers[idx] + "\n"+codes[idx]
        
        context_with_constraints = ""
        for idx in most_similar:
            context_with_constraints += "\n"+headers[idx] + "\n"+codes[idx] + "\n"+constraints[idx]
        
        return context, context_with_constraints
    
    def run_refine(self, input, program, context, query):
        prompt = f"""
You are supposed to modify the scene program that was generated in the previous step based on the input. Use the context provided to you make the necessary changes to the scene program as per the user query. 
You may refer to the API documentation:
{self.apis}
Input: {input}
Scene Program:
{program}
Context:
{context}
Now make the necessary modifications to the scene program based on the user query by using the context provided above. Only return the modified scene program.
User Query: {query}
Your response:
"""
        program = self.llm.run(prompt)
        debugged_program = self.debugger.run(program, save_string=self.SCENE_SAVE)
        self.save_program(debugged_program)
    
    def run(self, input):
        layout_draft = self.layout_draft.run(input)
        context,_ = self.retrieve_context(layout_draft)
        prompt = f"Input: {input}.\n"
        prompt += f"Initial layout draft:\n{layout_draft}\n"
        prompt += f"Use the following examples to generate the scene program based on the input. An initial draft of the layout is provided to you which may come handy. Only return the scene program.\nYou can refer to the following examples to understand how to write a scene program. However, they are provided only to give you an idea, you should avoid directly outputting the included examples. Try to be original! Examples:\n{context}\nYou may refer to the API documentation:\n{self.apis}\n"
        prompt += """
Following are some additional guidelines to keep in mind while generating the scene program:
1. Remember to set the orientation of the objects in the scene to ensure that they are facing the correct direction. Objects can be oriented both towards other objects or towards on of the four walls. For example, if some chairs or couches form a conversation area, then they should be oriented like that. In a desk-chair setup, the chair should be facing towards the table. 
There maybe other rationals for the orientation of the objects in the scene, so use your best judgement to correct the orientation of the objects in the scene. 
Hint: by setting the face_towards parameter in the place_global and place_relative methods you can set the orientations.
2. Make sure that you don't place such that objects are overlapping or out of bounds. This can be done by placing unrelated set of objects in different parts of the scene. For example, in a bedroom, the (bedroom,nightstands) set can be placed in one part of the room and the (desk, chair) can be placed in another part of the room.
3. When using for loops to place objects, make sure that you don't miss out on any object. For example, if you are placing chairs around a dining table, make sure that you place all the chairs around the table.

NOTE: Only generate the scene program, do not write the constraints here. You will be asked to write the constraints in the next step. Do not save or export the scene, I will do that myself later.
"""
        program = self.llm.run(prompt)
        
        debugged_program = self.debugger.run(program, save_string=self.SCENE_SAVE)
        self.save_program(debugged_program)
        
    def run_with_constraints(self, input, program):
        _,context = self.retrieve_context(self.layout_draft.run(input))
        prompt = f"Input: {input}.\n"
        prompt += f"Scene program:\n{program}\n"
        prompt += f"Have a look at how to write constraints given a scene program.Examples:\n{context}\nOnly return the constraints. You may refer to the API documentation:\n{self.apis}\n"
        constraints = self.llm.run(prompt)
        
        result = """
csr = Constraints(scene)
for i in tqdm(range(100)):
    csr.init_grads()
"""
        for constraint in constraints.split('\n'):
            result += f"""
    {constraint}"""

        result += f"""
    end = csr.update()
    if end:
        break
"""
        result = f"""
{program}
{result}        
"""
        debugged_program = self.debugger.run(result, save_string=self.CSR_SAVE)
        self.save_program(debugged_program)