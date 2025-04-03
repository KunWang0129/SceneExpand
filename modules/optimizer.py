import os
import json
import random
import numpy as np
import pickle
from tools.llm import LLM
from tools.simpleagent import SimpleAgent
from modules.progsyn import ProgramSynthesizer
from modules.utils.codegen import CodeExecutor

from pydantic import BaseModel, Field
from typing import Optional

class FunctionResult(BaseModel):
    status: str = Field(..., description="Summary of the function's execution outcome.")
    details: Optional[str] = Field(None, description="Additional details or issues, if any.")
    
class OptimizationTool:
    def __init__(self, reuse_state=False):
        self.scene_path = 'cache/scene.pkl'
        self.program_path = 'cache/program.py'
        self.input_path = 'cache/input.txt'
        self.reuse_state = reuse_state
        self.progsyn = ProgramSynthesizer()
        self.exec = CodeExecutor().run
        
    def load_input(self):
        with open(self.input_path, 'r') as f:
            self.input = f.read()
            
    def load_program(self):
        with open(self.program_path, 'r') as f:
            self.program = f.read()
        
    def load_meta_data(self):
        with open(self.scene_path, 'rb') as f:
            self.scene_data = pickle.load(f)
        
        self.sg = self.scene_data['sg']
        self.dims = self.scene_data['dims']
        self.weights = self.scene_data['weights']
        self.wall_occ = self.scene_data['wall_occ']
        
    def compute_state(self):
        self.exec(self.program+self.progsyn.SCENE_SAVE)
        self.load_meta_data()
    
    def load(self):
        self.load_input()
        self.load_program()
        if not self.reuse_state:
            self.compute_state()
            
        try:
            self.load_meta_data()
        except:
            self.compute_state()
            self.load_meta_data()
        
def resolve_wall_overlap() -> FunctionResult:
    tool = OptimizationTool()
    tool.load()
    
    wall_occ = tool.wall_occ
    
    issues = ""
    for wall in ['back_wall', 'left_wall', 'right_wall', 'front_wall']:
        left = wall_occ[wall]['left']
        right = wall_occ[wall]['right']
        middle = wall_occ[wall]['middle']
        
        if len(left) > 1:
            issues += f"Multiple objects: {wall_occ[wall]['left']} placed in the left side of {wall}.\n"
        if len(right) > 1:
            issues += f"Multiple objects: {wall_occ[wall]['right']} placed in the right side of {wall}.\n"
        if len(middle) > 1:
            issues += f"Multiple objects: {wall_occ[wall]['middle']} placed in the middle of {wall}.\n"
        
    if issues == "":
        return tool.program
    
    print("Resolving wall overlap...")
    
    query = """
There can be only one object occupying a side of the wall i.e. at most one object can be placed on the left, right and middle side of a wall. Windows that are 'full' occupy all three sides of the wall.    
Think about rearranging the objects on the wall (including location of windows, doors, etc) to resolve the issues. 
"""
    tool.progsyn.run_refine(tool.input, tool.program, issues, query)
    
    return FunctionResult(status="Solved")
    
