# EPUB Splitter - Technical Design

## Architecture

The EPUB Splitter will be implemented as a Python command-line tool with a modular architecture:

```
epub_splitter/
├── epub_splitter.py       # Main script and CLI interface
├── epub_processor.py      # Core logic for processing EPUB files
├── chapter_analyzer.py    # Logic for analyzing and splitting chapters
└── utils.py               # Helper functions
```

## Technology Stack

- **Python 3.7+**: Base language for implementation
- **ebooklib**: For reading and writing EPUB files
- **BeautifulSoup4**: For parsing HTML content within EPUB files
- **NLTK**: For word tokenization and counting
- **argparse**: For command-line argument parsing

## Implementation Details

### 1. EPUB Processing

The tool will use the following approach to process EPUB files:

1. Parse the input EPUB file using ebooklib
2. Extract and analyze the book structure (chapters, sections)
3. Count words in each chapter and determine optimal split points
4. Create new EPUB files for each part, copying necessary assets and metadata
5. Generate appropriate table of contents for each part

### 2. Word Counting

Accurate word counting is crucial for this tool. We'll implement:

- HTML content extraction from each chapter
- Text normalization to handle various formatting
- Word tokenization using NLTK
- Special handling for code blocks, tables, and other non-standard text elements

### 3. Split Point Determination

The algorithm for determining split points will:

1. Scan through chapters sequentially
2. Track cumulative word count
3. When approaching the word limit, identify the nearest chapter boundary
4. Make split decisions based on:
   - Distance to word limit threshold
   - Chapter size
   - User preferences (strict chapter boundary adherence vs. word count limit)

### 4. EPUB Generation

For each output part, the tool will:

1. Create a new EPUB container
2. Copy metadata from the original book
3. Include only the chapters designated for that part
4. Adjust internal links and references when possible
5. Generate a new table of contents
6. Include necessary CSS, images, and other assets

### 5. Command-Line Interface

The CLI will support the following parameters:

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

## Error Handling

The tool will handle various error conditions, including:

- Invalid or corrupted EPUB files
- Permission issues with input or output files
- Unusually structured EPUBs (without clear chapter divisions)
- Single chapters exceeding the word limit

## Performance Considerations

- Lazy loading of EPUB content to minimize memory usage
- Progress indicators for long-running operations
- Efficient text processing algorithms to handle very large books

## Testing Strategy

- Unit tests for core functions (word counting, split point determination)
- Integration tests with sample EPUB files of varying complexity
- Manual testing on popular e-readers to verify compatibility 