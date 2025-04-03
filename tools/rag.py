from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from assets.llm_config import LLM_CONFIG

class Retriever:
    def __init__(self, path, chunk_size=512):
        self.loader = TextLoader(path)
        self.documents = self.loader.load()
        self.text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=128)
        self.texts = self.text_splitter.split_documents(self.documents)
        self.embeddings = OpenAIEmbeddings(api_key=LLM_CONFIG['api_key'])
        self.db = FAISS.from_documents(self.texts, self.embeddings)
        self.retriever = self.db.as_retriever()
    
    def get(self, query):
        return self.retriever.invoke(query)[0].page_content