def resolve_relative_scale() -> FunctionResult:
    tool = OptimizationTool(reuse_state=True)
    tool.load()
    
    input = tool.input
    program = tool.program
    scene_graph = tool.sg
    dims = tool.dims
    scene_size = tool.weights['scene']
    
    resolver_llm = LLM(system_desc="""You are responsible for ensuring that the relative scale of objects in the scene is appropriate and realistic, adhearing to factors such as funcionality, ergonomics, asthetics and relative placement of objects.""")
    rel_placement_llm = LLM(system_desc="""Given the scene program, briefly describe the relative placement of the objects mentioned in the input. For example, a lamp placed on a table, a nightstand placed left adjacent to a bed, etc.""")
    scale_determination_llm = LLM(system_desc="""Given the suggested dimensions, output the updated dimensions for all the objects in the order of (width, depth, height) present in the scene program. You can do this by creating a list such as the following:
Your response:
1. chair: 0.5m x 0.5m x 0.5m  (width, depth, height)
2. table: 1m x 1m x 1m
...
""")
    resolutions = ""
    print("Resolving relative scale...")
    for parent in scene_graph.children:
        children = parent.get_all_children()[1]
        if len(children) == 0:
            continue
        prompt = f"""
We are creating a scene for the input: {input}. Whose dimensions (width x depth in meters) are: {scene_size}. 
Following objects along with their dimensions (in meters, in the order width, height, depth) have been identified: 
Parent Object: {parent}. Dimensions: {dims[parent.name]}.
"""
        for child in children:
            prompt += f"""
Child Object: {child}. Dimensions: {dims[child]}.
"""
        prompt += f"""The relative placement of the objects is as follows:{rel_placement_llm.run("Derive the relative placements for {parent}, {children} from the scene program: " + program)}"""
        prompt += f"""\nDo you think the relative scale of the objects: {parent}, {children} is appropriate? If you think the scales need to be adjusted by a lot, then you should suggest the new dimensions. If you think the scales are already reasonable or maybe only slightly off, then don't suggest any changes for that (you can skip that object).
Moreover, I want you to try to maintain the aspect original aspect ratio as much as possible. Think step by step."""
        resolution = resolver_llm.run(prompt)
        resolutions += resolution + "\n"
    
    prompt = f"Based on the following suggestions: {resolutions}\nPlease generated the updated dimensions for the objects in the scene."
    updated_dims = scale_determination_llm.run(prompt)
    with open('tmp/object_scale.txt', 'a') as f:
        f.write(updated_dims)
        
    return FunctionResult(status="Solved")

def resolve_balance() -> FunctionResult:
    tool = OptimizationTool(reuse_state=True)
    tool.load()
    
    input = tool.input
    program = tool.program
    weights = tool.weights
    W,D = weights['scene']
    buffer = 1.0
    
    left = []
    right = []
    back = []
    front = []
    midline = []
    median = []
    
    for obj in weights['objects']:
        name, loc, area = obj
        if loc[0]<W/2-buffer:
            left.append(name)
        elif loc[0]>W/2+buffer:
            right.append(name)
        else:
            midline.append(name)
        
        if loc[2]<D/2 - buffer:
            back.append(name)
        elif loc[2]>D/2 + buffer:
            front.append(name)
        else:
            median.append(name)
            
    context = f"""
We note that the objects are currently placed in the following manner:
Left half of the scene: {left}
Right half of the scene: {right}
Back half of the scene: {back}
Front half of the scene: {front}
Additionally, following objects seem to lie along the vertical midline (left-right center) of the scene: {midline} and the median (front-back center) of the scene: {median}.
You should think about how to balance the scene by moving objects around and generate the new program accordingly. Note that, it is sufficient if the scene is balanced along one of the left-right or front-back axis.
For scenes with fewer (less than 8) number of objects, balancing along one axis maybe sufficient, for scenes with more objects, you may need to balance along both axis.
If you are happy with the current balance, you can return the same program.
"""        
    query = """
Improve the balance of the scene by moving objects around while maintaining the overall aesthetics and functionality of the scene.
You achieve this by modifying the provided scene program based on the description of objects placed in various parts of the scene. 
"""
    tool.progsyn.run_refine(input, program, context, query)
        
    return FunctionResult(status="Solved")
    
def resolve_scene_scale() -> FunctionResult:
    tool = OptimizationTool(reuse_state=True)
    tool.load()
    
    input = tool.input
    program = tool.program
    weights = tool.weights
    W,D = weights['scene']
    
    total_area = 0
    for obj in weights['objects']:
        total_area +=obj[-1]
    
    occupancy = total_area/(W*D)    
    run=False
    if occupancy < 0.3:
        action = "low, scene dimension must be reduced."
        run=True
    elif occupancy < 0.5:
        action = "moderate, can be left as is."
    else: 
        action = "high, scene dimension must be increased."
        run=True
        
    context = f"""
Occupancy level: {occupancy}, which is {action}
"""
    query = """
Modify the scene program to ensure that the occupancy is appropriate by adjusting the dimensions of the room accordingly. Additionally, also reconsider the height of the scene, does it make sense? Don't forget to update object placements accordingly.
Note that minimum dimensions for the room are 5m x 5m x 3m.
"""
    if run:
        print("Rescaling scene...")
        tool.progsyn.run_refine(input, program, context, query)
    
    return FunctionResult(status="Solved")

