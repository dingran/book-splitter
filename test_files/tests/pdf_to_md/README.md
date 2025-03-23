# PDF to Markdown Splitting Tests

This directory contains test cases for converting PDF files to multiple markdown files.

## Test Commands

```bash
# Basic conversion with default options
python ../../pdf_to_markdown.py ../../input/sample1.pdf --output-dir ./

# Conversion with custom word count
python ../../pdf_to_markdown.py ../../input/large_sample.pdf --max-words 50000 --output-dir ./

# Conversion with strict section boundaries
python ../../pdf_to_markdown.py ../../input/sample2.pdf --strict-boundaries --output-dir ./

# Verbose output for detailed processing information
python ../../pdf_to_markdown.py ../../input/large_sample.pdf --verbose --output-dir ./
```

## Verification Steps

1. Check markdown formatting
   - Page numbers should be preserved as headers
   - Content should be properly formatted with markdown syntax
   - Section breaks should be clearly marked
   
2. Verify word count distribution
   - Each file should be approximately at or below the specified max word count
   - Files should split at logical boundaries when possible
   
3. Check content preservation
   - All pages from the original PDF should be present
   - Text should be properly extracted without major OCR errors
   - Hyphenated words at line breaks should be properly joined
   
4. Check for readability
   - Files should be well-organized with proper spacing
   - Page transitions should be clearly marked
   - Text flow should be natural and readable 