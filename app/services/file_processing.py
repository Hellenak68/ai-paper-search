import os
import uuid
import aiofiles
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from app.core.config import settings


class PDFProcessor:
    """PDF processing service for text extraction and chunking"""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    async def save_uploaded_file(self, file: UploadFile, upload_dir: str) -> str:
        """Save uploaded file to disk"""
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Create directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path, unique_filename
    
    def extract_text_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PyPDF2 extraction failed: {str(e)}")
    
    def extract_text_pymupdf(self, file_path: str) -> str:
        """Extract text using PyMuPDF (fallback)"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text() + "\n"
            doc.close()
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PyMuPDF extraction failed: {str(e)}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF with fallback methods"""
        # Try PyPDF2 first
        try:
            text = self.extract_text_pypdf2(file_path)
            if text.strip():  # If we got meaningful text
                return text
        except:
            pass
        
        # Fallback to PyMuPDF
        try:
            text = self.extract_text_pymupdf(file_path)
            if text.strip():
                return text
        except:
            pass
        
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            # Estimate page number (rough approximation)
            estimated_page = (i // self.chunk_size) + 1
            
            chunks.append({
                "text": chunk_text,
                "chunk_index": len(chunks),
                "estimated_page": estimated_page,
                "word_count": len(chunk_words)
            })
        
        return chunks
    
    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process PDF file and return extracted chunks"""
        # Extract text
        text = self.extract_text(file_path)
        
        # Chunk text
        chunks = self.chunk_text(text)
        
        return {
            "full_text": text,
            "chunks": chunks,
            "total_chunks": len(chunks),
            "total_words": len(text.split())
        }


# Global instance
pdf_processor = PDFProcessor()
