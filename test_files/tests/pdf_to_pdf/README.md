# PDF to PDF Splitting Tests

**Note: This feature is planned for future implementation.**

This directory will contain test cases for splitting PDF files into multiple smaller PDF files.

## Planned Test Commands

```bash
# These commands are planned for when the feature is implemented
python ../../splitter.py ../../input/sample1.pdf --output-format pdf --output-dir ./
python ../../splitter.py ../../input/large_sample.pdf --output-format pdf --max-words 50000 --output-dir ./
python ../../splitter.py ../../input/sample2.pdf --output-format pdf --strict-boundaries --output-dir ./
```

## Verification Steps (For Future Implementation)

1. Check that the output files are valid PDF files
   - Open in a PDF reader (e.g., Adobe Acrobat, Preview)
   - Ensure proper formatting and pagination
   
2. Verify page count distribution
   - Each file should have an appropriate number of pages
   - Files should split at logical boundaries when possible
   
3. Check metadata preservation
   - Title should be updated to indicate part number
   - Author, creation date, and other metadata should be preserved
   
4. Verify formatting
   - Fonts should be preserved
   - Images should be included correctly
   - Layout should be maintained 