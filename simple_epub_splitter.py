#!/usr/bin/env python3
"""
Simple EPUB Splitter - A tool to split large EPUB books into smaller parts.
"""

import os
import sys
import re
import argparse
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

def log(message, verbose=False):
    """Print a message if verbose mode is enabled."""
    if verbose:
        print(message)

def count_words(text):
    """Count words in a text string using a simple regex approach."""
    # Remove HTML tags if any remain
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Count words (sequences of alphanumeric characters)
    words = re.findall(r'\w+', text)
    return len(words)

def split_epub(input_file, max_words=80000, output_dir='.', strict_chapters=False, verbose=False):
    """Split an EPUB file into multiple smaller files."""
    log(f"Processing '{input_file}'...", verbose)
    
    # Extract book name from input file path
    book_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Load the book
    book = epub.read_epub(input_file)
    
    # Extract chapters
    log("Extracting chapters...", verbose)
    chapters = []
    
    # Get spine items (ordered document items)
    spine_items = []
    for itemref in book.spine:
        item_id = itemref[0]
        item = book.get_item_with_id(item_id)
        if item is not None and item.get_type() == ebooklib.ITEM_DOCUMENT:
            spine_items.append(item)
    
    # Process each spine item as a chapter
    for i, item in enumerate(spine_items):
        # Get content
        content = item.get_content().decode('utf-8')
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Try to extract title
        title = None
        title_elem = soup.find(['h1', 'h2', 'h3', 'title'])
        if title_elem:
            title = title_elem.get_text().strip()
        
        # If no title found, use generic name
        if not title:
            title = f"Chapter {i+1}"
        
        # Count words
        text = soup.get_text()
        word_count = count_words(text)
        
        # Create chapter info
        chapter = {
            'id': item.get_id(),
            'title': title,
            'content': content,
            'file_name': item.file_name,
            'word_count': word_count,
            'item': item
        }
        
        chapters.append(chapter)
        log(f"  - {title} ({word_count} words)", verbose)
    
    total_words = sum(chapter['word_count'] for chapter in chapters)
    log(f"Found {len(chapters)} chapters with a total of {total_words} words.", verbose)
    
    # Determine split points
    log("Determining split points...", verbose)
    split_points = []
    current_word_count = 0
    current_chapters = []
    
    for i, chapter in enumerate(chapters):
        # If adding this chapter would exceed the word limit
        if current_word_count + chapter['word_count'] > max_words and current_chapters:
            # If strict chapter mode is enabled or current word count is at least 40% of max
            if strict_chapters or current_word_count >= 0.4 * max_words:
                split_points.append(i - 1)  # Split before current chapter
                current_word_count = chapter['word_count']
                current_chapters = [chapter]
            else:
                # Add chapter anyway and split after it
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
    
    # Log split points
    part_start = 0
    for i, split_point in enumerate(split_points):
        part_chapters = chapters[part_start:split_point + 1]
        part_words = sum(c['word_count'] for c in part_chapters)
        log(f"  Part {i+1}: Chapters {part_start+1}-{split_point+1} ({part_words} words)", verbose)
        part_start = split_point + 1
    
    # Create output EPUBs
    log("Creating output EPUB files...", verbose)
    output_files = []
    
    part_start = 0
    for i, split_point in enumerate(split_points):
        part_num = i + 1
        output_filename = f"{book_name}_part{part_num}.epub"
        output_path = os.path.join(output_dir, output_filename)
        
        log(f"  Creating {output_filename}...", verbose)
        
        # Create a new EPUB book
        new_book = epub.EpubBook()
        
        # Set basic metadata
        book_title = book.title or f"{book_name}"
        new_book.set_title(f"{book_title} - Part {part_num}")
        
        if book.language:
            new_book.set_language(book.language)
        
        # Set a simple identifier
        new_book.set_identifier(f"{book_name}_part{part_num}")
        
        # Add author if available
        author = None
        if hasattr(book, 'get_metadata'):
            creators = book.get_metadata('DC', 'creator')
            if creators:
                author = creators[0][0]
        
        if author:
            new_book.add_author(author)
        
        # Get chapters for this part
        part_chapters = chapters[part_start:split_point + 1]
        
        # Add chapters to the book
        epub_chapters = []
        for chapter in part_chapters:
            # Create EpubHtml item
            epub_chapter = epub.EpubHtml(
                title=chapter['title'],
                file_name=chapter['file_name'],
                content=chapter['content']
            )
            epub_chapter.id = chapter['id']
            new_book.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)
        
        # Add CSS, images, and other assets from original book
        for item in book.get_items():
            if item.get_type() != ebooklib.ITEM_DOCUMENT and item.get_type() != ebooklib.ITEM_NAVIGATION:
                # Check if this is a referenced asset in our chapters
                for chapter in part_chapters:
                    if item.file_name in chapter['content']:
                        new_book.add_item(item)
                        break
        
        # Add chapters to spine
        for chapter in epub_chapters:
            new_book.spine.append(chapter)
        
        # Create table of contents
        new_book.toc = [(epub.Section(chapter.title), [chapter]) for chapter in epub_chapters]
        
        # Add default NCX and Nav files
        new_book.add_item(epub.EpubNcx())
        new_book.add_item(epub.EpubNav())
        
        # Save the EPUB file
        epub.write_epub(output_path, new_book, {})
        
        output_files.append(output_path)
        part_start = split_point + 1
    
    return output_files

def main():
    """Main entry point for the EPUB splitter tool."""
    parser = argparse.ArgumentParser(description='Split a large EPUB file into smaller parts')
    
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
    
    # Check if input file exists
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return 1
    
    # Check if input file is an EPUB
    if not args.input_file.lower().endswith('.epub'):
        print(f"Error: Input file '{args.input_file}' is not an EPUB file.")
        return 1
    
    # Check if output directory exists or can be created
    if not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except OSError as e:
            print(f"Error: Cannot create output directory '{args.output_dir}': {e}")
            return 1
    
    # Check if max words is positive
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
        
        if args.verbose:
            print(f"\nProcessing complete. Created {len(result)} output files:")
            for i, output_file in enumerate(result, 1):
                print(f"  {i}. {output_file}")
        else:
            print(f"\nProcessing complete. Created {len(result)} output files.")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 