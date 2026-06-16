try:
    import chromadb
    from sentence_transformers import SentenceTransformer

    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    chroma_client   = chromadb.PersistentClient(path='./chroma_db')
    collection      = chroma_client.get_or_create_collection(name='pm-documents')
    RAG_AVAILABLE   = True
    print("RAG: loaded successfully")

except Exception as e:
    embedding_model = None
    chroma_client   = None
    collection      = None
    RAG_AVAILABLE   = False
    print(f"RAG disabled: {e}")


def add_document(doc_id: str, text: str, metadata: dict = {}):

    if not RAG_AVAILABLE:
        return 0

    chunks = []
    chunk_size = 500

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    embeddings = embedding_model.encode(chunks).tolist()

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[metadata for _ in chunks]
    )

    return len(chunks)


def retrieve_context(query: str, n_results: int = 3) -> str:

    if not RAG_AVAILABLE:
        return ''

    if collection.count() == 0:
        return ''

    query_embedding = embedding_model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count())
    )

    if results['documents'] and results['documents'][0]:
        return '\n\n'.join(results['documents'][0])

    return ''


def clear_documents():

    if not RAG_AVAILABLE:
        return

    chroma_client.delete_collection('pm-documents')

    global collection
    collection = chroma_client.get_or_create_collection(
        name='pm-documents'
    )