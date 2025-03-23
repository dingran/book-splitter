#!/usr/bin/env python3
"""
EPUB to Markdown Splitter - Splits an EPUB book into multiple markdown files based on word count.
"""

import os
import sys
import re
import argparse
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
import html2text

def count_words(text):
    """Count words in text using a simple regex approach."""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Count words (sequences of alphanumeric characters)
    words = re.findall(r'\w+', text)
    return len(words)

def extract_markdown_from_html(html_content):
    """Convert HTML content to markdown."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_tables = False
    h.ignore_emphasis = False
    return h.handle(html_content)

def split_epub(input_file, max_words=80000, output_dir='.', strict_chapters=False, verbose=False):
    """Split an EPUB file into multiple markdown files."""
    def log(message):
        if verbose:
            print(message)
    
    log(f"Processing '{input_file}'...")
    
    # Extract book name from input file path
    book_name = os.path.splitext(os.path.basename(input_file))[0]
    
    try:
        # Load the book
        book = epub.read_epub(input_file)
        
        # Get book title
        book_title = getattr(book, 'title', book_name) or book_name
        
        # Get spine items (ordered document items)
        log("Extracting chapters...")
        chapters = []
        total_word_count = 0
        
        # Collect all document items from the spine
        for itemref in book.spine:
            item_id = itemref[0]
            item = book.get_item_with_id(item_id)
            if item is not None and item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Get content and convert to markdown
                content = item.get_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                
                # Try to extract title
                title_elem = soup.find(['h1', 'h2', 'h3', 'title'])
                title = title_elem.get_text().strip() if title_elem else f"Chapter {len(chapters) + 1}"
                
                # Convert to markdown
                markdown_content = extract_markdown_from_html(content)
                
                # Count words
                word_count = count_words(markdown_content)
                total_word_count += word_count
                
                # Add chapter to list
                chapters.append({
                    'title': title,
                    'markdown': markdown_content,
                    'word_count': word_count
                })
                
                log(f"  - {title} ({word_count} words)")
        
        log(f"Found {len(chapters)} chapters with a total of {total_word_count} words.")
        
        # Determine split points
        log("Determining split points...")
        split_points = []
        current_word_count = 0
        current_chapters = []
        
        for i, chapter in enumerate(chapters):
            # Check if adding this chapter would exceed the word limit
            if current_word_count + chapter['word_count'] > max_words and current_chapters:
                if strict_chapters or current_word_count >= 0.4 * max_words:
                    # Split before current chapter
                    split_points.append(i - 1)
                    current_word_count = chapter['word_count']
                    current_chapters = [chapter]
                else:
                    # Add chapter and split after it
                    current_chapters.append(chapter)
                    current_word_count += chapter['word_count']
                    split_points.append(i)
                    current_word_count = 0
                    current_chapters = []
            else:
                # Add chapter to current part
                current_chapters.append(chapter)
                current_word_count += chapter['word_count']
        
        # Add the last part if there are remaining chapters
        if current_chapters:
            split_points.append(len(chapters) - 1)
        
        # Log split information
        part_start = 0
        for i, split_point in enumerate(split_points):
            part_chapters = chapters[part_start:split_point + 1]
            part_words = sum(c['word_count'] for c in part_chapters)
            log(f"  Part {i+1}: Chapters {part_start+1}-{split_point+1} ({part_words} words)")
            part_start = split_point + 1
        
        # Create output files
        log("Creating output markdown files...")
        output_files = []
        
        part_start = 0
        for i, split_point in enumerate(split_points):
            part_num = i + 1
            output_filename = f"{book_name}_part{part_num}.md"
            output_path = os.path.join(output_dir, output_filename)
            
            log(f"  Creating {output_filename}...")
            
            # Get chapters for this part
            part_chapters = chapters[part_start:split_point + 1]
            
            # Create markdown content for this part
            markdown_content = f"# {book_title} - Part {part_num}\n\n"
            markdown_content += f"*Words: {sum(c['word_count'] for c in part_chapters)}*\n\n"
            
            # Add table of contents
            markdown_content += "## Table of Contents\n\n"
            for j, chapter in enumerate(part_chapters):
                markdown_content += f"{j+1}. [{chapter['title']}](#{sanitize_for_anchor(chapter['title'])})\n"
            markdown_content += "\n---\n\n"
            
            # Add chapter content
            for chapter in part_chapters:
                markdown_content += f"## {chapter['title']}\n\n"
                markdown_content += chapter['markdown']
                markdown_content += "\n\n---\n\n"
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            output_files.append(output_path)
            part_start = split_point + 1
        
        return output_files
        
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        raise Exception(f"Error processing EPUB: {str(e)}")

def sanitize_for_anchor(text):
    """Sanitize text for use as an anchor in markdown."""
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s-]+', '-', text)
    return text

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Split an EPUB file into multiple markdown files')
    
    parser.add_argument('input_file', help='Path to input EPUB file')
    parser.add_argument('--max-words', type=int, default=80000,
                        help='Maximum words per output file (default: 80000)')
    parser.add_argument('--output-dir', default='.',
                        help='Directory for output files (default: current directory)')
    parser.add_argument('--strict-chapters', action='store_true',
                        help='Only split at chapter boundaries, even if exceeding word limit')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed processing information')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return 1
    
    if not args.input_file.lower().endswith('.epub'):
        print(f"Error: Input file '{args.input_file}' is not an EPUB file.")
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
        result = split_epub(
            input_file=args.input_file,
            max_words=args.max_words,
            output_dir=args.output_dir,
            strict_chapters=args.strict_chapters,
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