"""Document parsers for various file formats."""

from .pdf_parser import PDFPatentParser, PatentClaim, PatentDocument
from .generic_pdf import PDFParser

__all__ = [
    "PDFParser",            # Generic PDF text extraction
    "PDFPatentParser",      # Domain-specific patent parser  
    "PatentClaim",
    "PatentDocument",
]
