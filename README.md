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
git clone https://github.com/yourusername/epub_splitter.git
cd epub_splitter
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

## Limitations

- Some complex EPUB structures might not be handled perfectly
- Internal links between different parts of the book might be broken after splitting
- Very large chapters cannot be split internally (will be kept as a single unit)
- PDF extraction quality depends on the PDF structure; scanned PDFs may have lower quality text extraction
- Some PDF formatting and layout may be lost in the conversion to markdown

## License

This project is licensed under the MIT License - see the LICENSE file for details. 