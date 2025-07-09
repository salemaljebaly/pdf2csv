# PDF to CSV Converter

A robust Python tool for extracting structured data from PDF files and converting them to CSV format. Specifically designed for extracting ID numbers, gender, and age data from large PDF documents.

## Features

- 🚀 **High Performance**: Efficiently processes large PDF files with streaming capabilities
- 🎯 **Multiple Extraction Methods**: Auto-detect, structured, regex, or table-based extraction
- ✅ **Data Validation**: Built-in validation for ID format, gender values, and age ranges
- 📊 **Progress Tracking**: Visual progress bar for large file processing
- 🔍 **Detailed Logging**: Comprehensive logging with verbose mode
- 🛡️ **Error Handling**: Robust error handling with detailed error messages
- 💾 **Memory Efficient**: Processes files page by page to minimize memory usage

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Method 1: Quick Installation (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/salemaljebaly/pdf2csv.git
cd pdf-to-csv-converter
```

2. Run the installation script:
```bash
# On Linux/macOS
./install.sh

# On Windows
install.bat
```

### Method 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/salemaljebaly/pdf2csv.git
cd pdf2csv
```

2. Create a virtual environment (recommended):
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Verify installation:
```bash
python pdf_to_csv_converter.py --version
```

### Method 3: System-wide Installation

```bash
# Clone and enter directory
git clone https://github.com/salemaljebaly/pdf2csv.git
cd pdf2csv

# Install package
pip install -e .
```

### Development Installation

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/salemaljebaly/pdf2csv.git
cd pdf2csv

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

## Usage

### Basic Usage

```bash
python pdf_to_csv_converter.py input.pdf output.csv
```

### Interactive Mode (NEW!)

Let the script detect columns and prompt you for names:

```bash
python pdf_to_csv_converter.py -i input.pdf output.csv
```

The script will:
1. Detect the number of columns in your data
2. Prompt you to name each column
3. Extract data using your custom column names

### Command Line Options

```bash
python pdf_to_csv_converter.py [OPTIONS] input.pdf output.csv

Options:
  -m, --method {auto,structured,regex,table}
                        Extraction method (default: auto)
  -i, --interactive     Interactive mode - prompts for column names
  -c, --num-columns N   Specify number of columns (e.g., -c 4)
  --columns "A,B,C"     Specify column names (comma-separated)
  --no-validate         Disable data validation
  -v, --verbose         Enable verbose output
  --version             Show program version
  -h, --help           Show help message
```

### Examples

1. **Interactive mode for custom data:**
   ```bash
   python pdf_to_csv_converter.py -i report.pdf output.csv
   # Script will prompt:
   # Detected 4 columns in your data.
   # Please provide names for each column:
   #   Column 1 name: ProductID
   #   Column 2 name: Name
   #   Column 3 name: Price
   #   Column 4 name: Stock
   ```

2. **Specify columns directly:**
   ```bash
   python pdf_to_csv_converter.py -c 3 --columns "ID,Gender,Age" data.pdf results.csv
   ```

3. **Custom 5-column data:**
   ```bash
   python pdf_to_csv_converter.py -c 5 --columns "ID,FirstName,LastName,Email,Phone" contacts.pdf contacts.csv
   ```

4. **Use regex extraction for complex PDFs:**
   ```bash
   python pdf_to_csv_converter.py -m regex complex_data.pdf output.csv
   ```

5. **Process without validation (faster for trusted data):**
   ```bash
   python pdf_to_csv_converter.py --no-validate large_file.pdf data.csv
   ```

6. **Verbose mode for debugging:**
   ```bash
   python pdf_to_csv_converter.py -v -m structured report.pdf extracted.csv
   ```

## Data Format

The tool can handle various data formats with any number of columns. By default, it expects space or tab-separated values.

### Example: 3-Column Data (ID, Gender, Age)
```
218915949830 F 21
218919256808 M 26
```

### Example: 4-Column Data (Product Info)
```
PRD001 Laptop 999.99 15
PRD002 Mouse 29.99 50
```

### Example: Mixed Format
The tool can handle data whether it's:
- One record per line
- Multiple records per line
- Tab or space separated

## Output Format

The tool generates a CSV file with your custom column names:

### With Interactive Mode:
```csv
ProductID,Name,Price,Stock
PRD001,Laptop,999.99,15
PRD002,Mouse,29.99,50
```

### With Default Names:
```csv
Column_1,Column_2,Column_3
Ali,M,26
```

## Extraction Methods

### Auto (Default)
Automatically detects the best extraction method based on the PDF structure.

### Structured
Assumes data is in a consistent 3-line format. Best for clean, well-formatted PDFs.

### Regex
Uses pattern matching to find valid data. Best for PDFs with mixed content or irregular formatting.

### Table
Extracts data from PDF tables. Best for PDFs with tabular data.

## Performance Tips

1. **For large files (>100MB):**
   - Use `--no-validate` flag if data is trusted
   - Consider splitting the PDF into smaller chunks
   - Ensure sufficient RAM (at least 2x file size)

2. **For better accuracy:**
   - Use `-m structured` for clean PDFs
   - Use `-m regex` for mixed content
   - Enable verbose mode to identify issues

## Troubleshooting

### Common Issues

1. **No data extracted:**
   - Check PDF is text-based (not scanned images)
   - Try different extraction methods
   - Enable verbose mode for debugging

2. **Memory errors:**
   - Process smaller chunks
   - Increase system RAM
   - Use a machine with more resources

3. **Invalid records:**
   - Check data format matches expected pattern
   - Review validation rules
   - Use `--no-validate` to see all extracted data

### For Scanned PDFs

If your PDF contains scanned images, you'll need to use OCR first:

```bash
# Install OCR tools
pip install pytesseract pdf2image

# Pre-process with OCR (separate script needed)
python ocr_preprocessor.py scanned.pdf text.pdf

# Then use the converter
python pdf_to_csv_converter.py text.pdf output.csv
```

## API Usage

You can also use the converter programmatically:

```python
from pdf_to_csv_converter import PDFToCSVConverter, ExtractionMethod

# Basic usage with custom columns
converter = PDFToCSVConverter(
    input_path="data.pdf",
    output_path="output.csv",
    column_names=["ID", "Name", "Age", "City"],
    num_columns=4,
    method=ExtractionMethod.AUTO,
    validate=True,
    verbose=False
)

# Run conversion
total_records, valid_records = converter.convert()
print(f"Extracted {valid_records} valid records out of {total_records} total")

# Interactive mode programmatically
converter = PDFToCSVConverter(
    input_path="data.pdf",
    output_path="output.csv",
    interactive=True  # Will prompt for column names
)
converter.convert()
```

### Custom Validation

You can extend the DataRecord class for custom validation:

```python
from pdf_to_csv_converter import PDFToCSVConverter, DataRecord

class CustomDataRecord(DataRecord):
    def validate(self) -> bool:
        """Custom validation logic"""
        if len(self.values) < 3:
            return False
        
        # Example: First column should be numeric
        if not self.values[0].isdigit():
            return False
        
        # Example: Second column should be alphabetic
        if not self.values[1].isalpha():
            return False
        
        return True
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit your changes: `git commit -m 'feat: add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to all functions
- Write tests for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF processing
- Progress bars powered by [tqdm](https://github.com/tqdm/tqdm)
- Inspired by the need for efficient PDF data extraction

## Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/salemaljebaly/pdf2csv/issues)
- 📖 Documentation: [Wiki](https://github.com/salemaljebaly/pdf2csv/wiki)

## Changelog

### Version 1.0.0 (2025-07-09)
- Initial release
- Support for structured, regex, and table extraction
- Data validation
- Progress tracking
- Comprehensive error handling

---

Made with ❤️ by @salemaljebaly