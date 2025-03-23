#!/usr/bin/env python3
"""
EPUB Splitter - A tool to split large EPUB books into smaller parts.
"""

import argparse
import os
import sys
from epub_processor import EPUBProcessor

def parse_arguments():
    """Parse command line arguments."""
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
    
    return parser.parse_args()

def validate_arguments(args):
    """Validate the provided arguments."""
    # Check if input file exists
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return False
    
    # Check if input file is an EPUB
    if not args.input_file.lower().endswith('.epub'):
        print(f"Error: Input file '{args.input_file}' is not an EPUB file.")
        return False
    
    # Check if output directory exists or can be created
    if not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except OSError as e:
            print(f"Error: Cannot create output directory '{args.output_dir}': {e}")
            return False
    
    # Check if max words is positive
    if args.max_words <= 0:
        print("Error: Maximum words must be a positive number.")
        return False
    
    return True

def main():
    """Main entry point for the EPUB splitter tool."""
    args = parse_arguments()
    
    if not validate_arguments(args):
        sys.exit(1)
    
    try:
        processor = EPUBProcessor(
            input_file=args.input_file,
            max_words=args.max_words,
            output_dir=args.output_dir,
            strict_chapters=args.strict_chapters,
            verbose=args.verbose
        )
        
        result = processor.process()
        
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
        sys.exit(1)

if __name__ == "__main__":
    main() 