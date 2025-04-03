from modules.progsyn import ProgramSynthesizer  
from modules.optimizer import SceneOptimizer
from modules.utils.codegen import CodeExecutor
import os

class SceneProg:
    def __init__(self):
        self.scene_pickle_path = 'cache/scene.pkl'
        self.program_path = 'cache/program.py'
        self.input_path = 'cache/input.txt'
        
        self.clean()
        self.proggen = ProgramSynthesizer()
        self.optimizer = SceneOptimizer()
        self.exec = CodeExecutor()
 
    def clean(self):
        if os.path.exists(self.scene_pickle_path):
            os.remove(self.scene_pickle_path)
        if os.path.exists(self.program_path):
            os.remove(self.program_path)
        if os.path.exists(self.input_path):
            os.remove(self.input_path)
        if os.path.exists('cache'):
            os.system('rm -r cache')
        if os.path.exists('tmp'):
            os.system('rm -r tmp')
        if os.path.exists('csr.pkl'):
            os.remove('csr.pkl')
        if os.path.exists('output'):
            os.system('rm -r output')
            
        os.makedirs('tmp/')
        with open('tmp/object_scale.txt', 'w') as f:
            f.write('Irrespective of what you think, you must use the following scales for the below mentioned objects')
        os.makedirs('cache')
        
    def run(self, input, output_path='output'):
        with open(self.input_path, 'w') as f:
            f.write(input)
        
        self.proggen.run(input)
        self.optimizer.run("Optimize the scene. ")
        
        with open(self.program_path, 'r') as f:
            program = f.read()
        print("Exporting scene...")
        self.exec.run(program+"\nscene.export()")