def resolve_orientation() -> FunctionResult:
    tool = OptimizationTool(reuse_state=True)
    tool.load()
    
    input = tool.input
    program = tool.program
    
    header = """
import sys
sys.path.append('/Users/kunalgupta/Documents/sceneprog/')
from modules.optimizer_tools.orientation_manager import OrientationManager
om = OrientationManager()
"""
    footer = """
om.save()
"""
    coder_llm = LLM(system_desc="""
Given the input and the scene program, you are supposed to write code to put constraints on the conversation as well as the orientation of seats in the scene.
If you think some seats form a conversation area, then you should add a constraint om.conversation_area([list of seats forming conversation area]). 
If you think a seat should face towards a specific object (such as a chair facing a desk), then you should add a constraint om.face_towards(seat, object). You don't need to add face_towards constraints if you have already added conversation_area constraint for the same objects.
Additionally, orientation constraints should also be added for objects that are supposed to be 'viewed' such as a tv, it should ideally be facing towards on of the prominent seats of all.
You don't need to worry about the object instance om, it is already defined and you just need to call the methods on it.
Some example outputs are:
om.conversation_area(['chair1', 'chair2', 'chair3'])
om.face_towards('chair1', 'table1')
om.face_towards('tv', 'sofa1')
""", response_format='code')
    
    prompt = f"""
Input description: {input}
Scene program: {program}
You need to add constraints to the OrientationManager (already initialized as om) object to ensure that the objects in the scene are oriented correctly and encourage conversation.
"""
    code = coder_llm.run(prompt)
    code = header + code + footer
    with open('tmp/orientation_constraints.py', 'w') as f:
        f.write(code)
    os.system('python tmp/orientation_constraints.py')
    
    with open('tmp/orientation_issues.txt', 'r') as f:
        issues = f.read()
    
    if issues == "":
        return program
    
    print("Resolving orientation issues...")
    context = f"""
The following orientation issues were identified in the scene:
{issues}
"""
    query = """
Given the input, scene program and issues with the orientation of seats and other objects in the scene, you are supposed to modify the scene program to resolve the issues.
"""
    tool.progsyn.run_refine(input, program, context, query)
        
    return FunctionResult(status="Solved")

def resolve_physical_and_ergonomic_issues() -> FunctionResult:
    
    tool = OptimizationTool(reuse_state=False)
    tool.load()
    
    input = tool.input
    program = tool.program
    
    pgen = tool.progsyn
    pgen.run_with_constraints(input, program)
    
    with open('tmp/csr.json', 'r') as f:
        displacement = json.load(f)
    
    print("Resolving ergonomic issues...")
    
    context = f"""
Displacements of the objects: {displacement}
"""
    query = """
Given the input, scene program and displacements of the objects in the scene, you are supposed to modify the scene program so that the objects appear in the updated locations.
"""     
    pgen.run_refine(input, program, context, query)
    
    return FunctionResult(status="Solved")
        
def resolve_greenery() -> FunctionResult:
    # tool = OptimizationTool(reuse_state=True)
    # tool.load_program()
    # tool.load_input()
    # context = ""
    # query = "Do you think the amount of greenery in the scene is sufficient? If not, then add more greenery such as small plants for decor, medium and larger ones which often help make the scene more welcoming and asthetically pleasing."
    # tool.progsyn.run_refine(tool.input, tool.program, context, query)
    
    return FunctionResult(status="Solved")
    
