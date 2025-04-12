from pymilvus import MilvusClient, DataType, db, connections, Collection, MilvusException, utility


class Vectorizer:
    """Processes documents, generates embeddings, and stores them in a vector database."""

    def __init__(self, model_name="all-MiniLM-L6-v2", vector_db=None):
        self.model = SentenceTransformer(model_name)
        self.vector_db = vector_db  # Vector storage (Chroma, FAISS, Qdrant)

    def process_document(self, doc_id, text):
        """Generates embeddings and stores them in the vector database."""
        embedding = self.model.encode(text)
        self.vector_db.add(doc_id, embedding, metadata={"text": text})  # Storing with metadata
        return embedding
    
    
    
if __name__ == "__main__":
    vector_db = ChromaVectorDB()
    vectorizer = Vectorizer(vector_db=vector_db)
    vectorizer.process_document("doc1", "This is a test document.")
    vectorizer.process_document("doc2", "This is another test document.")
    vector_db.search("test")  # Returns the most similar documents

    vector_db = FAISSVectorDB()
    vectorizer = Vectorizer(vector_db=vector_db)
    vectorizer.process_document("doc1", "This is a test document.")
    vectorizer.process_document("doc2", "This is another test document.")
    vector_db.search("test")  # Returns the most similar documents

    vector_db = QdrantVectorDB()
    vectorizer = Vectorizer(vector_db=vector_db)
    vectorizer.process_document("doc1", "This is a test document.")
    vectorizer.process_document("doc2", "This is another test document.")
    vector_db.search("test")  # Returns the most similar documents