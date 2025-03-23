#!/usr/bin/env python3
"""
Unified Book Splitter - A tool that can split EPUB or PDF files into multiple files
with support for different output formats (Markdown, EPUB, PDF).
"""

import os
import sys
import argparse
from typing import List, Optional

def split_book(input_file: str, 
               output_format: str = 'markdown',
               max_words: int = 80000, 
               output_dir: str = '.', 
               strict_boundaries: bool = False, 
               verbose: bool = False) -> List[str]:
    """
    Split any supported book file (EPUB or PDF) into multiple files of the specified format.
    
    Args:
        input_file: Path to the input book file (EPUB or PDF)
        output_format: Output format ('markdown', 'epub', or 'pdf')
        max_words: Maximum words per output file
        output_dir: Directory for output files
        strict_boundaries: Whether to split only at detected chapter/section boundaries
        verbose: Whether to print verbose output
        
    Returns:
        List of paths to the created files
    """
    input_ext = os.path.splitext(input_file)[1].lower()
    
    # Validate input format
    if input_ext not in ['.epub', '.pdf']:
        print(f"Error: Unsupported input format: {input_ext}")
        print("Supported input formats: .epub, .pdf")
        return []
        
    # Validate output format
    if output_format.lower() not in ['markdown', 'epub', 'pdf']:
        print(f"Error: Unsupported output format: {output_format}")
        print("Supported output formats: markdown, epub, pdf")
        return []
    
    # EPUB to Markdown conversion
    if input_ext == '.epub' and output_format.lower() == 'markdown':
        try:
            from epub_to_markdown import split_epub
            return split_epub(
                input_file=input_file,
                max_words=max_words,
                output_dir=output_dir,
                strict_chapters=strict_boundaries,
                verbose=verbose
            )
        except ImportError:
            print("Error: EPUB to Markdown support not found. Make sure epub_to_markdown.py is in the same directory.")
            return []
            
    # EPUB to EPUB conversion (splitting)
    elif input_ext == '.epub' and output_format.lower() == 'epub':
        try:
            from epub_splitter import split_epub_to_epub
            return split_epub_to_epub(
                input_file=input_file,
                max_words=max_words,
                output_dir=output_dir,
                strict_chapters=strict_boundaries,
                verbose=verbose
            )
        except ImportError:
            print("Error: EPUB to EPUB support not found. Make sure epub_splitter.py is in the same directory.")
            return []
            
    # PDF to Markdown conversion
    elif input_ext == '.pdf' and output_format.lower() == 'markdown':
        try:
            from pdf_to_markdown import split_pdf
            return split_pdf(
                input_file=input_file,
                max_words=max_words,
                output_dir=output_dir,
                strict_boundaries=strict_boundaries,
                verbose=verbose
            )
        except ImportError:
            print("Error: PDF to Markdown support not found. Make sure pdf_to_markdown.py is in the same directory.")
            return []
    
    # PDF to PDF conversion (splitting)
    elif input_ext == '.pdf' and output_format.lower() == 'pdf':
        print("Error: PDF to PDF splitting is not yet implemented.")
        return []
    
    # EPUB to PDF conversion
    elif input_ext == '.epub' and output_format.lower() == 'pdf':
        print("Error: EPUB to PDF conversion is not yet implemented.")
        return []
    
    # PDF to EPUB conversion
    elif input_ext == '.pdf' and output_format.lower() == 'epub':
        print("Error: PDF to EPUB conversion is not yet implemented.")
        return []
    
    return []

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Split a book file (EPUB or PDF) into multiple parts')
    
    parser.add_argument('input_file', help='Path to input book file (EPUB or PDF)')
    parser.add_argument('--output-format', choices=['markdown', 'epub', 'pdf'], default='markdown',
                        help='Output format (default: markdown)')
    parser.add_argument('--max-words', type=int, default=80000,
                        help='Maximum words per output file (default: 80000)')
    parser.add_argument('--output-dir', default='.',
                        help='Directory for output files (default: current directory)')
    parser.add_argument('--strict-boundaries', action='store_true',
                        help='Only split at chapter/section boundaries when possible')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed processing information')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return 1
    
    if not args.input_file.lower().endswith(('.epub', '.pdf')):
        print(f"Error: Input file '{args.input_file}' is not a supported format (EPUB or PDF).")
        return 1
    
    if not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except OSError as e:
            print(f"Error: Cannot create output directory '{args.output_dir}': {e}")
            return 1
    
    if args.max_words <= 0:
        print("Error: Maximum words must be a positive number.")
        return 1
    
    # Display configuration
    print(f"Processing '{args.input_file}'")
    print(f"Output format: {args.output_format}")
    print(f"Maximum words per file: {args.max_words}")
    print(f"Output directory: {args.output_dir}")
    print(f"Strict boundaries: {'Yes' if args.strict_boundaries else 'No'}")
    print(f"Verbose mode: {'Yes' if args.verbose else 'No'}")
    print("---")
    
    try:
        result = split_book(
            input_file=args.input_file,
            output_format=args.output_format,
            max_words=args.max_words,
            output_dir=args.output_dir,
            strict_boundaries=args.strict_boundaries,
            verbose=args.verbose
        )
        
        if result:
            print(f"\nProcessing complete. Created {len(result)} files:")
            for i, output_file in enumerate(result, 1):
                print(f"  {i}. {output_file}")
            return 0
        else:
            print("No output files were created.")
            return 1
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 