import os
import json

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.milvus import MilvusVectorStore

from utils.config_loader import app_config
from utils.leave_folders import find_non_empty_leaf_folders


# Access appplication environment variables
# define global Setting that sets the LLM and ebemdding model.
# There is no need to pass in any llm or embedding model to the LlamaIndexTool query engine.
# The LlamaIndexTool will use the global Settings to get the llm and embedding model.

model = app_config.LLAMAINDEX_MODEL
embed_model= app_config.LLAMAINDEX_EMBEDDING

Settings.llm = OpenAI(temperature=0.1, model=model)
Settings.embed_model = OpenAIEmbedding(model=embed_model)


class MilvusDataLoader:
    """
    A class to read documents from a directory and insert them into a Milvus collection.
    Reads configuration from config_loader.py
    """

    def __init__(self):
        """
        Initializes the MilvusDataLoader with Milvus server details from a TOML file.
        :param config_file: Path to the YAML configuration file.
        """
        self.milvus_uri = app_config.MILVUS_URL
        self.dim = app_config.MILVUS_DIM
        self.overwrite = app_config.MILVUS_OVERRIDE
        self.collection = app_config.MILVUS_COLLECTION


    def load_and_store(self, input_dir: str, collection_name: str):
        """
        Loads documents from a directory and inserts them into a Milvus collection.

        :param input_dir: Path to the directory containing documents.
        :param ship_ref_booking: Unique collection name in Milvus.
        """
        try:
            # Load documents from the directory
            
            # Check if the input directory exists and is not empty
            if not os.path.exists(input_dir):
                print(f"Error: The directory {input_dir} does not exist.")
                return

            if not os.listdir(input_dir):
                print(f"Error: The directory {input_dir} is empty.")
                return
            
            ## controls the file types to be read
            required_exts = [".txt", ".pdf", ".doc", ".html", ".xls", ".xlsx", ".docx"] 
            
            leaves = find_non_empty_leaf_folders(input_dir)
            all_documents = []
            
            for leave in leaves:
            # Load the first line of meta.jsonl
                meta_path = os.path.join(leave, "meta.jsonl")
                shared_meta = {}
            
                if os.path.exists(meta_path):
                    with open(meta_path, "r") as f:
                        shared_meta = json.loads(f.readline())
                        print(f"ℹ️ Loaded metadata from {meta_path}")
                        print (shared_meta)
                else:
                    print(f"⚠️ No meta.jsonl found in {leave}")
                
                    # Metadata for each file in the directory
    
                def file_metadata(file_path):
                    filename = os.path.basename(file_path)
                    base_metadata = {
                        "filename": filename,
                        "source_dir": leave,
                        "custom_tag": "custom_value"}             

                    # Merge shared metadata with per-file base metadata
                    print (base_metadata)
                    return {**base_metadata, **shared_meta}            
            
                reader = SimpleDirectoryReader(input_dir=leave,  
                                            required_exts=required_exts, 
                                            recursive=False,
                                        file_metadata=file_metadata)
                documents = reader.load_data()
                all_documents.extend(documents)

            if not all_documents:
                print("No documents found in the directory.")
                return

            
            # Create Milvus vector store
            vector_store = MilvusVectorStore(
                uri=self.milvus_uri,
                dim=self.dim,
                overwrite=self.overwrite,
                collection_name=self.collection
            )

 
            # Create storage context
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # Create vector index and insert documents
            index = VectorStoreIndex.from_documents(all_documents, storage_context=storage_context)

            print(f"Successfully stored {len(all_documents)} documents in collection: {collection_name}")

        except Exception as e:    
            print(f"Error: {e}")


if __name__ == "__main__": 
    loader = MilvusDataLoader()
    input_dir = "/home/tanpohkeam/ubts/msg_app/outputs/export/F45451345A/250313-103155"
    results = loader.load_and_store(input_dir=input_dir,  collection_name = "09TODELETE")