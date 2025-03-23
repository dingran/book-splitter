# EPUB to Markdown Splitting Tests

This directory contains test cases for converting EPUB files to multiple markdown files.

## Test Commands

```bash
# Basic conversion with default options
python ../../epub_to_markdown.py ../../input/pride_and_prejudice.epub --output-dir ./

# Conversion with custom word count
python ../../epub_to_markdown.py ../../input/guns_germs.epub --max-words 50000 --output-dir ./

# Conversion with strict chapter boundaries
python ../../epub_to_markdown.py ../../input/mosquito.epub --strict-chapters --output-dir ./

# Verbose output for detailed processing information
python ../../epub_to_markdown.py ../../input/pride_and_prejudice.epub --verbose --output-dir ./
```

## Verification Steps

1. Check markdown formatting
   - Headers should be properly formatted with #, ##, etc.
   - Table of contents should be generated with proper links
   - Chapter content should be preserved with appropriate markdown formatting
   
2. Verify word count distribution
   - Each file should be approximately at or below the specified max word count
   - Files should split at chapter boundaries when possible
   
3. Check content preservation
   - All chapters from the original EPUB should be present
   - Text formatting (italics, bold, etc.) should be converted to markdown syntax
   - Links should be preserved in markdown format
   
4. Check for readability
   - Files should be well-organized with proper spacing
   - Section headers should be clearly distinguished
   - Tables, lists, and other structured content should be properly formatted 