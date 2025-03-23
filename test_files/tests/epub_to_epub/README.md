# EPUB to EPUB Splitting Tests

This directory contains test cases for splitting EPUB files into multiple smaller EPUB files.

## Test Commands

```bash
# Basic splitting with default options
python ../../epub_splitter.py ../../input/pride_and_prejudice.epub --output-dir ./

# Splitting with custom word count
python ../../epub_splitter.py ../../input/guns_germs.epub --max-words 50000 --output-dir ./

# Splitting with strict chapter boundaries
python ../../epub_splitter.py ../../input/mosquito.epub --strict-chapters --output-dir ./

# Verbose output for detailed processing information
python ../../epub_splitter.py ../../input/pride_and_prejudice.epub --verbose --output-dir ./
```

## Verification Steps

1. Check that the output files are valid EPUB files
   - Open in an EPUB reader (e.g., Calibre, Apple Books)
   - Ensure proper formatting and navigation
   
2. Verify word count distribution
   - Each file should be approximately at or below the specified max word count
   - Files should split at chapter boundaries when possible
   
3. Check metadata preservation
   - Title should be updated to indicate part number
   - Author, language, and other metadata should be preserved from original
   
4. Verify embedded assets
   - CSS styles should be preserved
   - Images should be included correctly
   - Internal links should work where possible 