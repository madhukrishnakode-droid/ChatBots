"""
Resume Parser Module
Handles extraction of text from various file formats (PDF, DOCX, TXT, Images)
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Optional imports for document processing
try:
    import pytesseract  # type: ignore
except ImportError:
    pytesseract = None

try:
    from pdf2image import convert_from_path  # type: ignore
except ImportError:
    convert_from_path = None

try:
    from PIL import Image  # type: ignore
except ImportError:
    Image = None

try:
    from docx import Document  # type: ignore
except ImportError:
    Document = None

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Parses resumes from multiple file formats and extracts raw text
    """
    
    SUPPORTED_FORMATS = {'pdf', 'txt', 'docx', 'jpg', 'jpeg', 'png'}
    
    def __init__(self):
        self.extracted_text = ""
        self.file_type = None
    
    def parse(self, file_path: str) -> Tuple[str, str]:
        """
        Parse resume from file and return extracted text
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Tuple of (extracted_text, file_type)
        """
        file_path_str = str(file_path)
        file_path_obj = Path(file_path_str)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path_str}")
        
        file_ext = file_path_obj.suffix.lower().lstrip('.')
        
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        text = ""
        try:
            if file_ext == 'pdf':
                text = self._parse_pdf(file_path_str)
            elif file_ext == 'docx':
                text = self._parse_docx(file_path_str)
            elif file_ext == 'txt':
                text = self._parse_txt(file_path_str)
            elif file_ext in {'jpg', 'jpeg', 'png'}:
                text = self._parse_image(file_path_str)
            
            self.extracted_text = text
            self.file_type = file_ext
            return text, file_ext
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise
    
    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF using OCR"""
        logger.info(f"Parsing PDF: {file_path}")
        
        try:
            if convert_from_path is None or pytesseract is None:
                logger.warning("pdf2image or pytesseract not available")
                # Try pdfplumber fallback
                try:
                    import pdfplumber  # type: ignore
                    text_content = []
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages[:5]:
                            text = page.extract_text()
                            if text:
                                text_content.append(text)
                    return "\n".join(text_content) if text_content else "Unable to extract text from PDF"
                except Exception:
                    return "PDF content could not be extracted. Please use TXT, DOCX, or image formats instead."
            
            # Try using pdf2image with Poppler
            try:
                images = convert_from_path(file_path, first_page=1, last_page=5)
                all_text = []
                for page_num, image in enumerate(images):
                    logger.info(f"Processing page {page_num + 1}")
                    text = pytesseract.image_to_string(image, lang='eng')
                    all_text.append(text)
                return "\n".join(all_text)
            except Exception as pdf_error:
                logger.warning(f"PDF to image conversion failed: {str(pdf_error)}, trying alternative method")
                try:
                    import pdfplumber  # type: ignore
                    text_content = []
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages[:5]:
                            text = page.extract_text()
                            if text:
                                text_content.append(text)
                    return "\n".join(text_content) if text_content else "Unable to extract text from PDF"
                except ImportError:
                    logger.warning("pdfplumber not available, returning placeholder")
                    return "PDF content could not be extracted. Please use TXT, DOCX, or image formats instead."
        
        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}")
            return "Unable to extract text from PDF. The file may be corrupt, empty, or an invalid format."
    
    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        logger.info(f"Parsing DOCX: {file_path}")
        
        if Document is None:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")
        
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"DOCX parsing error: {str(e)}")
            raise
    
    def _parse_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        logger.info(f"Parsing TXT: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            logger.error(f"TXT parsing error: {str(e)}")
            raise
    
    def _parse_image(self, file_path: str) -> str:
        """Extract text from image using OCR (Tesseract)"""
        logger.info(f"Parsing Image: {file_path}")
        
        if pytesseract is None or Image is None:
            raise ImportError("pytesseract or PIL not installed. Install with: pip install pytesseract pillow")
        
        try:
            image = Image.open(file_path)
            # Enhance image for better OCR
            image = image.convert('RGB')
            text = pytesseract.image_to_string(image, lang='eng')
            return text
        except Exception as e:
            logger.error(f"Image parsing error: {str(e)}")
            raise
    
    def get_sections(self, text: str) -> Dict[str, str]:
        """
        Try to identify resume sections
        This is a simple heuristic-based approach
        """
        sections = {
            'contact': '',
            'summary': '',
            'experience': '',
            'education': '',
            'skills': '',
            'certifications': ''
        }
        
        text_lower = text.lower()
        
        # Look for section headers
        section_keywords = {
            'contact': ['contact', 'email', 'phone', 'linkedin'],
            'summary': ['summary', 'objective', 'professional summary'],
            'experience': ['experience', 'employment', 'work history'],
            'education': ['education', 'qualifications', 'degree'],
            'skills': ['skills', 'technical skills', 'competencies'],
            'certifications': ['certifications', 'certificates', 'certifications']
        }
        
        current_section = 'contact'
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            for section, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    current_section = section
                    break
            
            sections[current_section] += line + '\n'
        
        return sections


# Test function
if __name__ == "__main__":
    parser = ResumeParser()
    print("Resume Parser initialized successfully")
