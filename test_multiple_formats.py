"""
Test document processors with multiple file formats.
"""
import os
import tempfile
import shutil
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath('.'))

# Create test files
temp_dir = tempfile.mkdtemp()

# Text file
txt_file = os.path.join(temp_dir, "test.txt")
with open(txt_file, "w") as f:
    f.write("This is a plain text document.\nIt has multiple lines.")

# HTML file
html_file = os.path.join(temp_dir, "test.html")
with open(html_file, "w") as f:
    f.write("""
    <html>
    <head><title>Test Document</title></head>
    <body>
        <h1>Test HTML Document</h1>
        <p>This is a paragraph with <strong>bold text</strong>.</p>
        <script>console.log('This should be removed');</script>
    </body>
    </html>
    """)

# Markdown file
md_file = os.path.join(temp_dir, "test.md")
with open(md_file, "w") as f:
    f.write("""
# Test Markdown Document

This is a **markdown** document with:

- Lists
- *Italic text*
- Code blocks

```python
print("Hello, world!")
```
    """)

print(f"Created test files in: {temp_dir}")

try:
    from personal_automation_bot.services.rag.document_processors.factory import get_document_processor

    test_files = [
        (txt_file, "Text"),
        (html_file, "HTML"),
        (md_file, "Markdown")
    ]

    for file_path, file_type in test_files:
        print(f"\n=== Testing {file_type} file ===")

        processor = get_document_processor(file_path)
        if processor:
            print(f"Processor: {processor.__class__.__name__}")

            result = processor.process_file(file_path)
            print(f"Text length: {len(result['text'])}")
            print(f"Text preview: {result['text'][:100]}...")
            print(f"File type: {result['metadata'].get('file_type')}")
            print(f"MIME type: {result['metadata'].get('mime_type')}")
        else:
            print(f"No processor found for {file_path}")

    print("\n✅ All file formats processed successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Clean up
    shutil.rmtree(temp_dir)
    print(f"Cleaned up: {temp_dir}")