def resolve_storage() -> FunctionResult:
    # tool = OptimizationTool(reuse_state=True)
    # tool.load_program()
    # tool.load_input()
    # context = ""
    # query = "Do you think the amount of storage in the scene is sufficient? If not, then add more storage elements such as shelves, cupboards, etc."
    # tool.progsyn.run_refine(tool.input, tool.program, context, query)
    
    return FunctionResult(status="Solved")
    
def resolve_seating() -> FunctionResult:
    # tool = OptimizationTool(reuse_state=True)
    # tool.load_program()
    # tool.load_input()
    # context = ""
    # query = "Do you think the amount of seating in the scene is sufficient? If not, then add more seating elements such as chairs, sofas, etc."
    # tool.progsyn.run_refine(tool.input, tool.program, context, query)
    
    return FunctionResult(status="Solved")

def resolve_asthetics() -> FunctionResult:
    # tool = OptimizationTool(reuse_state=True)
    # tool.load_program()
    # tool.load_input()
    # context = ""
    # query = "Do you think the scene contains enough elements to make it asthetically pleasing? If not, then add more elements such as decor, paintings, and other interesting elements to the scene."
    # tool.progsyn.run_refine(tool.input, tool.program, context, query)
    
    return FunctionResult(status="Solved")

def resolve_health_and_safety() -> FunctionResult:
    # tool = OptimizationTool(reuse_state=True)
    # tool.load_program()
    # tool.load_input()
    # context = ""
    # query = "Do you think the scene contains enough elements to ensure safety and health of the occupants? If not, then add more elements such as fire extinguishers, first aid kits, etc. Other things to do would be to add signs for emergency exits, etc. You can also ensure that there isn't much clutter around exits. "
    # tool.progsyn.run_refine(tool.input, tool.program, context, query)
    
    return FunctionResult(status="Solved")

def resolve_lighting() -> FunctionResult:
    # tool = OptimizationTool(reuse_state=True)
    # tool.load_program()
    # tool.load_input()
    # context = ""
    # query = "Do you think the scene contains enough elements to ensure proper lighting? If not, then add more elements such as lamps, chandeliers, etc."
    # tool.progsyn.run_refine(tool.input, tool.program, context, query)
    
    return FunctionResult(status="Solved")

def resolve_temperature_control() -> FunctionResult:
    # tool = OptimizationTool(reuse_state=True)
    # tool.load_program()
    # tool.load_input()
    # context = ""
    # query = "Do you think the scene contains enough elements to ensure proper temperature control? If not, then add more elements such as air conditioners, heaters, etc."
    # tool.progsyn.run_refine(tool.input, tool.program, context, query)
    
    return FunctionResult(status="Solved")

