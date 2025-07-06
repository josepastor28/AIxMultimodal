import os
import tempfile
from typing import List, Dict, Any
from haystack.schema import Document
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process uploaded documents and convert them to Haystack Document objects"""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.docx', '.doc', '.txt'}
    
    def process_uploaded_file(self, file_content: bytes, filename: str, file_type: str) -> List[Document]:
        """Process an uploaded file and return Haystack Document objects"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # Process based on file type
            if filename.lower().endswith('.pdf'):
                return self._process_pdf(temp_file_path, filename)
            elif filename.lower().endswith(('.docx', '.doc')):
                return self._process_word(temp_file_path, filename)
            elif filename.lower().endswith('.txt'):
                return self._process_text(temp_file_path, filename)
            else:
                raise ValueError(f"Unsupported file type: {filename}")
                
        except Exception as e:
            logger.error(f"❌ Failed to process file {filename}: {e}")
            raise
        finally:
            # Clean up temporary file
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
    
    def _process_pdf(self, file_path: str, filename: str) -> List[Document]:
        """Process PDF files"""
        try:
            from haystack.nodes import PDFToTextConverter
            
            converter = PDFToTextConverter()
            documents = converter.convert(file_path=file_path)
            
            # Add metadata
            for doc in documents:
                doc.meta.update({
                    "filename": filename,
                    "file_type": "pdf",
                    "source": "upload"
                })
            
            logger.info(f"✅ Processed PDF file: {filename} -> {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Failed to process PDF {filename}: {e}")
            # Fallback: create a single document with error message
            return [Document(
                content=f"Error processing PDF file {filename}: {str(e)}",
                meta={"filename": filename, "file_type": "pdf", "source": "upload", "error": True}
            )]
    
    def _process_word(self, file_path: str, filename: str) -> List[Document]:
        """Process Word documents"""
        try:
            from haystack.nodes import DocxToTextConverter
            
            converter = DocxToTextConverter()
            documents = converter.convert(file_path=file_path)
            
            # Add metadata
            for doc in documents:
                doc.meta.update({
                    "filename": filename,
                    "file_type": "word",
                    "source": "upload"
                })
            
            logger.info(f"✅ Processed Word file: {filename} -> {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Failed to process Word file {filename}: {e}")
            # Fallback: create a single document with error message
            return [Document(
                content=f"Error processing Word file {filename}: {str(e)}",
                meta={"filename": filename, "file_type": "word", "source": "upload", "error": True}
            )]
    
    def _process_text(self, file_path: str, filename: str) -> List[Document]:
        """Process text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a single document
            document = Document(
                content=content,
                meta={
                    "filename": filename,
                    "file_type": "text",
                    "source": "upload"
                }
            )
            
            logger.info(f"✅ Processed text file: {filename}")
            return [document]
            
        except Exception as e:
            logger.error(f"❌ Failed to process text file {filename}: {e}")
            return [Document(
                content=f"Error processing text file {filename}: {str(e)}",
                meta={"filename": filename, "file_type": "text", "source": "upload", "error": True}
            )]
    
    def validate_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate uploaded file"""
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.supported_extensions:
            return {
                "valid": False,
                "message": f"Unsupported file type: {file_ext}. Supported types: {', '.join(self.supported_extensions)}"
            }
        
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            return {
                "valid": False,
                "message": f"File too large: {file_size / (1024*1024):.1f}MB. Maximum size: 50MB"
            }
        
        return {
            "valid": True,
            "message": "File validation passed"
        }

# Global instance
document_processor = DocumentProcessor() 