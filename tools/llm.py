from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser, SimpleJsonOutputParser
from assets.llm_config import LLM_CONFIG 

class LLM:
    def __init__(self, single_use=True, 
                 system_desc=None, 
                 response_format="text", 
                 force_accurate=False, 
                 image_input=False, 
                 image_detail='low',
                 json_keys=None,
                 num_images=1,
                 ):
        
        self.response_format = response_format
        self.image_detail=image_detail
        self.image_input=image_input
        self.json_keys = json_keys
        self.num_images = num_images    
        
        # Configure the response format
        if self.response_format == "json":
            self.response_format_config = {"type": "json_object"}
        else:
            self.response_format_config = {"type": "text"}
        
        # Initialize the model with the given configuration
        self.model = ChatOpenAI(
            model=LLM_CONFIG['model'] if not force_accurate else "gpt-4o",
            api_key=LLM_CONFIG['api_key'],
            model_kwargs={"response_format": self.response_format_config},
            # seed=LLM_CONFIG['seed']
        )
        
        # Initial system message and prompt template
        self.system_desc = system_desc or "You are a helpful assistant."
        
        if image_input:
            self.prompt_template = ChatPromptTemplate.from_messages(
            messages= self.prepare_image_prompt_template()
            )
        else:
            self.prompt_template = ChatPromptTemplate.from_messages([
                ("system", self.system_desc),
                ("human", "{input}")
            ])
        
        self.single_use = single_use
        self.history = []
        self.reset()

    def _sanitize_output(self, text: str):
        _, after = text.split("```python")
        return after.split("```")[0]
    
    def reset(self):
        """Resets the chat history, retaining the system description."""
        self.history = [{"role": "system", "content": self.system_desc}]
    
    def _get_prompt_with_history(self):
        """Constructs the full prompt including chat history."""
        return "".join([f"{msg['role']}: {msg['content']}\n" for msg in self.history])
    
    def run(self, query, image_paths=None):
        """Generates a response from the model based on the query and history."""
        # Append the user query to the history
        self.history.append({"role": "human", "content": query})
        
        # Prepare the full prompt with chat history
        full_prompt = self._get_prompt_with_history()
        
        # Define the chain based on the response format
        if self.response_format == "json":
            chain = self.prompt_template | self.model | SimpleJsonOutputParser()
        else:
            chain = self.prompt_template | self.model | StrOutputParser()
        
        if self.response_format == "code":
            full_prompt += """Return only python code in Markdown format, e.g.:
```python
....
```"""
        # Invoke the model and get the response
        if self.image_input:
            assert len(image_paths) == self.num_images, f"Number of images should be {self.num_images}."
            result = self.invoke_image_prompt_template(chain, full_prompt, image_paths)
        else:
            result = chain.invoke({"input": full_prompt})
        
        if self.response_format == "code":
            result = self._sanitize_output(result)

        if self.response_format == "json" and self.json_keys:
            # Check if all the keys are present in the response
            for key in self.json_keys:
                if key not in result:
                    query = """ 
                    For the query: {query}, the following response was generated: {response}. It didn't follow the expected format containing the keys: {self.json_keys}. Please ensure that the response follows the expected format and contains all the keys.
                    """
                    result = self.run(query, image_paths)
            
        # Append the model response to the history
        self.history.append({"role": "assistant", "content": result})
        
        if self.single_use:
            self.reset()

        # Return the response
        return result

    def invoke_image_prompt_template(self, chain, prompt, image_paths):
        if self.num_images == 1:
            return chain.invoke({'input':prompt, 'image_path1': image_paths[0], 'detail_parameter': self.image_detail})
        elif self.num_images == 2:
            return chain.invoke({'input':prompt, 'image_path1': image_paths[0], 'image_path2': image_paths[1], 'detail_parameter': self.image_detail})
        elif self.num_images == 3:
            return chain.invoke({'input':prompt, 'image_path1': image_paths[0], 'image_path2': image_paths[1], 'image_path3': image_paths[2], 'detail_parameter': self.image_detail})
        elif self.num_images == 4:
            return chain.invoke({'input':prompt, 'image_path1': image_paths[0], 'image_path2': image_paths[1], 'image_path3': image_paths[2], 'image_path4': image_paths[3], 'detail_parameter': self.image_detail})
        else:
            raise ValueError("Number of images should be between 1 and 4.")
        
    def prepare_image_prompt_template(self):
        if self.num_images == 1:
            return self.image1()
        elif self.num_images == 2:
            return self.image2()
        elif self.num_images == 3:
            return self.image3()
        elif self.num_images == 4:
            return self.image4()
        else:
            raise ValueError("Number of images should be between 1 and 4.")
        
    def image1(self):
        messages=[
                ChatPromptTemplate.from_messages([
                    ("system", self.system_desc),
                    ("human", "{input}")
                ]),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path1}', 'detail': '{detail_parameter}'}}]
                )
            ]
        return messages

    def image2(self):
        messages=[
                ChatPromptTemplate.from_messages([
                    ("system", self.system_desc),
                    ("human", "{input}")
                ]),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path1}', 'detail': '{detail_parameter}'}}]
                ),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path2}', 'detail': '{detail_parameter}'}}]
                )
            ]
        return messages
    
    def image3(self):
        messages=[
                ChatPromptTemplate.from_messages([
                    ("system", self.system_desc),
                    ("human", "{input}")
                ]),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path1}', 'detail': '{detail_parameter}'}}]
                ),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path2}', 'detail': '{detail_parameter}'}}]
                ),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path3}', 'detail': '{detail_parameter}'}}]
                )
            ]
        return messages
    
    def image4(self):
        messages=[
                ChatPromptTemplate.from_messages([
                    ("system", self.system_desc),
                    ("human", "{input}")
                ]),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path1}', 'detail': '{detail_parameter}'}}]
                ),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path2}', 'detail': '{detail_parameter}'}}]
                ),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path3}', 'detail': '{detail_parameter}'}}]
                ),
                HumanMessagePromptTemplate.from_template(
                    [{'image_url': {'path': '{image_path4}', 'detail': '{detail_parameter}'}}]
                )
            ]
        return messages