"""
Simple test to verify document indexing works.
"""
import os
import tempfile
import shutil

# Create a simple test document
temp_dir = tempfile.mkdtemp()
test_file = os.path.join(temp_dir, "test.txt")

with open(test_file, "w") as f:
    f.write("This is a test document for indexing.\nIt contains multiple lines.\nThis should work fine.")

print(f"Created test file: {test_file}")

try:
    # Test document processors
    from personal_automation_bot.services.rag.document_processors.text import TextProcessor
    from personal_automation_bot.services.rag.document_processors.factory import get_document_processor

    print("Testing TextProcessor...")
    processor = TextProcessor()

    # Test can_process
    can_process = processor.can_process(test_file)
    print(f"Can process: {can_process}")

    # Test extract_text
    text = processor.extract_text(test_file)
    print(f"Extracted text: {text}")

    # Test extract_metadata
    metadata = processor.extract_metadata(test_file)
    print(f"Metadata: {metadata}")

    # Test factory
    print("\nTesting factory...")
    factory_processor = get_document_processor(test_file)
    print(f"Factory processor: {factory_processor.__class__.__name__}")

    # Test document processing
    result = factory_processor.process_file(test_file)
    print(f"Process result keys: {result.keys()}")

    print("\n✅ All tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Clean up
    shutil.rmtree(temp_dir)
    print(f"Cleaned up: {temp_dir}")
