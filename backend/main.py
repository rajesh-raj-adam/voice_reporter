from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from document_processor import DocumentProcessor
from vector_engine import VectorEngine
from nlp_engine import NLEngine
from voice_engine import VoiceEngine

app = FastAPI(title="Document Analysis Agent")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure required directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("audio_output", exist_ok=True)
os.makedirs("vector_storage", exist_ok=True)
os.makedirs("model_cache", exist_ok=True)

# Initialize components
doc_processor = DocumentProcessor()
vector_engine = VectorEngine()
nl_engine = NLEngine()
voice_engine = VoiceEngine()

class Query(BaseModel):
    text: str
    document_id: Optional[str] = None

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
            
        # Save the uploaded file
        file_location = f"uploads/{file.filename}"
        try:
            with open(file_location, "wb+") as file_object:
                file_object.write(await file.read())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
        
        # Process the document
        try:
            doc_content = doc_processor.process_document(file_location)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
        
        # Store in vector database
        try:
            doc_id = vector_engine.store_document(doc_content, file.filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing document in vector database: {str(e)}")
        
        return {"message": "Document processed successfully", "document_id": doc_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/query")
async def query_document(query: Query):
    try:
        if not query.text:
            raise HTTPException(status_code=400, detail="No query text provided")
            
        if not query.document_id:
            raise HTTPException(status_code=400, detail="No document ID provided")
            
        # Get relevant context from vector store
        try:
            context = vector_engine.search(query.text, query.document_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error searching vector database: {str(e)}")
        
        # Generate response using NLP engine
        try:
            response = nl_engine.generate_response(query.text, context)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
        
        # Convert response to speech
        try:
            audio_url = voice_engine.text_to_speech(response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting text to speech: {str(e)}")
        
        return {
            "response": response,
            "audio_url": audio_url,
            "context": context,
            "type": "assistant"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...)):
    try:
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
            
        # Save the audio file
        file_location = f"uploads/{audio_file.filename}"
        try:
            with open(file_location, "wb+") as file_object:
                file_object.write(await audio_file.read())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving audio file: {str(e)}")
        
        # Convert speech to text
        try:
            text = voice_engine.speech_to_text(file_location)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting speech to text: {str(e)}")
        
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 