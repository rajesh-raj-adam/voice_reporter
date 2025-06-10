from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from typing import List, Dict, Any
import torch
from functools import lru_cache
import time

class NLEngine:
    def __init__(self):
        # Initialize with a model better suited for question answering
        self.model_name = "google/flan-t5-base"  # Better for QA tasks
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        
        # Move model to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Enable model optimization
        self.model.eval()  # Set to evaluation mode
        if self.device == "cuda":
            self.model = self.model.half()  # Use FP16 for faster inference

    @lru_cache(maxsize=100)
    def _generate_cached(self, prompt: str) -> str:
        """Cached version of text generation to avoid redundant computations."""
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=150,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                num_beams=4,
                repetition_penalty=1.2  # Prevent repetitive responses
            )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def generate_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate a response based on the query and context."""
        start_time = time.time()
        
        # Prepare the context - use more context items
        context_text = "\n".join([item["content"] for item in context[:5]])  # Increased from 3 to 5
        
        # Create a better prompt that guides the model for list-type questions
        prompt = f"""Context: {context_text}

Question: {query}

Based on the above context, please provide a complete and comprehensive answer. If the question asks for a list, make sure to include ALL items from the context. If the answer cannot be found in the context, say so.

Answer:"""
        
        # Generate response with increased max length
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)  # Increased from 512
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=300,  # Increased from 150
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                num_beams=4,
                repetition_penalty=1.2
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up response
        response = response.replace(prompt, "").strip()
        
        # If response is too short or repetitive, use a fallback
        if len(response) < 20 or response.count(response[:20]) > 1:
            if context_text:
                response = "Based on the document, I can see that it contains information, but I need more specific context to answer your question accurately. Could you please rephrase your question or ask about a specific aspect of the document?"
            else:
                response = "I couldn't find relevant information in the document to answer your question. Could you please try rephrasing your question or ask about a different aspect of the document?"
        
        processing_time = time.time() - start_time
        print(f"Response generation took {processing_time:.2f} seconds")
        
        return response

    def analyze_document(self, content: str) -> Dict[str, Any]:
        """Analyze document content and extract key insights."""
        start_time = time.time()
        
        # Prepare the prompt
        prompt = f"""Please analyze the following document and provide a summary and key points:

Document: {content[:1000]}

Please provide:
1. A brief summary
2. Key points or main topics
3. Any notable details

Analysis:"""
        
        # Generate analysis
        analysis = self._generate_cached(prompt)
        
        processing_time = time.time() - start_time
        print(f"Document analysis took {processing_time:.2f} seconds")
        
        return {
            "summary": analysis,
            "key_points": analysis.split("\n"),
            "processing_time": f"{processing_time:.2f} seconds"
        }

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze the sentiment of the text."""
        start_time = time.time()
        
        # Prepare the prompt
        prompt = f"""Please analyze the sentiment of the following text:

Text: {text[:200]}

Please provide:
1. Overall sentiment (positive, negative, or neutral)
2. Brief explanation

Analysis:"""
        
        # Generate sentiment
        sentiment = self._generate_cached(prompt)
        
        processing_time = time.time() - start_time
        print(f"Sentiment analysis took {processing_time:.2f} seconds")
        
        return sentiment 