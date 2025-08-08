import os
import logging
from typing import Optional, Dict
import PyPDF2
from werkzeug.utils import secure_filename
from config import Config

logger = logging.getLogger(__name__)

class FileProcessor:
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def process_file(file) -> Dict:
        """Process uploaded file and extract text content."""
        try:
            if not file or file.filename == '':
                raise ValueError("No file provided")
            
            if not FileProcessor.allowed_file(file.filename):
                raise ValueError(f"File type not allowed. Supported types: {', '.join(Config.ALLOWED_EXTENSIONS)}")
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > Config.MAX_FILE_SIZE:
                raise ValueError(f"File too large. Maximum size: {Config.MAX_FILE_SIZE / (1024*1024):.1f}MB")
            
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            logger.debug(f"Processing file: {filename} ({file_size} bytes)")
            
            if file_extension == 'pdf':
                content = FileProcessor._extract_pdf_text(file)
            elif file_extension == 'txt':
                content = FileProcessor._extract_text_content(file)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            return {
                "filename": filename,
                "size": file_size,
                "type": file_extension,
                "content": content,
                "word_count": len(content.split()) if content else 0
            }
            
        except Exception as e:
            logger.error(f"File processing error: {e}")
            raise
    
    @staticmethod
    def _extract_pdf_text(file) -> str:
        """Extract text from PDF file."""
        try:
            reader = PyPDF2.PdfReader(file)
            text_content = []
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(page_text)
                    logger.debug(f"Extracted text from page {page_num + 1}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            if not text_content:
                raise ValueError("No readable text found in PDF")
            
            full_text = "\n\n".join(text_content)
            logger.debug(f"Successfully extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    @staticmethod
    def _extract_text_content(file) -> str:
        """Extract text from plain text file."""
        try:
            content = file.read().decode('utf-8')
            if not content.strip():
                raise ValueError("Text file is empty")
            
            logger.debug(f"Successfully extracted {len(content)} characters from text file")
            return content
            
        except UnicodeDecodeError:
            logger.error("File encoding error")
            raise ValueError("File must be UTF-8 encoded text")
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise ValueError(f"Failed to process text file: {str(e)}")
