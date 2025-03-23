"""
EPUB Processor module for handling EPUB files.
"""

import os
import re
from collections import namedtuple
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
import nltk
from copy import deepcopy
import re

# A simple structure to hold chapter info
Chapter = namedtuple('Chapter', ['id', 'title', 'content', 'file_name', 'word_count'])

class EPUBProcessor:
    """Handles the processing of EPUB files, including splitting into smaller parts."""
    
    def __init__(self, input_file, max_words=80000, output_dir='.', strict_chapters=False, verbose=False):
        """Initialize the EPUB processor.
        
        Args:
            input_file (str): Path to the input EPUB file.
            max_words (int): Maximum number of words per output file.
            output_dir (str): Directory for output files.
            strict_chapters (bool): Only split at chapter boundaries.
            verbose (bool): Print detailed processing information.
        """
        self.input_file = input_file
        self.max_words = max_words
        self.output_dir = output_dir
        self.strict_chapters = strict_chapters
        self.verbose = verbose
        self.book = None
        self.chapters = []
        self.output_files = []
        
        # Extract book name from input file path
        self.book_name = os.path.splitext(os.path.basename(input_file))[0]
    
    def log(self, message):
        """Print a message if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def process(self):
        """Process the EPUB file and split it into smaller parts.
        
        Returns:
            list: Paths to the generated output files.
        """
        self.log(f"Processing '{self.input_file}'...")
        
        # Load the book
        self.book = epub.read_epub(self.input_file)
        
        # Extract chapters
        self.extract_chapters()
        
        # Determine split points
        split_points = self.determine_split_points()
        
        # Create output EPUBs
        self.create_output_epubs(split_points)
        
        return self.output_files
    
    def count_words(self, text):
        """Count words in a text string using a simple regex approach instead of NLTK tokenizer.
        
        Args:
            text (str): Text to count words in.
            
        Returns:
            int: Number of words in the text.
        """
        # Remove HTML tags if any remain
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Count words (sequences of alphanumeric characters)
        words = re.findall(r'\w+', text)
        return len(words)
    
    def extract_chapters(self):
        """Extract chapters from the EPUB book."""
        self.log("Extracting chapters...")
        
        # Get spine items (ordered document items)
        spine_items = []
        for itemref in self.book.spine:
            item_id = itemref[0]
            item = self.book.get_item_with_id(item_id)
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
            
            # Count words using our simple word counter instead of NLTK
            text = soup.get_text()
            word_count = self.count_words(text)
            
            # Create chapter object
            chapter = Chapter(
                id=item.get_id(),
                title=title,
                content=content,
                file_name=item.file_name,
                word_count=word_count
            )
            
            self.chapters.append(chapter)
            
            self.log(f"  - {title} ({word_count} words)")
        
        self.log(f"Found {len(self.chapters)} chapters with a total of {sum(c.word_count for c in self.chapters)} words.")
    
    def determine_split_points(self):
        """Determine where to split the book.
        
        Returns:
            list: Indices of the last chapter in each part.
        """
        self.log("Determining split points...")
        
        split_points = []
        current_word_count = 0
        current_chapters = []
        
        for i, chapter in enumerate(self.chapters):
            # If adding this chapter would exceed the word limit
            if current_word_count + chapter.word_count > self.max_words and current_chapters:
                # If strict chapter mode is enabled or current word count is at least 40% of max
                # (avoiding creating very small parts)
                if self.strict_chapters or current_word_count >= 0.4 * self.max_words:
                    split_points.append(i - 1)  # Split before current chapter
                    current_word_count = chapter.word_count
                    current_chapters = [chapter]
                else:
                    # Add chapter anyway and split after it
                    current_chapters.append(chapter)
                    current_word_count += chapter.word_count
                    split_points.append(i)
                    current_word_count = 0
                    current_chapters = []
            else:
                # Add chapter to current part
                current_chapters.append(chapter)
                current_word_count += chapter.word_count
        
        # Add the last part if there are remaining chapters
        if current_chapters:
            split_points.append(len(self.chapters) - 1)
        
        # Log split points
        part_start = 0
        for i, split_point in enumerate(split_points):
            part_chapters = self.chapters[part_start:split_point + 1]
            part_words = sum(c.word_count for c in part_chapters)
            self.log(f"  Part {i+1}: Chapters {part_start+1}-{split_point+1} ({part_words} words)")
            part_start = split_point + 1
        
        return split_points
    
    def create_output_epubs(self, split_points):
        """Create output EPUB files based on split points.
        
        Args:
            split_points (list): Indices of the last chapter in each part.
        """
        self.log("Creating output EPUB files...")
        
        part_start = 0
        for i, split_point in enumerate(split_points):
            part_num = i + 1
            output_filename = f"{self.book_name}_part{part_num}.epub"
            output_path = os.path.join(self.output_dir, output_filename)
            
            self.log(f"  Creating {output_filename}...")
            
            # Create a new EPUB book
            book = epub.EpubBook()
            
            # Copy metadata from original book
            self._copy_metadata(book)
            
            # Update title to indicate it's a part
            book.set_title(f"{book.title} - Part {part_num}")
            
            # Get chapters for this part
            part_chapters = self.chapters[part_start:split_point + 1]
            
            # Add chapters to the book
            epub_chapters = []
            for chapter in part_chapters:
                # Create EpubHtml item
                epub_chapter = epub.EpubHtml(
                    title=chapter.title,
                    file_name=chapter.file_name,
                    content=chapter.content
                )
                epub_chapter.id = chapter.id
                book.add_item(epub_chapter)
                epub_chapters.append(epub_chapter)
            
            # Copy CSS, images, and other assets from original book
            self._copy_assets(book)
            
            # Add chapters to spine
            for chapter in epub_chapters:
                book.spine.append(chapter)
            
            # Create table of contents
            book.toc = [(epub.Section(chapter.title), [chapter]) for chapter in epub_chapters]
            
            # Add default NCX and Nav files
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Save the EPUB file
            epub.write_epub(output_path, book, {})
            
            self.output_files.append(output_path)
            part_start = split_point + 1
    
    def _copy_metadata(self, book):
        """Copy metadata from original book to the new book.
        
        Args:
            book (EpubBook): The target EPUB book.
        """
        # Copy basic metadata
        if self.book.title:
            book.set_title(self.book.title)
        if self.book.language:
            book.set_language(self.book.language)
        
        # Copy identifiers safely
        if 'http://purl.org/dc/elements/1.1/' in self.book.metadata:
            dc_metadata = self.book.metadata['http://purl.org/dc/elements/1.1/']
            
            # Copy identifier
            if 'identifier' in dc_metadata:
                for item in dc_metadata['identifier']:
                    # Handle different formats of metadata
                    if len(item) >= 2:  # At least has id and value
                        item_id = item[0] if len(item) > 0 else 'id'
                        value = item[1] if len(item) > 1 else ''
                        book.add_metadata('DC', 'identifier', value, {'id': item_id})
            
            # Copy creator (author)
            if 'creator' in dc_metadata:
                for item in dc_metadata['creator']:
                    if len(item) >= 2:
                        value = item[1]
                        book.add_author(value)
    
    def _copy_assets(self, book):
        """Copy CSS, images, and other assets from original book to the new book.
        
        Args:
            book (EpubBook): The target EPUB book.
        """
        # Copy items that are not documents
        for item in self.book.get_items():
            if item.get_type() != ebooklib.ITEM_DOCUMENT:
                new_item = deepcopy(item)
                book.add_item(new_item) 