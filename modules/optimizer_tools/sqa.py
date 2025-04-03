from tools.llm import LLM
class SQA:
    def __init__(self):
        self.llm = LLM(
            system_desc="Your task is to examine the images rendered from different corners of the room and answer the user's query. You must use relevant context provided by the user and the images to generate a helpful response.",
            image_input=True, 
            num_images=4)
        
    def render(self):
        import subprocess
        # Path to the Blender executable
        # Update this path according to your Blender installation
        blender_executable_path = '/Applications/Blender.app/Contents/MacOS/Blender'

        # Path to your custom script that you want Blender to run
        script_path = '/Users/kunalgupta/Documents/sceneprog/modules/optimizer_tools/render_from_corners.py'

        # Constructing the command to run Blender, execute the script, and pass the assetID
        command = [
            blender_executable_path,
            '--python', script_path,  # The path to the script Blender will run
            '--background',  # Run Blender in background mode
        ]
        # Execute the command
        try:
            subprocess.run(command, timeout=30)
        except subprocess.TimeoutExpired:
            print("Blender process exceeded the time limit and was terminated.")
        
    def run(self, query):
        self.render()
        image_paths = [
            'tmp/render_corner_0.png',
            'tmp/render_corner_1.png',
            'tmp/render_corner_2.png',
            'tmp/render_corner_3.png'
        ]
        return self.llm.run(query, image_paths=image_paths)