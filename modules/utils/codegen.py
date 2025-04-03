import os
import random
from tqdm import tqdm
from tools.llm import LLM

class CodeExecutor:
    def __init__(self):
        self.temp_dir = 'tmp/'
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
        self.header = """
import sys
sys.path.append('/Users/kunalgupta/Documents/sceneprog/')
import warnings
warnings.filterwarnings("ignore")
from tqdm import tqdm
from modules.sdl.scene import Scene       
from modules.optimizer_tools.constraints import Constraints 
"""
    def run(self, code):
        
        rand_id = random.randint(0, 100000)

        with open(f"{self.temp_dir}{rand_id}.py", 'w') as f:
            f.write(self.header+code)
        
        os.system(f'python {self.temp_dir}{rand_id}.py 2> {self.temp_dir}{rand_id}.out')
        
        with open(f"{self.temp_dir}{rand_id}.out", 'r') as f:
            reply = f.read()
        
        os.system(f'rm {self.temp_dir}{rand_id}.py')
        os.system(f'rm {self.temp_dir}{rand_id}.out')
        
        return reply
    
class CodeDebugger:
    def __init__(self):
        self.exec = CodeExecutor().run
        
        with open('rag/scene_api.py', 'r') as f:
            self.apis = f.read()
            
        self.llm_debugger = LLM(system_desc=f"""
You should go through the code and find syntax errors including those caused by wrong use of the API. Please refer to the API documentation:\n{self.apis}. 
First identify the errors and then respond with the corrected code. You should also pay attention to the exteptions raised while running the code and find ways to fix them. 
You are not supposed to change placement values or settings in the code, but only watch out for reasons due to which the code may crash! Lastly, do not save or export the scene, I will do that myself later.
Also, you don't have to worry about importing modules. They are already imported for you.
""", response_format='code')
        self.debugger = LLM(system_desc=f"""You are a large language model based assistant, expert at designing layouts for indoor scenes. At the same time, you are also expert at debugging codes related to layout designs.
You should only respond with code that is correct and does not have any errors. Feel free to fix any other issues that you think may exist in the code by refering to API documentation:\n{self.apis}.  You should also pay attention to the exteptions raised while running the code and find ways to fix them. Think step by step. You are not supposed to change placement values or settings in the code, but only watch out for reasons due to which the code may crash!
Lastly, do not save or export the scene, I will do that myself later.
Also, you don't have to worry about importing modules. They are already imported for you.
""", response_format='code')
        self.checker = LLM(system_desc="You are supposed to go through the stdout and respond whether there are any errors or not. In case you don't see any errors (ignore warnings!) respond in a JSON format with 'errors': False. Else, respond with 'errors': True.", response_format='json')

    def run(self, code, save_string=""):
        code = self.llm_debugger.run(code)
        errors = self.exec(code+save_string)
        import time
        print("Debugging code...")
        with tqdm(total=5, desc="Debugging Attempts") as pbar:
            for attempt in range(5):
                # Animated dots indicating debugging in progress
                for frame in ["   ", ".  ", ".. ", "...", ".. ", ".  ", "   "]:
                    print(f"\rAttempt {attempt + 1}/5{frame}", end="")
                    time.sleep(0.2)
                
                if self.checker.run(errors)['errors']:
                    breakpoint()
                    prompt = f"Input: {code}.\nErrors: {errors}.\nDebugged code:"
                    code = self.debugger.run(prompt)
                    code = self.llm_debugger.run(code)
                    errors = self.exec(code+save_string)
                    pbar.update(1)  # Update progress bar for each attempt
                else:
                    print("\nDebugging completed successfully!")
                    break
                
                print("\r  ", end="")  # Clear line after each attempt

        print("\nDebugging cycle finished.")
        return code
