# EPUB Splitter - Product Requirements

## Overview
EPUB Splitter is a command-line tool designed to split large EPUB books into smaller, more manageable parts. This is particularly useful for e-readers with performance issues when handling large books or for readers who prefer to track their progress through shorter segments.

## Core Requirements

1. **Input/Output**
   - Accept an EPUB file as input
   - Generate multiple smaller EPUB files as output
   - Maintain a logical naming convention for output files (e.g., original_name_part1.epub, original_name_part2.epub)

2. **Splitting Logic**
   - Primary constraint: Maximum of 80,000 words per output file
   - Prioritize splitting at chapter boundaries
   - Only split within chapters when absolutely necessary (when a single chapter exceeds the word limit)
   - Preserve the original book's structure, metadata, and formatting

3. **Content Handling**
   - Preserve all images, tables, and other media
   - Maintain proper table of contents in each output file
   - Correctly handle CSS styling and formatting
   - Preserve hyperlinks and references when possible

4. **User Interface**
   - Command-line interface with clear options and help information
   - Allow users to specify maximum word count (default: 80,000)
   - Allow users to specify output directory
   - Provide verbose mode for detailed processing information

## Optional Features

1. **Advanced Options**
   - Option to force splits only at chapter boundaries, even if it means exceeding the word limit
   - Option to split by page count instead of word count
   - Preview mode to show how the book will be split without actually creating files

2. **Quality Assurance**
   - Verify generated EPUBs are valid and can be opened by common e-readers
   - Generate a log file with details about the splitting process

3. **Performance**
   - Efficiently handle very large EPUB files
   - Provide progress indicators for long-running operations

## Technical Requirements

1. **Dependencies**
   - Minimal external dependencies
   - Cross-platform compatibility (Linux, macOS, Windows)

2. **Code Quality**
   - Well-documented code
   - Error handling for various input file issues
   - Unit tests for core functionality 