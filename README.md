# EPUB Splitter

A set of command-line tools to split large EPUB books into smaller, more manageable parts.

## Features

- Split EPUB files based on word count (default: 80,000 words per part)
- Intelligently split at chapter boundaries when possible
- Two output formats supported:
  - Multiple EPUB files (epub_splitter.py)
  - Multiple Markdown files (epub_to_markdown.py)
- Preserve book structure and content
- Option for strict chapter boundary splitting

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

### Command-line options

Both tools support the same options:

```
usage: epub_splitter.py [-h] [--max-words MAX_WORDS] [--output-dir OUTPUT_DIR] 
                        [--strict-chapters] [--verbose] input_file

Split a large EPUB file into smaller parts

positional arguments:
  input_file            Path to input EPUB file

optional arguments:
  -h, --help            Show this help message and exit
  --max-words MAX_WORDS
                        Maximum words per output file (default: 80000)
  --output-dir OUTPUT_DIR
                        Directory for output files (default: current directory)
  --strict-chapters     Only split at chapter boundaries, even if exceeding word limit
  --verbose             Print detailed processing information
```

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

## Limitations

- Some complex EPUB structures might not be handled perfectly
- Internal links between different parts of the book might be broken after splitting
- Very large chapters cannot be split internally (will be kept as a single unit)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 