"""
Example usage of the RAG generation system.
"""
import os
import logging
import sys
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run RAG generation example."""
    parser = argparse.ArgumentParser(description='Generate text using RAG')
    parser.add_argument('--query', type=str, default="What is RAG and how does it work?", help='Query to generate text for')
    parser.add_argument('--dir', type=str, help='Directory containing documents to index')
    parser.add_argument('--provider', type=str, default="mock", help='Text generator provider (openai, huggingface, or mock)')
    parser.add_argument('--model', type=str, help='Model to use for generation')
    args = parser.parse_args()

    # Import here to handle potential import errors gracefully
    try:
        from personal_automation_bot.services.rag.vector_store import get_vector_store
        from personal_automation_bot.services.rag.indexer import DocumentIndexer
        from personal_automation_bot.services.rag.retriever import DocumentRetriever
        from personal_automation_bot.services.rag.document_indexer import DocumentIndexingService
        from personal_automation_bot.services.content import RAGGenerator, get_text_generator

        # Create vector store
        vector_store_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vector_store', 'rag_example')
        vector_store = get_vector_store("faiss", vector_store_path)

        # Create indexer and retriever
        indexer = DocumentIndexer(vector_store=vector_store)
        retriever = DocumentRetriever(indexer=indexer)

        # Create document indexing service
        indexing_service = DocumentIndexingService(indexer=indexer)

        # Index documents if directory provided
        if args.dir:
            if os.path.isdir(args.dir):
                print(f"Indexing documents in {args.dir}...")
                results = indexing_service.index_directory(args.dir)
                print(f"Indexed {len(results)} documents")
            else:
                print(f"Directory not found: {args.dir}")
                return

        # Create text generator based on provider
        if args.provider == "mock":
            # Create a mock text generator for testing
            from personal_automation_bot.services.content.text_generator import TextGenerator

            class MockTextGenerator(TextGenerator):
                def generate(self, prompt, **kwargs):
                    return f"Generated text for: {prompt}"

                def generate_with_context(self, prompt, context, **kwargs):
                    return f"Generated text for: {prompt}\nBased on context: {context[:100]}..."

            generator = MockTextGenerator()
            print("Using mock text generator")
        else:
            # Get real text generator
            generator = get_text_generator(provider=args.provider, model=args.model)
            print(f"Using {args.provider} text generator")

        # Create RAG generator
        rag_generator = RAGGenerator(retriever=retriever, generator=generator)

        # Generate text
        print(f"\\nGenerating text for query: {args.query}")
        response = rag_generator.generate(query=args.query, top_k=3)

        # Print results
        print("\\n=== Generated Text ===")
        print(response.text)

        print("\\n=== Citations ===")
        if response.citations:
            for i, citation in enumerate(response.citations):
                print(f"{i+1}. {citation.source_path} (Score: {citation.relevance_score:.2f})")
        else:
            print("No citations available")

        print("\\n=== Formatted Text with Citations ===")
        print(response.get_formatted_text_with_citations())

    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Make sure all dependencies are installed")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
