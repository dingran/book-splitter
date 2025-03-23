# Unified Interface Tests

This directory contains test cases for the unified `splitter.py` script that can handle both EPUB and PDF files with multiple output formats.

## Test Commands

```bash
# EPUB to Markdown (default)
python ../../splitter.py ../../input/pride_and_prejudice.epub --output-dir ./

# EPUB to EPUB
python ../../splitter.py ../../input/guns_germs.epub --output-format epub --output-dir ./

# PDF to Markdown
python ../../splitter.py ../../input/sample1.pdf --output-dir ./

# Custom word count
python ../../splitter.py ../../input/large_sample.pdf --max-words 40000 --output-dir ./

# Strict boundaries
python ../../splitter.py ../../input/mosquito.epub --strict-boundaries --output-dir ./

# Verbose output
python ../../splitter.py ../../input/pride_and_prejudice.epub --verbose --output-dir ./
```

## Verification Steps

1. Check interface consistency
   - All formats should be processed with the same parameter naming
   - Common behaviors should be consistent across input formats
   
2. Verify format detection
   - EPUB files should be automatically detected and processed correctly
   - PDF files should be automatically detected and processed correctly
   
3. Check output format selection
   - EPUB output should create valid EPUB files
   - Markdown output should create properly formatted markdown files
   
4. Verify parameter handling
   - Custom word counts should be properly applied
   - Strict boundaries option should respect logical boundaries
   - Verbose output should provide useful processing information
   
5. Compare with dedicated scripts
   - Results should be identical to using the dedicated scripts (epub_to_markdown.py, etc.)
   - No loss of functionality when using the unified interface 