class SceneOptimizer:
    def __init__(self):
        self.agent = SimpleAgent(
            name="SceneOptimizer",
            role="Optimize the scene layout using a variety of tools",
            description=f"""
You are a scene optimizer responsible for improving the layout of the scene based on the input provided. To do so, you should use the various tools provided according to the following guidelines:

1. **Optional Tools**: Depending on the scene, consider enhancing greenery, storage, seating, aesthetics, health and safety, lighting, and temperature control. Use your best judgment to call appropriate tools as optional enhancements.
   - Call **resolve_greenery** in spaces where plants or green elements add value (e.g., lobbies, cafes, offices, or wellness spaces).
   - Use **resolve_storage** where additional storage can increase functionality (e.g., kitchens, bedrooms, or retail spaces).
   - Activate **resolve_seating** when the scene benefits from organized seating (e.g., living rooms, waiting rooms, restaurants).
   - **resolve_asthetics** should enhance the visual appeal and maintain a cohesive design, particularly in public and retail spaces.
   - **resolve_health_and_safety** should ensure safe layouts in high-traffic areas, healthcare settings, and environments where safety is a priority.
   - **resolve_lighting** is critical in areas that require specific lighting conditions for visibility or ambiance, such as offices, galleries, and restaurants.
   - **resolve_temperature_control** is needed in spaces where temperature significantly impacts comfort or product preservation, like kitchens, lobbies, and storage areas.

2. **Mandatory Tools**: After using optional tools, execute the following tools in the specified order to complete the scene optimization:
   - **resolve_wall_overlap**, **resolve_relative_scale**, **resolve_balance**, **resolve_scene_scale**, **resolve_orientation**, and **resolve_physical_and_ergonomic_issues**.

""",
        )

        self.agent.add_tool(
            resolve_wall_overlap,
            "resolve_wall_overlap",
            "Check for and resolve overlapping issues between objects on walls. This tool is particularly important in small spaces with limited wall space, like bathrooms, kitchens, and small retail stores, where wall-mounted items can crowd or interfere with one another."
        )
        self.agent.add_tool(
            resolve_relative_scale,
            "resolve_relative_scale",
            "Ensure that objects in the scene are proportionate to one another. This tool is essential for spaces where items should look well-balanced in size, such as in living rooms, office spaces, and showrooms."
        )
        self.agent.add_tool(
            resolve_balance,
            "resolve_balance",
            "Balance the layout to create a visually appealing and functional arrangement. This tool is useful for any scene, but especially in retail stores, galleries, and living spaces where a balanced layout improves usability and aesthetics."
        )
        self.agent.add_tool(
            resolve_scene_scale,
            "resolve_scene_scale",
            "Ensure that the scene’s overall scale is appropriate for the number of objects. This tool is critical in spaces with limited square footage, such as small offices, home studios, and compact retail shops, to prevent overcrowding."
        )
        self.agent.add_tool(
            resolve_orientation,
            "resolve_orientation",
            "Orient objects appropriately, focusing on visibility and accessibility. Use this tool in conversation-oriented spaces like living rooms, meeting rooms, and waiting areas to ensure seating arrangements promote interaction and comfort."
        )
        self.agent.add_tool(
            resolve_physical_and_ergonomic_issues,
            "resolve_physical_and_ergonomic_issues",
            "Address physical and ergonomic concerns, including visibility, accessibility, and clearance. This tool is important in workspaces, kitchens, and medical facilities where comfort and accessibility improve safety and productivity."
        )
        
        # Optional Tools
        self.agent.add_tool(
            resolve_greenery,
            "resolve_greenery",
            "Add greenery if beneficial, ensuring it enhances the ambiance without overcrowding. Prioritize this in reception areas, wellness spaces, and restaurants where plants can improve mood and aesthetics."
        )
        self.agent.add_tool(
            resolve_storage,
            "resolve_storage",
            "Add storage elements if needed, focusing on functionality. This is especially important in kitchens, offices, bedrooms, and stores to maintain organization and reduce clutter."
        )
        self.agent.add_tool(
            resolve_seating,
            "resolve_seating",
            "Ensure enough seating where required. This tool is critical in waiting rooms, cafes, theaters, and living rooms to enhance comfort and usability for occupants."
        )
        self.agent.add_tool(
            resolve_asthetics,
            "resolve_asthetics",
            "Enhance the aesthetic appeal to align with the space’s purpose and theme. This is particularly relevant in retail, dining, and residential spaces where visual appeal is crucial for user experience."
        )
        self.agent.add_tool(
            resolve_health_and_safety,
            "resolve_health_and_safety",
            "Add health and safety elements, especially in spaces that see high foot traffic, workspaces, kitchens, and child-friendly areas where safety is paramount."
        )
        self.agent.add_tool(
            resolve_lighting,
            "resolve_lighting",
            "Ensure that the scene has adequate lighting. Use this tool in spaces that require task-specific lighting, such as offices, kitchens, and art studios, or ambient lighting for mood in restaurants and living rooms."
        )
        self.agent.add_tool(
            resolve_temperature_control,
            "resolve_temperature_control",
            "Check that the scene has adequate temperature control. This tool is important for areas that need specific temperature conditions, like kitchens, storage rooms, and lobbies, to ensure comfort and product preservation."
        )

    def run(self, input):
        self.agent.respond(input)