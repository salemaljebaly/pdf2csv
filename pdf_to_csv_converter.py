#!/usr/bin/env python3
"""
PDF to CSV Converter
A robust tool for extracting structured data from PDF files and converting to CSV format.
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
    column_names: Optional[List[str]] = None

    def validate(self) -> bool:
        """Basic validation - can be customized"""
        # Basic check: all values should be non-empty
        return all(val and val.strip() for val in self.values)
    
    def to_dict(self) -> dict:
        """Convert to dictionary with column names"""
        if self.column_names:
            return dict(zip(self.column_names, self.values))
        return {f"Column_{i+1}": val for i, val in enumerate(self.values)}


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
                 num_columns: Optional[int] = None):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.method = method
        self.validate = validate
        self.verbose = verbose
        self.interactive = interactive
        self.column_names = column_names or []
        self.num_columns = num_columns
        
        # Setup logging
        self._setup_logging()
        
        # Statistics
        self.total_pages = 0
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
    
    def _setup_logging(self):
        """Configure logging"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
    
    def detect_columns(self, text: str) -> int:
        """Detect number of columns in the data"""
        # Split into lines and tokens
        lines = text.strip().split('\n')
        all_tokens = []
        
        # Collect tokens from first few lines
        for line in lines[:50]:  # Look at first 50 lines
            tokens = line.strip().split()
            if tokens:
                all_tokens.extend(tokens)
        
        if not all_tokens:
            return 3  # Default
        
        # Method 1: Try to find a repeating pattern
        # For data like: ID Gender Age ID Gender Age...
        for num_cols in range(2, 11):
            if len(all_tokens) < num_cols * 3:  # Need at least 3 full records
                continue
                
            # Check if pattern repeats
            pattern_matches = True
            for i in range(num_cols):
                # Check if every num_cols position has similar type
                first_token = all_tokens[i]
                
                # Sample a few positions
                for j in range(1, min(5, len(all_tokens) // num_cols)):
                    idx = i + (j * num_cols)
                    if idx >= len(all_tokens):
                        break
                    
                    # Basic type checking
                    token = all_tokens[idx]
                    if (first_token.isdigit() != token.isdigit() and 
                        first_token.isalpha() != token.isalpha()):
                        pattern_matches = False
                        break
                
                if not pattern_matches:
                    break
            
            if pattern_matches:
                self.logger.info(f"Detected {num_cols} columns based on pattern analysis")
                return num_cols
        
        # Method 2: Look for newline patterns (original format)
        # Count unique line lengths
        line_lengths = {}
        for line in lines[:100]:
            tokens = line.strip().split()
            if tokens:
                length = len(tokens)
                line_lengths[length] = line_lengths.get(length, 0) + 1
        
        # Most common line length might indicate columns per line
        if line_lengths:
            most_common_length = max(line_lengths, key=line_lengths.get)
            if most_common_length in range(2, 11):
                self.logger.info(f"Detected {most_common_length} columns based on line analysis")
                return most_common_length
        
        # Method 3: Ask user if detection fails
        self.logger.warning("Column detection uncertain, defaulting to 3")
        return 3
    
    def get_column_names_interactive(self, num_columns: int) -> List[str]:
        """Interactively get column names from user"""
        print(f"\nDetected {num_columns} columns in your data.")
        print("Please provide names for each column:")
        
        column_names = []
        for i in range(num_columns):
            name = input(f"  Column {i+1} name: ").strip()
            if not name:
                name = f"Column_{i+1}"
            column_names.append(name)
        
        print("\nColumn names set to:", ", ".join(column_names))
        confirm = input("Confirm? (y/n): ").lower()
        
        if confirm != 'y':
            return self.get_column_names_interactive(num_columns)
        
        return column_names
    
    def extract_structured_data(self, text: str) -> List[DataRecord]:
        """Extract data assuming structured format"""
        records = []
        tokens = text.split()
        
        if not self.num_columns:
            return records
        
        i = 0
        while i + self.num_columns <= len(tokens):
            # Extract values for one record
            values = tokens[i:i + self.num_columns]
            
            record = DataRecord(
                values=values,
                column_names=self.column_names
            )
            
            if not self.validate or record.validate():
                records.append(record)
                self.valid_records += 1
            else:
                self.invalid_records += 1
                if self.verbose:
                    self.logger.warning(f"Invalid record: {values}")
            
            i += self.num_columns
        
        return records
    
    def extract_regex_data(self, text: str) -> List[DataRecord]:
        """Extract data using regex patterns - general approach"""
        records = []
        
        if not self.num_columns:
            return records
        
        # Build a general pattern based on number of columns
        # This pattern looks for groups of non-whitespace tokens
        pattern_parts = [r'(\S+)' for _ in range(self.num_columns)]
        pattern = re.compile(r'\s*'.join(pattern_parts))
        
        matches = pattern.findall(text)
        
        for match in matches:
            values = list(match)
            
            record = DataRecord(
                values=values,
                column_names=self.column_names
            )
            
            if not self.validate or record.validate():
                records.append(record)
                self.valid_records += 1
            else:
                self.invalid_records += 1
                if self.verbose:
                    self.logger.warning(f"Invalid record: {values}")
        
        return records
    
    def extract_table_data(self, page) -> List[DataRecord]:
        """Extract data from tables in the page"""
        records = []
        tables = page.extract_tables()
        
        for table in tables:
            for row in table:
                if len(row) >= self.num_columns:
                    # Extract values based on number of columns
                    values = [str(row[i]).strip() for i in range(self.num_columns)]
                    
                    record = DataRecord(
                        values=values,
                        column_names=self.column_names
                    )
                    
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
            records = self.extract_table_data(page)
        else:
            text = page.extract_text()
            if not text:
                self.logger.warning(f"No text found on page {page.page_number}")
                return records
            
            if self.method == ExtractionMethod.STRUCTURED:
                records = self.extract_structured_data(text)
            elif self.method == ExtractionMethod.REGEX:
                records = self.extract_regex_data(text)
            else:  # AUTO mode
                # Try regex first for space-separated data
                records = self.extract_regex_data(text)
                if len(records) == 0:  # If no results, try structured
                    self.logger.info("No records found with regex, trying structured extraction")
                    records = self.extract_structured_data(text)
        
        return records
    
    def convert(self) -> Tuple[int, int]:
        """Main conversion method"""
        self.logger.info(f"Starting conversion: {self.input_path} -> {self.output_path}")
        
        try:
            with pdfplumber.open(self.input_path) as pdf:
                self.total_pages = len(pdf.pages)
                self.logger.info(f"Processing {self.total_pages} pages")
                
                # If interactive mode, detect columns and get names
                if self.interactive and not self.column_names:
                    # Sample first page to detect structure
                    if pdf.pages:
                        sample_text = pdf.pages[0].extract_text()
                        if sample_text:
                            print("\nAnalyzing PDF structure...")
                            detected_cols = self.detect_columns(sample_text)
                            
                            # Allow user to override detection
                            print(f"\nDetected {detected_cols} columns in your data.")
                            user_input = input(f"Press Enter to accept, or type the correct number of columns: ").strip()
                            
                            if user_input.isdigit():
                                self.num_columns = int(user_input)
                            else:
                                self.num_columns = detected_cols
                            
                            self.column_names = self.get_column_names_interactive(self.num_columns)
                
                # Set default column names if not provided
                if not self.column_names and self.num_columns:
                    self.column_names = [f"Column_{i+1}" for i in range(self.num_columns)]
                elif not self.num_columns:
                    self.num_columns = 3  # Default
                    self.column_names = ["Column_1", "Column_2", "Column_3"]
                
                with open(self.output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.column_names)
                    
                    # Process pages with progress bar if available
                    pages = pdf.pages
                    if tqdm:
                        pages = tqdm(pages, desc="Processing pages", unit="page")
                    
                    for page in pages:
                        records = self.process_page(page)
                        for record in records:
                            writer.writerow(record.values)
                            self.total_records += 1
                
                self.logger.info(f"Conversion complete!")
                self.logger.info(f"Total records: {self.total_records}")
                self.logger.info(f"Valid records: {self.valid_records}")
                self.logger.info(f"Invalid records: {self.invalid_records}")
                
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
  %(prog)s -c 4 --columns "ID,Name,Age,City" input.pdf output.csv
  %(prog)s -m regex -v large_file.pdf data.csv
        """
    )
    
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('output', help='Output CSV file path')
    
    parser.add_argument('-m', '--method', 
                        type=str,
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
                        help='Comma-separated column names (e.g., "ID,Name,Age")')
    
    parser.add_argument('--no-validate', 
                        action='store_true',
                        help='Disable data validation')
    
    parser.add_argument('-v', '--verbose', 
                        action='store_true',
                        help='Enable verbose output')
    
    parser.add_argument('--version', 
                        action='version',
                        version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Parse column names if provided
    column_names = None
    if args.columns:
        column_names = [col.strip() for col in args.columns.split(',')]
        if args.num_columns and len(column_names) != args.num_columns:
            print(f"Error: Number of column names ({len(column_names)}) doesn't match --num-columns ({args.num_columns})")
            sys.exit(1)
    
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
            num_columns=args.num_columns
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