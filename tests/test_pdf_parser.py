import unittest
from unittest.mock import patch, MagicMock
import logging

# Assuming the project structure allows this import path
from asmf.parsers.pdf_parser import PDFPatentParser, PatentDocument, PatentClaim

# Disable logging for cleaner test output
logging.disable(logging.CRITICAL)


class TestPDFPatentParserExistingBehavior(unittest.TestCase):
    """
    Tests to characterize the existing behavior of PDFPatentParser before modifications.
    """

    def setUp(self):
        """Set up the parser and mock patent text for each test."""
        self.parser = PDFPatentParser()
        self.full_patent_text = """
        A METHOD FOR PROCESSING DATA

        ABSTRACT
        An abstract describing a novel method for processing data streams efficiently.
        It involves several key steps.

        BACKGROUND
        Some background info.

        CLAIMS
        1. A method, comprising:
        receiving a data stream; and
        processing the data stream.

        2. The method of claim 1, further comprising:
        transmitting the processed data stream.
        """
        self.no_claims_patent_text = """
        A SYSTEM WITH NO CLAIMS

        ABSTRACT
        An abstract for a system that has no claims section in the document.
        """

    @patch("asmf.parsers.pdf_parser.PDFPatentParser._extract_text")
    def test_parse_full_patent_successfully(self, mock_extract_text: MagicMock):
        """
        Verify that a patent with all sections is parsed correctly.
        """
        mock_extract_text.return_value = self.full_patent_text

        doc = self.parser.parse("dummy/path/full_patent.pdf")

        self.assertIsInstance(doc, PatentDocument)
        self.assertEqual(doc.title, "A METHOD FOR PROCESSING DATA")
        self.assertIn("novel method for processing data", doc.abstract)
        self.assertEqual(len(doc.claims), 2)

    @patch("asmf.parsers.pdf_parser.PDFPatentParser._extract_text")
    def test_correctly_identifies_claim_types(self, mock_extract_text: MagicMock):
        """
        Verify that independent and dependent claims are identified correctly.
        """
        mock_extract_text.return_value = self.full_patent_text

        doc = self.parser.parse("dummy/path/full_patent.pdf")

        independent_claims = doc.get_independent_claims()
        dependent_claims = doc.get_dependent_claims()

        self.assertEqual(len(independent_claims), 1)
        self.assertEqual(independent_claims[0].number, 1)
        self.assertEqual(independent_claims[0].claim_type, "independent")

        self.assertEqual(len(dependent_claims), 1)
        self.assertEqual(dependent_claims[0].number, 2)
        self.assertEqual(dependent_claims[0].claim_type, "dependent")
        self.assertEqual(dependent_claims[0].depends_on, [1])

    @patch("asmf.parsers.pdf_parser.PDFPatentParser._extract_text")
    def test_parse_patent_without_claims_returns_empty_list(self, mock_extract_text: MagicMock):
        """
        Verify the NEW behavior that parsing a patent without a claims section
        returns an empty list for claims instead of raising an error.
        """
        mock_extract_text.return_value = self.no_claims_patent_text

        # The parse should complete without raising an error.
        doc = self.parser.parse("dummy/path/no_claims.pdf")

        self.assertIsNotNone(doc, "A document object should be returned.")
        self.assertEqual(doc.claims, [], "The claims list should be empty.")

    @patch("pathlib.Path.exists", return_value=False)
    def test_parse_raises_file_not_found(self, mock_exists: MagicMock):
        """
        Verify that FileNotFoundError is raised for a non-existent PDF.
        """
        with self.assertRaises(FileNotFoundError):
            self.parser.parse("non_existent_file.pdf")


if __name__ == "__main__":
    unittest.main()
