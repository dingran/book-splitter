# Output Directory

This directory is for storing output files from tests.

Files placed here will be ignored by git.

## Directory Usage

When running tests, output files will be generated here based on the test commands.
These output files can include:

- Split EPUB files
- Markdown files converted from EPUB or PDF
- (Future) Split PDF files

## Clean Up

To clean this directory, you can use:

```bash
rm -f *.epub *.md *.pdf
``` 