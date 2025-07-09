#!/usr/bin/env python3
"""
PDF to CSV Converter - Optimized version with header skipping
"""

import argparse
import csv
import logging
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Iterator
import re
from dataclasses import dataclass
from enum import Enum

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is required. Install with: pip install pdfplumber")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


class ExtractionMethod(Enum):
    """Supported extraction methods"""
    AUTO = "auto"
    STRUCTURED = "structured"
    REGEX = "regex"
    TABLE = "table"


@dataclass
class DataRecord:
    """Data structure for extracted records"""
    values: List[str]
    
    def validate(self) -> bool:
        """Basic validation - all values should be non-empty"""
        return all(val and val.strip() for val in self.values)


class PDFToCSVConverter:
    """Main converter class for PDF to CSV extraction"""
    
    def __init__(self, 
                 input_path: str, 
                 output_path: str,
                 method: ExtractionMethod = ExtractionMethod.AUTO,
                 validate: bool = True,
                 verbose: bool = False,
                 interactive: bool = False,
                 column_names: Optional[List[str]] = None,
                 num_columns: Optional[int] = None,
                 skip_rows: int = 0):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.method = method
        self.validate = validate
        self.verbose = verbose
        self.interactive = interactive
        self.column_names = column_names or []
        self.num_columns = num_columns or 3
        self.skip_rows = skip_rows
        
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
        self.rows_skipped = 0
    
    def detect_columns(self, text: str) -> int:
        """Detect number of columns in the data"""
        lines = text.strip().split('\n')
        
        # Skip header lines if they contain Arabic or non-data patterns
        data_lines = []
        for line in lines:
            # Skip lines that appear to be headers (contain Arabic, stars, etc.)
            if not any(ord(c) > 1536 for c in line) and not line.startswith('*'):
                tokens = line.strip().split()
                if tokens:
                    data_lines.append(tokens)
        
        if not data_lines:
            return 3
        
        # Count most common number of tokens per line
        token_counts = {}
        for tokens in data_lines[:20]:  # Sample first 20 data lines
            count = len(tokens)
            if 2 <= count <= 10:  # Reasonable column range
                token_counts[count] = token_counts.get(count, 0) + 1
        
        if token_counts:
            # Return most common count
            return max(token_counts, key=token_counts.get)
        
        return 3  # Default
    
    def get_column_names_interactive(self, num_columns: int) -> List[str]:
        """Interactively get column names from user"""
        print(f"\nDetected {num_columns} columns in your data.")
        print("Please provide names for each column:")
        
        column_names = []
        for i in range(num_columns):
            name = input(f"  Column {i+1} name: ").strip()
            column_names.append(name or f"Column_{i+1}")
        
        print("\nColumn names set to:", ", ".join(column_names))
        if input("Confirm? (y/n): ").lower() != 'y':
            return self.get_column_names_interactive(num_columns)
        
        return column_names
    
    def extract_data(self, text: str) -> List[DataRecord]:
        """Extract data from text - unified method"""
        records = []
        
        if self.method == ExtractionMethod.REGEX:
            # Regex pattern for space-separated values
            pattern = re.compile(r'\s*'.join([r'(\S+)' for _ in range(self.num_columns)]))
            matches = pattern.findall(text)
            
            for i, match in enumerate(matches):
                # Skip first N matches if skip_rows is set
                if i < self.skip_rows:
                    self.rows_skipped += 1
                    continue
                    
                record = DataRecord(values=list(match))
                if not self.validate or record.validate():
                    records.append(record)
                    self.valid_records += 1
                else:
                    self.invalid_records += 1
        else:
            # Token-based extraction
            tokens = text.split()
            
            # Skip tokens that are likely headers (Arabic text)
            start_idx = 0
            if self.skip_rows > 0:
                # Skip first N records worth of tokens
                skip_tokens = self.skip_rows * self.num_columns
                while start_idx < len(tokens) and skip_tokens > 0:
                    # Skip Arabic tokens
                    if any(ord(c) > 1536 for c in tokens[start_idx]):
                        start_idx += 1
                    else:
                        start_idx += 1
                        skip_tokens -= 1
                self.rows_skipped = self.skip_rows
            
            # Extract records
            for i in range(start_idx, len(tokens) - self.num_columns + 1, self.num_columns):
                values = tokens[i:i + self.num_columns]
                
                # Skip if values contain Arabic text
                if any(any(ord(c) > 1536 for c in val) for val in values):
                    continue
                
                record = DataRecord(values=values)
                if not self.validate or record.validate():
                    records.append(record)
                    self.valid_records += 1
                else:
                    self.invalid_records += 1
        
        return records
    
    def process_page(self, page) -> List[DataRecord]:
        """Process a single PDF page"""
        records = []
        
        if self.method == ExtractionMethod.TABLE:
            tables = page.extract_tables()
            for table in tables:
                for i, row in enumerate(table):
                    if i < self.skip_rows:
                        self.rows_skipped += 1
                        continue
                        
                    if len(row) >= self.num_columns:
                        values = [str(row[j]).strip() for j in range(self.num_columns)]
                        
                        # Skip if contains Arabic
                        if any(any(ord(c) > 1536 for c in val) for val in values):
                            continue
                            
                        record = DataRecord(values=values)
                        if not self.validate or record.validate():
                            records.append(record)
                            self.valid_records += 1
                        else:
                            self.invalid_records += 1
        else:
            text = page.extract_text()
            if text:
                records = self.extract_data(text)
        
        return records
    
    def convert(self) -> Tuple[int, int]:
        """Main conversion method"""
        self.logger.info(f"Starting conversion: {self.input_path} -> {self.output_path}")
        
        try:
            with pdfplumber.open(self.input_path) as pdf:
                self.total_pages = len(pdf.pages)
                self.logger.info(f"Processing {self.total_pages} pages")
                
                # Interactive mode for column detection
                if self.interactive and not self.column_names:
                    if pdf.pages:
                        sample_text = pdf.pages[0].extract_text()
                        if sample_text:
                            print("\nAnalyzing PDF structure...")
                            detected_cols = self.detect_columns(sample_text)
                            
                            print(f"\nDetected {detected_cols} columns in your data.")
                            user_input = input("Press Enter to accept, or type the correct number: ").strip()
                            
                            self.num_columns = int(user_input) if user_input.isdigit() else detected_cols
                            self.column_names = self.get_column_names_interactive(self.num_columns)
                
                # Set default column names if not provided
                if not self.column_names:
                    self.column_names = [f"Column_{i+1}" for i in range(self.num_columns)]
                
                # Process PDF
                with open(self.output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.column_names)
                    
                    pages = tqdm(pdf.pages, desc="Processing pages", unit="page") if tqdm else pdf.pages
                    
                    for page_num, page in enumerate(pages):
                        # Only skip rows on first page
                        if page_num > 0:
                            self.skip_rows = 0
                            
                        records = self.process_page(page)
                        for record in records:
                            writer.writerow(record.values)
                            self.total_records += 1
                
                self.logger.info(f"Conversion complete!")
                self.logger.info(f"Total records: {self.total_records}")
                self.logger.info(f"Valid records: {self.valid_records}")
                self.logger.info(f"Invalid records: {self.invalid_records}")
                if self.rows_skipped > 0:
                    self.logger.info(f"Rows skipped: {self.rows_skipped}")
                
                return self.total_records, self.valid_records
                
        except Exception as e:
            self.logger.error(f"Error during conversion: {e}")
            raise


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Convert PDF files with structured data to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.pdf output.csv
  %(prog)s -i input.pdf output.csv  # Interactive mode
  %(prog)s -c 3 --skip 1 input.pdf output.csv  # Skip first row
  %(prog)s -c 4 --columns "ID,Name,Age,City" input.pdf output.csv
        """
    )
    
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('output', help='Output CSV file path')
    
    parser.add_argument('-m', '--method', 
                        choices=['auto', 'structured', 'regex', 'table'],
                        default='auto',
                        help='Extraction method (default: auto)')
    
    parser.add_argument('-i', '--interactive',
                        action='store_true',
                        help='Interactive mode - prompts for column names')
    
    parser.add_argument('-c', '--num-columns',
                        type=int,
                        help='Number of columns in the data')
    
    parser.add_argument('--columns',
                        type=str,
                        help='Comma-separated column names')
    
    parser.add_argument('--skip',
                        type=int,
                        default=0,
                        help='Number of rows to skip at start (default: 0)')
    
    parser.add_argument('--no-validate', 
                        action='store_true',
                        help='Disable data validation')
    
    parser.add_argument('-v', '--verbose', 
                        action='store_true',
                        help='Enable verbose output')
    
    parser.add_argument('--version', 
                        action='version',
                        version='%(prog)s 1.1.0')
    
    args = parser.parse_args()
    
    # Validate input
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    # Parse column names
    column_names = None
    if args.columns:
        column_names = [col.strip() for col in args.columns.split(',')]
    
    # Run conversion
    try:
        converter = PDFToCSVConverter(
            input_path=args.input,
            output_path=args.output,
            method=ExtractionMethod(args.method),
            validate=not args.no_validate,
            verbose=args.verbose,
            interactive=args.interactive,
            column_names=column_names,
            num_columns=args.num_columns,
            skip_rows=args.skip
        )
        
        total, valid = converter.convert()
        
        if total == 0:
            print("Warning: No records were extracted")
            sys.exit(1)
        
        print(f"Success! Extracted {valid} records to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()