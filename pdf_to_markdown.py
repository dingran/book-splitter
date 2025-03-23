#!/usr/bin/env python3
"""
PDF to Markdown Splitter - Splits a PDF file into multiple markdown files based on page count.
"""

import os
import sys
import re
import argparse
import io
from pathlib import Path
from typing import List, Dict, Any, Tuple
import PyPDF2
from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFPage

def count_words(text: str) -> int:
    """Count words in text using a simple regex approach."""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Count words (sequences of alphanumeric characters)
    words = re.findall(r'\w+', text)
    return len(words)

def extract_text_from_pdf(pdf_path: str, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Extract text from PDF file, page by page.
    
    Args:
        pdf_path: Path to the PDF file
        verbose: Whether to print verbose output
        
    Returns:
        List of dictionaries with page number, text, and word count
    """
    if verbose:
        print(f"Extracting text from {pdf_path}...")
    
    pages = []
    
    # Use PyPDF2 to get total page count and basic metadata
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)
        
        # Extract document info if available
        title = None
        if reader.metadata:
            title = reader.metadata.title
        
        # Use pdfminer for better text extraction
        for page_num in range(total_pages):
            if verbose and page_num % 10 == 0:
                print(f"  Processing page {page_num + 1}/{total_pages}...")
                
            # Extract using PyPDF2 first
            page = reader.pages[page_num]
            text = page.extract_text()
                
            # If PyPDF2 extraction is poor, try pdfminer
            if not text or len(text.strip()) < 100:
                # Re-open file for pdfminer
                with open(pdf_path, 'rb') as miner_file:
                    # Skip to the desired page
                    pdf_pages = list(PDFPage.get_pages(miner_file, 
                                                      pagenos=[page_num], 
                                                      maxpages=1))
                    if pdf_pages:
                        # Use StringIO to capture the text
                        output = io.StringIO()
                        text = extract_text(pdf_path, page_numbers=[page_num])
            
            # Count words
            word_count = count_words(text)
            
            pages.append({
                'page_num': page_num + 1,
                'text': text,
                'word_count': word_count
            })
            
            if verbose:
                if page_num % 10 == 0 or page_num == total_pages - 1:
                    print(f"  Page {page_num + 1}: {word_count} words")
    
    total_words = sum(page['word_count'] for page in pages)
    if verbose:
        print(f"Extracted {total_pages} pages with a total of {total_words} words.")
    
    return pages, title

def determine_split_points(pages: List[Dict[str, Any]], 
                          max_words: int, 
                          strict_boundaries: bool = False,
                          verbose: bool = False) -> List[int]:
    """
    Determine where to split the PDF.
    
    Args:
        pages: List of page dictionaries with text and word count
        max_words: Maximum words per output file
        strict_boundaries: Whether to split only at detected section boundaries
        verbose: Whether to print verbose output
        
    Returns:
        List of indices of the last page in each part
    """
    if verbose:
        print("Determining split points...")
    
    # Try to detect section/chapter boundaries
    section_boundaries = detect_section_boundaries(pages)
    
    split_points = []
    current_word_count = 0
    current_pages = []
    
    for i, page in enumerate(pages):
        # Check if adding this page would exceed the word limit
        if current_word_count + page['word_count'] > max_words and current_pages:
            # Find the nearest section boundary if strict mode is enabled
            if strict_boundaries and section_boundaries:
                # Find the closest boundary before current position
                closest_boundary = None
                for boundary in section_boundaries:
                    if boundary <= i:
                        if closest_boundary is None or boundary > closest_boundary:
                            closest_boundary = boundary
                
                # If a nearby boundary is found (within 20% of max_words)
                if closest_boundary is not None and closest_boundary > i - 5:
                    # Split at the boundary
                    split_points.append(closest_boundary)
                    current_word_count = sum(p['word_count'] for p in pages[closest_boundary+1:i+1])
                    current_pages = pages[closest_boundary+1:i+1]
                    continue
            
            # Otherwise split at current position
            split_points.append(i - 1)
            current_word_count = page['word_count']
            current_pages = [page]
        else:
            # Add page to current part
            current_pages.append(page)
            current_word_count += page['word_count']
    
    # Add the last part if there are remaining pages
    if current_pages:
        split_points.append(len(pages) - 1)
    
    # Log split information
    if verbose:
        part_start = 0
        for i, split_point in enumerate(split_points):
            part_pages = pages[part_start:split_point + 1]
            part_words = sum(p['word_count'] for p in part_pages)
            print(f"  Part {i+1}: Pages {part_start+1}-{split_point+1} ({part_words} words)")
            part_start = split_point + 1
    
    return split_points

def detect_section_boundaries(pages: List[Dict[str, Any]]) -> List[int]:
    """
    Attempt to detect section or chapter boundaries in the PDF.
    
    Args:
        pages: List of page dictionaries with text and word count
        
    Returns:
        List of page indices that likely contain section boundaries
    """
    boundaries = []
    
    # Common chapter/section heading patterns
    chapter_patterns = [
        r'^\s*chapter\s+\d+', 
        r'^\s*\d+\.\s+',  # Numbered sections like "1. Introduction"
        r'^\s*section\s+\d+',
        r'^\s*part\s+\d+',
    ]
    
    for i, page in enumerate(pages):
        text = page['text']
        
        # Check first few lines of the page
        lines = text.split('\n')[:5]
        for line in lines:
            line = line.strip().lower()
            
            # Check for common chapter/section patterns
            for pattern in chapter_patterns:
                if re.match(pattern, line):
                    boundaries.append(i)
                    break
            
            # Check for short headings (likely titles) followed by empty line
            if len(lines) > 1 and len(line) < 50 and len(line) > 3 and lines[1].strip() == '':
                boundaries.append(i)
                break
    
    return boundaries

def create_markdown_files(pages: List[Dict[str, Any]], 
                         split_points: List[int], 
                         output_dir: str, 
                         input_file: str,
                         title: str = None,
                         verbose: bool = False) -> List[str]:
    """
    Create markdown files based on split points.
    
    Args:
        pages: List of page dictionaries with text and word count
        split_points: List of indices of the last page in each part
        output_dir: Directory for output files
        input_file: Path to the input PDF file
        title: Title of the document
        verbose: Whether to print verbose output
        
    Returns:
        List of paths to the created markdown files
    """
    if verbose:
        print("Creating output markdown files...")
    
    # Extract base name without extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Use file name as title if no title is provided
    if not title:
        title = base_name
    
    output_files = []
    part_start = 0
    
    for i, split_point in enumerate(split_points):
        part_num = i + 1
        output_filename = f"{base_name}_part{part_num}.md"
        output_path = os.path.join(output_dir, output_filename)
        
        if verbose:
            print(f"  Creating {output_filename}...")
        
        # Get pages for this part
        part_pages = pages[part_start:split_point + 1]
        
        # Create markdown content for this part
        markdown_content = f"# {title} - Part {part_num}\n\n"
        markdown_content += f"*Pages: {part_pages[0]['page_num']}-{part_pages[-1]['page_num']}*\n\n"
        markdown_content += f"*Words: {sum(p['word_count'] for p in part_pages)}*\n\n"
        
        # Add page content
        for page in part_pages:
            markdown_content += f"## Page {page['page_num']}\n\n"
            
            # Clean up text
            text = page['text']
            
            # Remove excessive newlines
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            # Fix common OCR issues
            text = re.sub(r'([a-zA-Z])-\n([a-zA-Z])', r'\1\2', text)  # Fix hyphenated words
            
            markdown_content += text + "\n\n---\n\n"
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        output_files.append(output_path)
        part_start = split_point + 1
    
    return output_files

def split_pdf(input_file: str, 
             max_words: int = 80000, 
             output_dir: str = '.', 
             strict_boundaries: bool = False, 
             verbose: bool = False) -> List[str]:
    """
    Split a PDF file into multiple markdown files.
    
    Args:
        input_file: Path to the input PDF file
        max_words: Maximum words per output file
        output_dir: Directory for output files
        strict_boundaries: Whether to split only at detected section boundaries
        verbose: Whether to print verbose output
        
    Returns:
        List of paths to the created markdown files
    """
    try:
        # Extract text from PDF
        pages, title = extract_text_from_pdf(input_file, verbose)
        
        # Determine split points
        split_points = determine_split_points(pages, max_words, strict_boundaries, verbose)
        
        # Create output files
        output_files = create_markdown_files(pages, split_points, output_dir, input_file, title, verbose)
        
        return output_files
        
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        raise Exception(f"Error processing PDF: {str(e)}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Split a PDF file into multiple markdown files')
    
    parser.add_argument('input_file', help='Path to input PDF file')
    parser.add_argument('--max-words', type=int, default=80000,
                        help='Maximum words per output file (default: 80000)')
    parser.add_argument('--output-dir', default='.',
                        help='Directory for output files (default: current directory)')
    parser.add_argument('--strict-boundaries', action='store_true',
                        help='Only split at detected section boundaries when possible')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed processing information')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return 1
    
    if not args.input_file.lower().endswith('.pdf'):
        print(f"Error: Input file '{args.input_file}' is not a PDF file.")
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
    
    try:
        result = split_pdf(
            input_file=args.input_file,
            max_words=args.max_words,
            output_dir=args.output_dir,
            strict_boundaries=args.strict_boundaries,
            verbose=args.verbose
        )
        
        print(f"\nProcessing complete. Created {len(result)} markdown files:")
        for i, output_file in enumerate(result, 1):
            print(f"  {i}. {output_file}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 