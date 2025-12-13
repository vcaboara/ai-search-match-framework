"""PDF patent parser for extracting claims and metadata."""

import re
from pathlib import Path
from typing import List, Optional
import logging

try:
    import pypdf
    import pdfplumber
except ImportError:
    pypdf = None
    pdfplumber = None

logger = logging.getLogger(__name__)


class PatentClaim:
    """Represents a single patent claim."""

    def __init__(
        self,
        number: int,
        text: str,
        claim_type: str = "unknown",
        depends_on: Optional[List[int]] = None,
    ):
        """Initialize patent claim.

        Args:
            number: Claim number
            text: Full claim text
            claim_type: "independent" or "dependent"
            depends_on: List of claim numbers this depends on
        """
        self.number = number
        self.text = text.strip()
        self.claim_type = claim_type
        self.depends_on = depends_on or []

    def __repr__(self):
        return f"Claim({self.number}, type={self.claim_type})"


class PatentDocument:
    """Parsed patent document with metadata and claims."""

    def __init__(
        self,
        title: Optional[str] = None,
        abstract: Optional[str] = None,
        claims: Optional[List[PatentClaim]] = None,
    ):
        """Initialize patent document.

        Args:
            title: Patent title
            abstract: Patent abstract
            claims: List of parsed claims
        """
        self.title = title
        self.abstract = abstract
        self.claims = claims or []

    def get_independent_claims(self) -> List[PatentClaim]:
        """Get all independent claims."""
        return [c for c in self.claims if c.claim_type == "independent"]

    def get_dependent_claims(self) -> List[PatentClaim]:
        """Get all dependent claims."""
        return [c for c in self.claims if c.claim_type == "dependent"]


class PDFPatentParser:
    """Extract patent claims and metadata from PDF documents."""

    def __init__(self):
        """Initialize PDF parser."""
        if pypdf is None or pdfplumber is None:
            raise ImportError(
                "PDF parsing requires pypdf and pdfplumber. "
                "Install with: pip install pypdf pdfplumber"
            )

    def parse(self, pdf_path: str) -> PatentDocument:
        """Extract patent data from PDF.

        Args:
            pdf_path: Path to patent PDF file

        Returns:
            Parsed PatentDocument

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If claims section not found
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        logger.info(f"Parsing patent PDF: {pdf_file.name}")

        # Extract full text
        text = self._extract_text(pdf_path)

        # Extract components
        title = self._extract_title(text)
        abstract = self._extract_abstract(text)
        claims = self._extract_claims(text)

        logger.info(f"Extracted {len(claims)} claims from {pdf_file.name}")

        return PatentDocument(title=title, abstract=abstract, claims=claims)

    def _extract_text(self, pdf_path: str) -> str:
        """Extract all text from PDF."""
        text_parts = []

        try:
            # Try pdfplumber first (better formatting)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying pypdf: {e}")
            # Fallback to pypdf
            with open(pdf_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text_parts.append(page.extract_text())

        return "\n\n".join(text_parts)

    def _extract_title(self, text: str) -> Optional[str]:
        """Extract patent title."""
        # Look for title patterns at start of document
        lines = text.split("\n")[:20]  # Check first 20 lines
        for i, line in enumerate(lines):
            line = line.strip()
            # Title is usually short and before abstract
            if (
                5 < len(line) < 200
                and not line.isupper()
                and not line.startswith("United States Patent")
            ):
                return line
        return None

    def _extract_abstract(self, text: str) -> Optional[str]:
        """Extract patent abstract."""
        # Look for "ABSTRACT" section
        pattern = r"ABSTRACT\s+(.*?)(?=\n\n[A-Z]|\n\nBACKGROUND|\n\nFIELD)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_claims(self, text: str) -> List[PatentClaim]:
        """Extract and parse all patent claims."""
        claims_section = self._extract_claims_section(text)
        if not claims_section:
            raise ValueError("Claims section not found in document")

        # Split into individual claims
        claim_pattern = r"(\d+)\.\s+(.*?)(?=\n\d+\.\s+|\Z)"
        matches = re.findall(claim_pattern, claims_section, re.DOTALL)

        claims = []
        for number_str, claim_text in matches:
            number = int(number_str)
            claim_text = self._clean_claim_text(claim_text)

            # Determine if independent or dependent
            depends_on = self._parse_claim_dependencies(claim_text)
            claim_type = "dependent" if depends_on else "independent"

            claims.append(
                PatentClaim(
                    number=number,
                    text=claim_text,
                    claim_type=claim_type,
                    depends_on=depends_on,
                )
            )

        return claims

    def _extract_claims_section(self, text: str) -> Optional[str]:
        """Find and extract the claims section."""
        # Look for various claim section headers
        patterns = [
            r"CLAIMS?\s*\n(.*?)(?=\n\n[A-Z]{2,}|\Z)",
            r"What is claimed:?\s*\n(.*?)(?=\n\n[A-Z]{2,}|\Z)",
            r"We claim:?\s*\n(.*?)(?=\n\n[A-Z]{2,}|\Z)",
            r"I claim:?\s*\n(.*?)(?=\n\n[A-Z]{2,}|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _clean_claim_text(self, text: str) -> str:
        """Clean and normalize claim text."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove page numbers
        text = re.sub(r"\n\d+\n", " ", text)
        return text.strip()

    def _parse_claim_dependencies(self, claim_text: str) -> List[int]:
        """Extract which claims this claim depends on.

        Args:
            claim_text: The claim text to analyze

        Returns:
            List of claim numbers this claim depends on
        """
        dependencies = []

        # Pattern: "The method of claim 5"
        pattern1 = r"(?:of|in)\s+claim\s+(\d+)"
        matches = re.findall(pattern1, claim_text, re.IGNORECASE)
        dependencies.extend(int(m) for m in matches)

        # Pattern: "The system of claims 1-3"
        pattern2 = r"(?:of|in)\s+claims\s+(\d+)-(\d+)"
        matches = re.findall(pattern2, claim_text, re.IGNORECASE)
        for start, end in matches:
            dependencies.extend(range(int(start), int(end) + 1))

        # Pattern: "The apparatus of any of claims 1, 2, or 5"
        pattern3 = r"(?:of|in)\s+(?:any of\s+)?claims?\s+([\d,\s]+)"
        matches = re.findall(pattern3, claim_text, re.IGNORECASE)
        for match in matches:
            nums = re.findall(r"\d+", match)
            dependencies.extend(int(n) for n in nums)

        return sorted(list(set(dependencies)))
