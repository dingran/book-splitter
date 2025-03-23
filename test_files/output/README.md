# EPUB and PDF Splitter

A set of command-line tools to split large EPUB and PDF books into smaller, more manageable parts.

## Features

- Split EPUB files based on word count (default: 80,000 words per part)
- Split PDF files based on word count and page boundaries
- Intelligently split at chapter boundaries when possible
- Multiple output formats supported:
  - Multiple EPUB files
  - Multiple Markdown files
  - (Future support for PDF output)
- Preserve book structure and content
- Option for strict chapter boundary splitting
- Unified command-line interface for all formats

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/dingran/epub-splitter.git
cd epub-splitter
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Unified Splitter (Recommended)

The easiest way to use this tool is through the unified `splitter.py` script:

```bash
python splitter.py my_book.epub
python splitter.py my_book.pdf
```

By default, this will convert your input file to multiple markdown files. You can specify the output format:

```bash
python splitter.py my_book.epub --output-format epub
python splitter.py my_book.pdf --output-format markdown
```

### EPUB to EPUB Splitting

Basic usage:

```bash
python epub_splitter.py my_book.epub
```

This will split `my_book.epub` into multiple EPUB files with a maximum of 80,000 words each, preferring to split at chapter boundaries.

### EPUB to Markdown Splitting

To convert an EPUB to multiple markdown files:

```bash
python epub_to_markdown.py my_book.epub
```

This will split `my_book.epub` into multiple markdown (.md) files with a maximum of 80,000 words each. Each markdown file will include a table of contents and chapter headers.

### PDF to Markdown Splitting

To convert a PDF to multiple markdown files:

```bash
python pdf_to_markdown.py my_book.pdf
```

This will split `my_book.pdf` into multiple markdown (.md) files with a maximum of 80,000 words each. Each markdown file will include page numbers and word counts.

### Command-line options for the unified splitter

```
usage: splitter.py [-h] [--output-format {markdown,epub,pdf}] [--max-words MAX_WORDS] 
                   [--output-dir OUTPUT_DIR] [--strict-boundaries] [--verbose] input_file

Split a book file (EPUB or PDF) into multiple parts

positional arguments:
  input_file            Path to input book file (EPUB or PDF)

optional arguments:
  -h, --help            Show this help message and exit
  --output-format {markdown,epub,pdf}
                        Output format (default: markdown)
  --max-words MAX_WORDS
                        Maximum words per output file (default: 80000)
  --output-dir OUTPUT_DIR
                        Directory for output files (default: current directory)
  --strict-boundaries   Only split at chapter/section boundaries when possible
  --verbose             Print detailed processing information
```

Note: Individual tools use `--strict-chapters` or `--strict-boundaries` depending on the script, but the unified splitter standardizes on `--strict-boundaries` for all formats.

### Examples

Split a book with a maximum of 50,000 words per part:

```bash
python epub_to_markdown.py --max-words 50000 my_book.epub
```

Only split at chapter boundaries, even if it means some parts might be larger than the word limit:

```bash
python epub_splitter.py --strict-chapters my_book.epub
```

Output files to a specific directory and show detailed processing information:

```bash
python epub_to_markdown.py --output-dir ./split_books --verbose my_book.epub
```

Split a PDF book with detailed processing information:

```bash
python pdf_to_markdown.py --verbose my_book.pdf
```

Use the unified splitter to convert an EPUB to markdown with custom word count:

```bash
python splitter.py --output-format markdown --max-words 50000 my_book.epub
```

## Project Structure

The project includes these main components:

- **`splitter.py`** - Unified tool that handles both EPUB and PDF conversion to various formats
  - Serves as the main entry point with a standardized interface
  - Can process both EPUB and PDF files as input
  - Supports multiple output formats (markdown, EPUB, with PDF planned for future)
  - Provides a consistent command-line interface for all operations

- **`epub_splitter.py`** - Tool for splitting EPUB files into multiple EPUB files
  - Contains the `split_epub_to_epub` function for processing EPUBs
  - Maintains chapter boundaries and book structure
  - Preserves metadata, CSS, images, and other assets from the original EPUB

- **`epub_to_markdown.py`** - Tool for converting EPUB files to markdown
  - Extracts chapter content from EPUB files
  - Formats the content as markdown with proper headers and links
  - Creates tables of contents for each output file
  - Splits content into multiple files based on word count

- **`pdf_to_markdown.py`** - Tool for converting PDF files to markdown
  - Extracts text from PDF pages using multiple extraction methods for accuracy
  - Detects section boundaries where possible
  - Preserves page numbers in the output markdown
  - Cleans up common OCR and formatting issues

- **`epub_processor.py`** - Core library for handling EPUB processing
  - Contains the `EPUBProcessor` class that manages EPUB manipulation
  - Handles chapter extraction, word counting, and split point determination
  - Preserves metadata and assets between split files
  - Used by epub_splitter.py to perform the actual EPUB splitting

- **`requirements.txt`** - Required Python packages for running the tools
- **`LICENSE`** - MIT License for the project
- **`technical_design.md`** - Technical design documentation explaining architecture decisions

## Code Organization

The codebase is modular and follows these design principles:

1. **Separation of concerns**: Each file focuses on a specific task (EPUB splitting, PDF processing, etc.)
2. **Common interfaces**: Similar functions across files follow the same parameter patterns
3. **Unified frontend**: The `splitter.py` script provides a single entry point for all functionality
4. **Error handling**: Comprehensive error checking with informative messages
5. **Documentation**: Detailed docstrings and command-line help

The unified interface in `splitter.py` makes it easy to use for most common tasks, while the specialized scripts provide more tailored functionality for specific use cases.

## Limitations

- Some complex EPUB structures might not be handled perfectly
- Internal links between different parts of the book might be broken after splitting
- Very large chapters cannot be split internally (will be kept as a single unit)
- PDF extraction quality depends on the PDF structure; scanned PDFs may have lower quality text extraction
- Some PDF formatting and layout may be lost in the conversion to markdown

## License

This project is licensed under the MIT License - see the LICENSE file for details. 