#!/usr/bin/env python3
"""
Minimal EPUB Splitter - Splits an EPUB book into smaller parts based on word count.
"""

import os
import sys
import re
import argparse
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub


def count_words(text):
    """Count words in text using a simple regex approach."""
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Count words (sequences of alphanumeric characters)
    words = re.findall(r'\w+', text)
    return len(words)


def split_epub(input_file, max_words=80000, output_dir='.', strict_chapters=False, verbose=False):
    """Split an EPUB file into multiple smaller files."""
    def log(message):
        if verbose:
            print(message)
    
    log(f"Processing '{input_file}'...")
    
    # Extract book name from input file path
    book_name = os.path.splitext(os.path.basename(input_file))[0]
    
    try:
        # Load the book
        book = epub.read_epub(input_file)
        
        # Get spine items (ordered document items)
        log("Extracting chapters...")
        chapters = []
        total_word_count = 0
        
        # Collect all document items from the spine
        for itemref in book.spine:
            item_id = itemref[0]
            item = book.get_item_with_id(item_id)
            if item is not None and item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Get content and count words
                content = item.get_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                
                # Try to extract title
                title_elem = soup.find(['h1', 'h2', 'h3', 'title'])
                title = title_elem.get_text().strip() if title_elem else f"Chapter {len(chapters) + 1}"
                
                # Count words
                text = soup.get_text()
                word_count = count_words(text)
                total_word_count += word_count
                
                # Add chapter to list
                chapters.append({
                    'item': item,
                    'title': title,
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
        log("Creating output EPUB files...")
        output_files = []
        
        part_start = 0
        for i, split_point in enumerate(split_points):
            part_num = i + 1
            output_filename = f"{book_name}_part{part_num}.epub"
            output_path = os.path.join(output_dir, output_filename)
            
            log(f"  Creating {output_filename}...")
            
            # Create a new EPUB book
            new_book = epub.EpubBook()
            
            # Set basic metadata
            title = getattr(book, 'title', book_name) or book_name
            new_book.set_title(f"{title} - Part {part_num}")
            if hasattr(book, 'language') and book.language:
                new_book.set_language(book.language)
            new_book.set_identifier(f"{book_name}_part{part_num}")
            
            # Add chapters for this part
            part_chapters = chapters[part_start:split_point + 1]
            
            # A list to keep track of what we've added
            added_items = set()
            
            # Add chapters to the book
            for chapter in part_chapters:
                item = chapter['item']
                new_book.add_item(item)
                new_book.spine.append(item)
                added_items.add(item.get_id())
            
            # Add CSS, images, and other assets
            for item in book.get_items():
                if item.get_id() not in added_items and item.get_type() not in (ebooklib.ITEM_DOCUMENT, ebooklib.ITEM_NAVIGATION):
                    new_book.add_item(item)
            
            # Add NCX/Nav if needed
            if not any(item.get_type() == ebooklib.ITEM_NAVIGATION for item in new_book.get_items()):
                new_book.add_item(epub.EpubNcx())
                nav = epub.EpubNav()
                new_book.add_item(nav)
            
            # Write the EPUB file
            epub.write_epub(output_path, new_book, {})
            output_files.append(output_path)
            
            part_start = split_point + 1
        
        return output_files
        
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        raise Exception(f"Error processing EPUB: {str(e)}")


def main():
    """Main entry point for the script."""
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
        
        print(f"\nProcessing complete. Created {len(result)} output files:")
        for i, output_file in enumerate(result, 1):
            print(f"  {i}. {output_file}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 