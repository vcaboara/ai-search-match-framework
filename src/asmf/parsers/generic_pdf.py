"""Generic PDF text extraction."""

import logging
from pathlib import Path
from typing import Optional

try:
    import pypdf
except ImportError:
    pypdf = None

logger = logging.getLogger(__name__)


class PDFParser:
    """Generic PDF text extractor for documents.
    
    Example:
        >>> parser = PDFParser("document.pdf")
        >>> text = parser.extract_text()
        >>> print(text[:100])
    """
    
    def __init__(self, pdf_path: str):
        """Initialize PDF parser.
        
        Args:
            pdf_path: Path to PDF file
            
        Raises:
            ImportError: If pypdf is not installed
            FileNotFoundError: If PDF file doesn't exist
        """
        if pypdf is None:
            raise ImportError(
                "pypdf is required for PDF parsing. "
                "Install with: pip install pypdf"
            )
        
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.debug(f"Initialized PDFParser for {self.pdf_path}")
    
    def extract_text(self) -> str:
        """Extract all text from PDF.
        
        Returns:
            Extracted text with pages separated by double newlines
            
        Raises:
            ValueError: If PDF cannot be read or parsed
        """
        try:
            text_parts = []
            with open(self.pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                
                logger.debug(f"PDF has {len(reader.pages)} pages")
                
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(page_text)
                        logger.debug(f"Extracted {len(page_text)} chars from page {page_num}")
            
            if not text_parts:
                logger.warning(f"No text extracted from {self.pdf_path}")
                return ""
            
            full_text = '\n\n'.join(text_parts)
            logger.info(f"Extracted {len(full_text)} total characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise ValueError(f"Could not extract text from PDF: {e}")
