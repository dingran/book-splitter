# Test Files for EPUB and PDF Splitter

This directory contains files and test cases for the EPUB and PDF splitter project.

## Directory Structure

- **input/** - Contains source EPUB and PDF files for testing
- **output/** - Directory for storing output files from regular use
- **tests/** - Structured test cases for different conversion types
  - **epub_to_epub/** - Tests for EPUB to EPUB conversion
  - **epub_to_md/** - Tests for EPUB to Markdown conversion
  - **pdf_to_md/** - Tests for PDF to Markdown conversion
  - **pdf_to_pdf/** - Tests for PDF to PDF conversion (future feature)
  - **unified_interface/** - Tests for the unified interface (splitter.py)

## Running Tests

Each test directory contains a README.md with:
1. Specific test commands to run
2. Verification steps to check if the tests pass
3. Expected output and behavior

To run all tests, you can execute the commands in each test directory or use the provided test scripts.

## Adding New Test Files

When adding new test files:
1. Place source files in the `input/` directory
2. Add a note about the file's characteristics (size, language, complexity)
3. For reference outputs, place them in the appropriate test directory

## Cleanup

To clean up test outputs, run:
```bash
rm tests/*/*.epub tests/*/*.md
```

This will remove the generated files while preserving the test structure and READMEs. 