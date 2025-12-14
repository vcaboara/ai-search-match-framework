# Context for ai-search-match-framework Update

## Issue
The `PDFPatentParser` in `asmf.parsers` currently **requires** a "Claims" section in PDFs and raises an error if not found. This breaks the patent learning feature.

## Location
Repository: `C:\Users\vcabo\ai-search-match-framework`
File: Likely `src/asmf/parsers/pdf_parser.py` or similar

## Required Change
Make the Claims section **optional** in PDFPatentParser:

```python
# Current behavior (breaks):
if "Claims" not in text:
    raise ValueError("Claims section not found in document")

# Needed behavior:
if "Claims" not in text:
    logger.warning("No claims section found, continuing with title/abstract only")
    claims = []  # Empty list instead of error
```

## Why
Many patents from patents.google.com (especially published applications) don't have extractable claims sections. We need to:

1. **Learn** from patents even without claims (title + abstract have technical details)
2. **Analyze** patents that DO have claims (current functionality)

## Test Case
These sample PDFs have NO claims section:
- `US11046890_Pyrolysis to determine hydrocarbon expulsion efficiency of hydrocarbon source rock.pdf`
- `US20230045385A1_high-fixed-carbon-material-from-pyrolysis.pdf`

## Expected Result After Fix
```python
from asmf.parsers import PDFPatentParser

parser = PDFPatentParser()
doc = parser.parse("patent_without_claims.pdf")

# Should work:
assert doc.title is not None
assert doc.abstract is not None  
assert doc.claims == []  # Empty, not error!
```

## Changes Needed in asmf

1. **Make claims optional** in parser
2. **Add test** for PDFs without claims
3. **Keep backward compatibility** - existing code expecting claims should still work

## Priority
High - blocking the patent learning feature in ai-patent-eval-standalone

## Context
The ai-patent-eval-standalone repo depends on this fix to enable:
- Learning from existing patents (building knowledge base)
- Training data generation for model fine-tuning
- Flexibility with different patent document formats

## Files to Check in asmf
- `src/asmf/parsers/pdf_parser.py` (or wherever PDFPatentParser is)
- `src/asmf/parsers/__init__.py` 
- `tests/` - add test for no-claims case

## Related Issue
See: ai-patent-eval-standalone PR #2 - "Handle patents without claims section"
