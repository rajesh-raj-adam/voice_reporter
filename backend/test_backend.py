import os
import time
from document_processor import DocumentProcessor
from vector_engine import VectorEngine
from nlp_engine import NLEngine
from voice_engine import VoiceEngine

def test_document_processor():
    print("\nTesting Document Processor...")
    processor = DocumentProcessor()
    
    # Create a test text file
    test_file = "uploads/test.txt"
    with open(test_file, "w") as f:
        f.write("This is a test document.\nIt has multiple lines.\nFor testing purposes.")
    
    try:
        result = processor.process_document(test_file)
        print("✓ Document processing successful")
        print(f"Content: {result['content'][:100]}...")
        return result
    except Exception as e:
        print(f"✗ Document processing failed: {e}")
        return None

def test_vector_engine(document):
    print("\nTesting Vector Engine...")
    engine = VectorEngine()
    
    try:
        # Test document storage
        doc_id = engine.store_document(document, "test.txt")
        print("✓ Document storage successful")
        
        # Test search
        results = engine.search("test document")
        print("✓ Vector search successful")
        print(f"Found {len(results)} results")
        
        return doc_id
    except Exception as e:
        print(f"✗ Vector engine test failed: {e}")
        return None

def test_nlp_engine():
    print("\nTesting NLP Engine...")
    engine = NLEngine()
    
    try:
        # Test response generation
        response = engine.generate_response("What is this document about?", [{"content": "This is a test document."}])
        print("✓ Response generation successful")
        print(f"Response: {response}")
        
        return True
    except Exception as e:
        print(f"✗ NLP engine test failed: {e}")
        return False

def test_voice_engine():
    print("\nTesting Voice Engine...")
    engine = VoiceEngine()
    
    try:
        # Test text-to-speech
        audio_file = engine.text_to_speech("This is a test of the voice engine.")
        print("✓ Text-to-speech successful")
        print(f"Audio file: {audio_file}")
        
        return True
    except Exception as e:
        print(f"✗ Voice engine test failed: {e}")
        return False

def main():
    print("Starting backend component tests...")
    
    # Test document processor
    document = test_document_processor()
    if not document:
        return
    
    # Test vector engine
    doc_id = test_vector_engine(document)
    if not doc_id:
        return
    
    # Test NLP engine
    if not test_nlp_engine():
        return
    
    # Test voice engine
    if not test_voice_engine():
        return
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main() 