import pytest
from pathlib import Path
from asmf.parsers.pdf_parser import PDFPatentParser

def test_parse_without_claims():
    parser = PDFPatentParser()
    # Use sample PDF without extractable claims
    sample = Path('../ai-patent-eval-standalone/samples/US11046890_Pyrolysis to determine hydrocarbon expulsion efficiency of hydrocarbon source rock.pdf')
    if not sample.exists():
        pytest.skip('Sample PDF not found')
    
    doc = parser.parse(str(sample))
    assert doc.title
    assert doc.abstract
    assert doc.claims == []
