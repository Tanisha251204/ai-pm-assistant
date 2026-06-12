import chromadb
from sentence_transformers import SentenceTransformer
# Load the embedding model once when the file is imported

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
# Create a local ChromaDB client

chroma_client = chromadb.PersistentClient(path='./chroma_db')
# Get or create a collection (like a table in ChromaDB)
collection = chroma_client.get_or_create_collection(
    name='pm-documents'
)

def add_document(doc_id: str, text: str, metadata: dict = {}):
    # Split text into chunks of 500 characters
    chunks = []
    chunk_size = 500

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    # Create embeddings for each chunk
    embeddings = embedding_model.encode(chunks).tolist()

    # Store each chunk with its embedding in ChromaDB
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[metadata for _ in chunks]
    )

    return len(chunks)


def retrieve_context(query: str, n_results: int = 3) -> str:
    # Check if collection has any documents
    if collection.count() == 0:
        return ""

    # Convert query to embedding
    query_embedding = embedding_model.encode([query]).tolist()

    # Find most similar chunks
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count())
    )

    # Join the retrieved chunks into one context string
    if results["documents"] and results["documents"][0]:
        return "\n\n".join(results["documents"][0])

    return ""


def clear_documents():
    # Delete and recreate the collection
    chroma_client.delete_collection("pm_documents")

    global collection
    collection = chroma_client.get_or_create_collection(
        name="pm_documents"
    )