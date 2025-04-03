import numpy as np 
import pickle
class OrientationManager:
    def __init__(self):
        self.scene_path = 'cache/scene.pkl'
        with open(self.scene_path, 'rb') as f:
            self.scene_data = pickle.load(f)
            
        self.placements = self.scene_data['placements']
        self.issues = ""
    def conversation_area(self, list_of_objects):
        
        for i in range(len(list_of_objects)):
            for j in range(i+1, len(list_of_objects)):
                obj1 = list_of_objects[i]
                obj2 = list_of_objects[j]
                __obj1 = obj1
                __obj2 = obj2
                obj1 = self.placements[obj1]
                obj2 = self.placements[obj2]
                
                vec = obj2[0] - obj1[0]
                vec = vec/np.linalg.norm(vec)
                angle = obj1[1].dot(vec)
                
                if angle < 0:
                    self.issues += f"Objects: {__obj1} and {__obj2} are not oriented such that they facilitate conversation.\n"
                    self.save()
                    
    def face_towards(self, obj, target):
        __obj = obj
        __target = target
        obj = self.placements[obj]
        target = self.placements[target]
                                 
        vec = target[0] - obj[0]
        vec = vec/np.linalg.norm(vec)
        angle = vec.dot(obj[1])
        if angle < 0.5:
            self.issues += f"Object: {__obj} is not facing towards the target: {__target}.\n"
            self.save()
            
    def save(self):
        with open('tmp/orientation_issues.txt', 'w') as f:
            f.write(self.issues)
