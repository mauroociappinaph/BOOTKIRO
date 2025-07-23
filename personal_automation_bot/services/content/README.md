# Content Generation Service

This service provides functionality for generating text and images using various AI services, with a focus on Retrieval-Augmented Generation (RAG).

## Components

### Text Generators

The service includes multiple text generation backends:

- **OpenAITextGenerator**: Uses OpenAI's API for text generation
- **HuggingFaceTextGenerator**: Uses Hugging Face models (either API or local)

### RAG Generator

The RAG Generator combines document retrieval with text generation to create responses that are:

1. Grounded in your personal documents
2. Properly cited with sources
3. Contextually relevant to your query

## Usage

### Basic Text Generation

```python
from personal_automation_bot.services.content import get_text_generator

# Create a text generator (defaults to OpenAI)
generator = get_text_generator(api_key="your-api-key")

# Generate text
response = generator.generate(
    prompt="Write a short paragraph about artificial intelligence",
    max_tokens=100,
    temperature=0.7
)

print(response)
```

### RAG Generation

```python
from personal_automation_bot.services.content import RAGGenerator
from personal_automation_bot.services.rag import DocumentRetriever, get_vector_store

# Create vector store and retriever
vector_store = get_vector_store("faiss", "/path/to/store")
retriever = DocumentRetriever(vector_store=vector_store)

# Create RAG generator
rag = RAGGenerator(retriever=retriever)

# Generate text with RAG
response = rag.generate(
    query="What are the key features of our product?",
    top_k=5,
    max_tokens=300
)

# Get formatted text with citations
formatted_text = response.get_formatted_text_with_citations()
print(formatted_text)

# Access citations
for citation in response.citations:
    print(f"Source: {citation.source_path}, Score: {citation.relevance_score}")
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: API key for OpenAI
- `OPENAI_ORGANIZATION`: Organization ID for OpenAI (optional)
- `HF_API_KEY`: API key for Hugging Face

### Supported Models

#### OpenAI

- `gpt-3.5-turbo` (default)
- `gpt-4` (if available)
- Any other model supported by your API key

#### Hugging Face

- `google/flan-t5-base` (default)
- Any model available on Hugging Face

## Dependencies

- `openai`: For OpenAI API integration
- `transformers`: For local Hugging Face models
- `torch`: For local model inference
- `requests`: For API calls

## Features

- **Multiple Backends**: Support for different text generation services
- **Context-Aware Generation**: Generate text based on retrieved documents
- **Citation System**: Track and cite sources used in generation
- **Local and API Options**: Use either cloud APIs or local models
