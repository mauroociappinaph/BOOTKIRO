"""
Example usage of the RAG system.
"""
import os
import logging
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_automation_bot.services.rag.vector_store import get_vector_store

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Run RAG example."""
    # Create vector store
    vector_store_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vector_store', 'example')
    vector_store = get_vector_store("faiss", vector_store_path)

    # Check if sentence-transformers is installed
    try:
        import sentence_transformers
        has_sentence_transformers = True
    except ImportError:
        has_sentence_transformers = False
        print("Warning: sentence-transformers is not installed. Using mock embeddings for demonstration.")
        print("Install with: pip install sentence-transformers")

    if has_sentence_transformers:
        # Import these only if sentence-transformers is available
        from personal_automation_bot.services.rag.indexer import DocumentIndexer
        from personal_automation_bot.services.rag.retriever import DocumentRetriever

        # Create indexer with real embedding model
        indexer = DocumentIndexer(vector_store=vector_store)
        # Create retriever
        retriever = DocumentRetriever(indexer=indexer)
    else:
        # Create mock indexer and retriever for demonstration
        class MockIndexer:
            def index_document(self, document):
                print(f"Indexing document: {document['id']}")
                return [document['id']]

            def generate_embeddings(self, texts):
                # Generate random embeddings for demonstration
                import random
                return [[random.random() for _ in range(128)] for _ in texts]

        class MockRetriever:
            def search(self, query, top_k=5, filters=None):
                print(f"Searching for: {query}")
                return [
                    {"id": "doc2", "title": "Vector Databases", "text": "Vector databases are specialized databases...", "score": 0.95},
                    {"id": "doc1", "title": "Introduction to RAG", "text": "Retrieval-Augmented Generation (RAG) is a technique...", "score": 0.85}
                ][:top_k]

            def get_relevant_context(self, query, top_k=5, filters=None, max_tokens=None):
                results = self.search(query, top_k, filters)
                context = "\n\n".join([f"[Document {i+1}] (Source: {r['id']}, Relevance: {r['score']:.2f})\n{r['text']}" for i, r in enumerate(results)])
                return context, results

        indexer = MockIndexer()
        retriever = MockRetriever()

    # Sample documents
    documents = [
        {
            "id": "doc1",
            "title": "Introduction to RAG",
            "text": "Retrieval-Augmented Generation (RAG) is a technique that combines retrieval-based and generation-based approaches for natural language processing tasks. It first retrieves relevant documents from a corpus and then uses them to augment the input of a language model for generation."
        },
        {
            "id": "doc2",
            "title": "Vector Databases",
            "text": "Vector databases are specialized databases designed to store and query vector embeddings efficiently. They are essential for implementing RAG systems as they enable fast similarity search over large collections of documents. Popular vector databases include FAISS and Chroma."
        },
        {
            "id": "doc3",
            "title": "Embedding Models",
            "text": "Embedding models convert text into numerical vectors that capture semantic meaning. These vectors can be compared using similarity metrics like cosine similarity. Popular embedding models include those from the sentence-transformers library."
        }
    ]

    # Index documents
    print("Indexing documents...")
    for doc in documents:
        indexer.index_document(doc)

    # Search for documents
    print("\nSearching for documents...")
    query = "How do vector databases work?"
    results = retriever.search(query, top_k=2)

    print(f"\nResults for query: '{query}'")
    for i, result in enumerate(results):
        print(f"\n[Result {i+1}]")
        print(f"Title: {result.get('title', 'Unknown')}")
        print(f"Score: {result.get('score', 0.0):.4f}")
        print(f"Text: {result.get('text', '')[:100]}...")

    # Get context for RAG
    print("\nGetting context for RAG...")
    context, _ = retriever.get_relevant_context(query, top_k=2)
    print(f"\nContext:\n{context[:500]}...")

if __name__ == "__main__":
    main()
