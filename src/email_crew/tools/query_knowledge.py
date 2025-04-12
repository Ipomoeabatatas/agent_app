import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI
from crewai_tools import LlamaIndexTool
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from utils.config_loader import app_config

# Access appplication environment variables
model = app_config.LLAMAINDEX_MODEL
embed_model= app_config.LLAMAINDEX_EMBEDDING
input_dir = app_config.LLAMAINDEX_DOCDIR

# define global Setting that sets the LLM and ebemdding model.
# There is no need to pass in any llm or embedding model to the LlamaIndexTool query engine.
# The LlamaIndexTool will use the global Settings to get the llm and embedding model.
Settings.llm = OpenAI(temperature=0.1, model=model)
Settings.embed_model = OpenAIEmbedding(model=embed_model)

class QueryToolManager:
    """
    A singleton class to build and manage the query engine efficiently.
    Ensures the query engine is built only once and provides access to query_tool.
    """

    _instance = None  # Class-level variable to store the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QueryToolManager, cls).__new__(cls)
            cls._instance._initialized = False  # Track initialization status
        return cls._instance

    def __init__(self, input_dir=input_dir, similarity_top_k=5):
        """
        Initializes the QueryToolManager.

        Parameters:
        - input_dir (str): The directory containing knowledge documents.
        - similarity_top_k (int): Number of top similar results to retrieve (default: 5).
        """
        if not self._initialized:
            self.input_dir = input_dir
            self.similarity_top_k = similarity_top_k

            # Build the query engine
            self.query_engine = self._build_query_engine()

            # Build the query tool
            self.query_tool = self._build_query_tool()

            self._initialized = True  # Mark as initialized

    def _build_query_engine(self):
        """
        Private method to build the query engine only once.
        """

        # Check if the input directory exists
        if not os.path.exists(self.input_dir):
            raise FileNotFoundError(f"The input directory '{self.input_dir}' does not exist.")

        # List out all the files in the input directory
        files = os.listdir(self.input_dir)
        if not files:
            raise FileNotFoundError(f"The input directory '{self.input_dir}' is empty.")
        
        print("\nFiles in input directory to be indexed and used as Crew Tool:")
        for file in files:
            print(file)


        print("Building the query engine...")
        
        # Load documents from the input directory
        reader = SimpleDirectoryReader(input_dir=self.input_dir, recursive=True)
        
        
        docs = reader.load_data()

        # Initialize the OpenAI language model
   

        # Create the vector store index
        index = VectorStoreIndex.from_documents(docs)

        # Create the query engine
        query_engine = index.as_query_engine(similarity_top_k=self.similarity_top_k)

        return query_engine

    def _build_query_tool(self):
        """
        Private method to build the query tool using LlamaIndexTool.
        """
        print("Creating LlamaIndex query tool...")
        
        query_tool = LlamaIndexTool.from_query_engine(
            self.query_engine,
            name="UBTS Documents",
            description="Use this tool to retrieve information from UBTS documents such as policy handbook, operational procedures guides, shipping schedule tables, and more.",
        )
        
        return query_tool

    def get_query_tool(self):
        """
        Public method to get the query tool.
        """
        return self.query_tool

    def get_query_engine(self):
        """
        Public method to get the query engine.
        """
        return self.query_engine

# Example Usage:
if __name__ == "__main__":
    # Initialize the QueryToolManager
    tool_manager = QueryToolManager(
        input_dir=input_dir,
    )

    # Get the query tool
    query_tool = tool_manager.get_query_tool()

    # Test the query engine
    query_engine = tool_manager.get_query_engine()
    queries = [
        "What are the export documentation needs?", 
        "What was arrival information for An Hai?", 
        "Give the coordinates of Singapore port"
    ]
    
    
    for query in queries:
        print("================================================")
        response = query_tool.run(query)
        print("Query   : ", query)
        print("Response: ", response)
        print()
