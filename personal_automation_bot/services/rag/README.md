# RAG Service

This service implements a Retrieval-Augmented Generation (RAG) system for the Personal Automation Bot. It provides functionality for indexing documents, storing vector embeddings, and retrieving relevant context for generating content.

## Components

### Vector Store

The vector store component provides an abstraction over different vector database implementations:

- **FAISSVectorStore**: Uses Facebook AI Similarity Search (FAISS) for efficient similarity search
- **ChromaVectorStore**: Uses ChromaDB for vector storage and retrieval

### Document Indexer

The document indexer handles:

- Processing documents into chunks
- Generating embeddings using sentence-transformers
- Adding documents to the vector store
- Managing document cache to avoid reprocessing unchanged documents

### Document Retriever

The document retriever provides:

- Semantic search functionality based on query embeddings
- Filtering of search results
- Context formatting for RAG applications

## Usage

### Basic Usage

```python
from personal_automation_bot.services.rag import DocumentIndexer, DocumentRetriever, get_vector_store

# Create vector store
vector_store = get_vector_store("faiss", "/path/to/store")

# Create indexer
indexer = DocumentIndexer(vector_store=vector_store)

# Create retriever
retriever = DocumentRetriever(indexer=indexer)

# Index documents
documents = [
    {"id": "doc1", "title": "Example", "text": "This is an example document."}
]
indexer.index_document(documents[0])

# Search for documents
results = retriever.search("example query", top_k=5)

# Get context for RAG
context, sources = retriever.get_relevant_context("example query", top_k=5)
```

### Configuration Options

#### Vector Store

- **store_type**: Type of vector store ("faiss" or "chroma")
- **store_path**: Path to store vector data
- **dimension**: Dimension of embedding vectors (for FAISS)
- **collection_name**: Name of the collection (for ChromaDB)

#### Document Indexer

- **embedding_model**: Name of the sentence-transformer model to use
- **chunk_size**: Size of text chunks for processing
- **chunk_overlap**: Overlap between chunks

## Dependencies

- **FAISS**: For efficient similarity search
- **ChromaDB**: Alternative vector database
- **sentence-transformers**: For generating embeddings

Install dependencies with:

```bash
pip install faiss-cpu chromadb sentence-transformers
```

## Example

See `examples/rag_example.py` for a complete example of using the RAG service.
