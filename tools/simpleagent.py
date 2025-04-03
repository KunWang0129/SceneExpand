from autogen import UserProxyAgent, ConversableAgent, GroupChat, GroupChatManager
from tools.llm import LLM
from assets.llm_config import LLM_CONFIG
from tools.rag import Retriever

class SimpleAgent:
    def __init__(self, name, role, description, context=None, concluding_llm=None, additional_context=None, chunk_size=512, critic_description=None, force_accurate=False):
        """
        The agent's operation is realized via a group chat between the following primitive agents:
        1. The agent itself that also serves as the group chat manager
        2. Tool agent that is responsible for the execution of the agent's tasks
        """

        self.name = name
        self.role = role
        self.description = description
        
        if force_accurate:
            llm_config = LLM_CONFIG.copy()
            llm_config["model"] = "gpt-4o"
        else:
            llm_config = LLM_CONFIG
        if context:
            self.retriever = Retriever(context, chunk_size=chunk_size)
        else:
            self.retriever = None

        if additional_context:
            with open(additional_context, 'r') as f:
                self.additional_context = "\nFollowing are some examples of how your response should look like:\n" + f.read()
                self.additional_context += "\n"
        else:
            self.additional_context = ""
            
        if concluding_llm:
            self.concluding_llm = concluding_llm
        else:
            self.concluding_llm = LLM(single_use=True, system_desc="You are a helpful assistant that goes through a chat and generates a reponse based on the query.", response_format="text")

        self.agent = ConversableAgent(
            name=name,
            description=role,
            system_message=description+self.additional_context,
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg = self.terminate,
        )
        
        if critic_description:
            self.critic = LLM(single_use=True, system_desc=critic_description+self.additional_context, response_format="text", force_accurate=force_accurate)
        else:
            self.critic = None
            
        self.tool_agent = ConversableAgent(
            name=f"{name}_tool_agent",
            description=f"Executes tools on behalf of {name}",
            system_message=f"Your task is to execute tools on behalf of {name}. In case no tool usage is needed, reply with TERMINATE. Never ask human for feedback.",
            llm_config=LLM_CONFIG,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg = self.terminate,
        )

    def terminate(self, msg):
        if msg["content"] is None:
            return False
        return "terminate" in msg["content"].lower()

    def add_tool(self, tool, name, description):
        self.agent.register_for_llm(name=name, description=description)(tool)
        self.tool_agent.register_for_execution(name=name)(tool)

    def respond(self, query):
        if self.critic:
            return self.__respond_with_critic(query)
        return self.__respond(query)
    
    def __respond(self, query):
        if self.retriever:
            context = self.retriever.get(query)
            prompt = f"\nFollowing are an example of how your response should look like:\n{context}\nRefrain from simply outputing the example responses, use your own creativity!\n"   
            query = prompt + query
        
        result = self.tool_agent.initiate_chat(self.agent, message=query, summary_method="last_msg", human_input_mode="NEVER",silent=False)
        prompt = f"Query: {query}. \n Chat: {result}"
        prompt += f"\n Generate a response to the query based on the above chat. \nYour response:"
        result = self.concluding_llm.run(prompt)
        return result
    
    def refine(self, query, response, critique):
        query = f"""Given the query: {query}, you had earlier generated the response: {response}. Now, you need to refine the response based on the critique: {critique}.
        """
        return self.__respond(query)
        
    def __respond_with_critic(self, query):
        result = self.__respond(query)
        
        prompt = f"Query: {query}. \n Response: {result}"
        prompt += f"\n Provide a critique to the response above. \nYour critique:"
        critique = self.critic.run(prompt)
        refined_response = self.refine(query, result, critique) 
        return refined_response
        


