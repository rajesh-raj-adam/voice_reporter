import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid
from functools import lru_cache
import time
import re

class VectorEngine:
    def __init__(self):
        # Initialize with a better model for semantic search
        self.model = SentenceTransformer('all-mpnet-base-v2', device='cpu')
        
        # Define embedding function class for ChromaDB
        class CustomEmbeddingFunction:
            def __init__(self, model):
                self.model = model
            def __call__(self, input):
                if isinstance(input, str):
                    input = [input]
                return self.model.encode(input).tolist()

        # Initialize ChromaDB with optimized settings
        self.client = chromadb.Client(Settings(
            persist_directory="vector_storage",
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create or get the collection with explicit embedding function
        self.collection = self.client.get_or_create_collection(
            name="documents",
            embedding_function=CustomEmbeddingFunction(self.model),
            metadata={
                "hnsw:space": "cosine",
                "hnsw:construction_ef": 200,  # Increased for better accuracy
                "hnsw:search_ef": 100,  # Increased for better accuracy
            }
        )

    @lru_cache(maxsize=1000)
    def _encode_text(self, text: str) -> List[float]:
        """Cached version of text encoding."""
        return self.model.encode(text).tolist()

    def _split_into_chunks(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """Split text into meaningful chunks."""
        # First split by paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_size = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If paragraph is too long, split it into sentences
            if len(paragraph) > max_chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                for sentence in sentences:
                    if current_size + len(sentence) > max_chunk_size and current_chunk:
                        chunks.append(' '.join(current_chunk))
                        current_chunk = []
                        current_size = 0
                    current_chunk.append(sentence)
                    current_size += len(sentence)
            else:
                if current_size + len(paragraph) > max_chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                current_chunk.append(paragraph)
                current_size += len(paragraph)

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def store_document(self, document: Dict[str, Any], filename: str) -> str:
        """Store document content in the vector database."""
        start_time = time.time()
        
        # Generate a unique ID for the document
        doc_id = str(uuid.uuid4())
        
        # Split content into meaningful chunks
        chunks = self._split_into_chunks(document['content'])
        
        # Generate embeddings for chunks
        embeddings = [self._encode_text(chunk) for chunk in chunks]
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{
                "doc_id": doc_id,
                "filename": filename,
                "file_type": document['file_type'],
                "chunk_index": i,
                **document['metadata']
            } for i in range(len(chunks))],
            ids=[f"{doc_id}_{i}" for i in range(len(chunks))]
        )
        
        processing_time = time.time() - start_time
        print(f"Document storage took {processing_time:.2f} seconds")
        
        return doc_id

    def search(self, query: str, document_id: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant content in the vector database."""
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self._encode_text(query)
        
        # Prepare where clause if document_id is provided
        where = {"doc_id": document_id} if document_id else None
        
        # Search in ChromaDB with increased results
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )
        
        # Format results and sort by relevance
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        
        # Sort by distance (lower is better)
        formatted_results.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
        
        processing_time = time.time() - start_time
        print(f"Vector search took {processing_time:.2f} seconds")
        
        return formatted_results

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks from the vector database."""
        try:
            self.collection.delete(
                where={"doc_id": document_id}
            )
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False 