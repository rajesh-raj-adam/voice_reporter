import os
from typing import Dict, Any
import PyPDF2
import pandas as pd
from docx import Document
from PIL import Image
import pytesseract
import json
import re
from datetime import datetime

class DocumentProcessor:
    def __init__(self):
        self.supported_extensions = {
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.xlsx': self._process_excel,
            '.xls': self._process_excel,
            '.txt': self._process_text,
            '.jpg': self._process_image,
            '.jpeg': self._process_image,
            '.png': self._process_image
        }

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and return its content in a structured format."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_extension}")

        processor = self.supported_extensions[file_extension]
        content = processor(file_path)
        
        # Clean and preprocess the content
        content = self._clean_content(content)

        return {
            "file_name": os.path.basename(file_path),
            "file_type": file_extension,
            "content": content,
            "metadata": self._extract_metadata(file_path)
        }

    def _clean_content(self, content: str) -> str:
        """Clean and preprocess the extracted content."""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove special characters but keep important punctuation
        content = re.sub(r'[^\w\s.,!?;:()\-\'"]', ' ', content)
        
        # Fix spacing around punctuation
        content = re.sub(r'\s+([.,!?;:])', r'\1', content)
        
        # Remove multiple newlines
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        # Ensure proper paragraph separation
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content

    def _process_pdf(self, file_path: str) -> str:
        """Extract text from PDF files."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text += page_text + "\n\n"
        return text

    def _process_docx(self, file_path: str) -> str:
        """Extract text from DOCX files."""
        doc = Document(file_path)
        paragraphs = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # Only add non-empty paragraphs
                paragraphs.append(paragraph.text)
        return "\n\n".join(paragraphs)

    def _process_excel(self, file_path: str) -> str:
        """Extract text from Excel files."""
        df = pd.read_excel(file_path)
        # Convert DataFrame to a more readable format
        text_parts = []
        
        # Add column names
        text_parts.append("Columns: " + ", ".join(df.columns))
        
        # Add data rows
        for index, row in df.iterrows():
            row_text = f"Row {index + 1}: " + ", ".join(str(val) for val in row)
            text_parts.append(row_text)
        
        return "\n".join(text_parts)

    def _process_text(self, file_path: str) -> str:
        """Extract text from plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Ensure proper paragraph separation
                return re.sub(r'\n\s*\n', '\n\n', content)
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                return re.sub(r'\n\s*\n', '\n\n', content)

    def _process_image(self, file_path: str) -> str:
        """Extract text from images using OCR."""
        try:
            image = Image.open(file_path)
            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error processing image: {e}")
            return ""

    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from the file."""
        stats = os.stat(file_path)
        return {
            "size": stats.st_size,
            "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "file_type": os.path.splitext(file_path)[1].lower(),
            "file_name": os.path.basename(file_path)
        } 