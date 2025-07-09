# Contributing to PDF to CSV Converter

Thank you for your interest in contributing to the PDF to CSV Converter! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/salemaljebaly/pdf2csv/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Sample PDF (if possible)

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue with the `enhancement` label
3. Describe the feature and its use case
4. Explain why it would be valuable

### Code Contributions

#### Setup Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/salemaljebaly/pdf2csv.git
   cd pdf2csv
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

#### Development Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Write/update tests for your changes

4. Run tests:
   ```bash
   pytest tests/
   pytest --cov=pdf_to_csv_converter tests/  # With coverage
   ```

5. Run linters:
   ```bash
   black .
   flake8 .
   mypy pdf_to_csv_converter.py
   ```

6. Commit your changes using Conventional Commits:
   ```bash
   git commit -m "feat: add support for encrypted PDFs"
   git commit -m "fix: handle empty pages gracefully"
   git commit -m "docs: update installation instructions"
   ```

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Create a Pull Request

### Commit Message Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, missing semicolons, etc.)
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Adding or updating tests
- `build:` Build system changes
- `ci:` CI/CD changes
- `chore:` Other changes that don't modify src or test files

### Pull Request Guidelines

1. **PR Title**: Use Conventional Commits format
2. **Description**: Include:
   - Summary of changes
   - Related issue number (fixes #123)
   - Testing performed
   - Screenshots (if UI changes)
3. **Size**: Keep PRs focused and reasonably sized
4. **Tests**: All tests must pass
5. **Documentation**: Update relevant documentation

### Code Style Guidelines

1. **Python Style**:
   - Follow PEP 8
   - Use type hints
   - Maximum line length: 88 characters (Black default)

2. **Docstrings**:
   ```python
   def extract_data(pdf_path: str) -> List[Dict[str, str]]:
       """Extract structured data from PDF file.
       
       Args:
           pdf_path: Path to the PDF file
           
       Returns:
           List of dictionaries containing extracted data
           
       Raises:
           FileNotFoundError: If PDF file doesn't exist
           PDFProcessingError: If PDF cannot be processed
       """
   ```

3. **Error Handling**:
   - Use specific exceptions
   - Provide helpful error messages
   - Log errors appropriately

## Documentation

1. Update README.md for user-facing changes
2. Add docstrings to all functions
3. Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/)
4. Include code examples where helpful

## Release Process

1. Update version in `pdf_to_csv_converter.py`
2. Update CHANGELOG.md
3. Create a release PR
4. After merge, tag the release:
   ```bash
   git tag -a v1.0.1 -m "Release version 1.0.1"
   git push origin v1.0.1
   ```

## Getting Help

- 💬 [Discussions](https://github.com/yourusername/pdf2csv/discussions)
- 📧 Email: support@example.com
- 🐛 [Issues](https://github.com/yourusername/pdf2csv/issues)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🎉