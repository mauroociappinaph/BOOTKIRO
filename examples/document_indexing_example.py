"""
Example usage of the document indexing system.
"""
import os
import logging
import sys
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_automation_bot.services.rag.vector_store import get_vector_store
from personal_automation_bot.services.rag.indexer import DocumentIndexer
from personal_automation_bot.services.rag.document_indexer import DocumentIndexingService
from personal_automation_bot.services.rag.retriever import DocumentRetriever

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run document indexing example."""
    parser = argparse.ArgumentParser(description='Index documents and perform semantic search')
    parser.add_argument('--dir', type=str, help='Directory containing documents to index')
    parser.add_argument('--file', type=str, help='Single file to index')
    parser.add_argument('--query', type=str, help='Search query')
    parser.add_argument('--force', action='store_true', help='Force reindexing of documents')
    args = parser.parse_args()

    # Create vector store
    vector_store_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vector_store', 'documents')
    vector_store = get_vector_store("faiss", vector_store_path)

    # Create indexer
    indexer = DocumentIndexer(vector_store=vector_store)

    # Create document indexing service
    indexing_service = DocumentIndexingService(indexer=indexer)

    # Create retriever
    retriever = DocumentRetriever(indexer=indexer)

    # Process documents
    if args.file:
        if os.path.exists(args.file):
            try:
                print(f"Processing file: {args.file}")
                document = indexing_service.process_document(args.file, force=args.force)
                print(f"Document processed: {document['id']}")
                print(f"Text length: {len(document['text'])} characters")
                print(f"Metadata: {document['metadata']}")

                # Index document
                chunk_ids = indexing_service.index_document(args.file, force=args.force)
                print(f"Document indexed into {len(chunk_ids)} chunks")
            except Exception as e:
                print(f"Error processing file: {e}")
        else:
            print(f"File not found: {args.file}")

    if args.dir:
        if os.path.isdir(args.dir):
            try:
                print(f"Indexing directory: {args.dir}")
                results = indexing_service.index_directory(args.dir, force=args.force)
                print(f"Indexed {len(results)} documents")

                for file_path, chunk_ids in results.items():
                    print(f"  - {file_path}: {len(chunk_ids)} chunks")
            except Exception as e:
                print(f"Error indexing directory: {e}")
        else:
            print(f"Directory not found: {args.dir}")

    # Perform search if query provided
    if args.query:
        print(f"\\nSearching for: {args.query}")
        results = retriever.search(args.query, top_k=5)

        print(f"Found {len(results)} results:")
        for i, result in enumerate(results):
            print(f"\\n[Result {i+1}]")
            print(f"Score: {result.get('score', 0.0):.4f}")
            print(f"Source: {result.get('source', 'Unknown')}")
            print(f"Text: {result.get('text', '')[:200]}...")

if __name__ == "__main__":
    main()
