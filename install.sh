#!/bin/bash

# PDF to CSV Converter Installation Script
# This script sets up the PDF to CSV converter with all dependencies

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Check Python version
check_python() {
    print_info "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
    else
        print_error "Python is not installed. Please install Python 3.7 or higher."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.7"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python $PYTHON_VERSION is too old. Python 3.7+ is required."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_info "Virtual environment already exists. Skipping creation."
    else
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    fi
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment activation failed"
        exit 1
    fi
}

# Upgrade pip
upgrade_pip() {
    print_info "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1
    print_success "pip upgraded to $(pip --version | cut -d' ' -f2)"
}

# Install requirements
install_requirements() {
    print_info "Installing requirements..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Requirements installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Install development requirements (optional)
install_dev_requirements() {
    if [ "$1" = "--dev" ]; then
        print_info "Installing development requirements..."
        
        if [ -f "requirements-dev.txt" ]; then
            pip install -r requirements-dev.txt
            print_success "Development requirements installed"
            
            # Install pre-commit hooks
            print_info "Installing pre-commit hooks..."
            pre-commit install
            print_success "Pre-commit hooks installed"
        else
            print_error "requirements-dev.txt not found"
        fi
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    directories=("output" "logs" "temp")
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created $dir directory"
        fi
    done
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    if python pdf_to_csv_converter.py --version > /dev/null 2>&1; then
        print_success "Installation test passed"
        VERSION=$(python pdf_to_csv_converter.py --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
        print_success "PDF to CSV Converter $VERSION is ready to use!"
    else
        print_error "Installation test failed"
        exit 1
    fi
}

# Main installation process
main() {
    echo "======================================"
    echo "PDF to CSV Converter Installation"
    echo "======================================"
    echo
    
    # Check if we're in the right directory
    if [ ! -f "pdf_to_csv_converter.py" ]; then
        print_error "pdf_to_csv_converter.py not found. Are you in the correct directory?"
        exit 1
    fi
    
    # Run installation steps
    check_python
    create_venv
    activate_venv
    upgrade_pip
    install_requirements
    install_dev_requirements "$1"
    create_directories
    test_installation
    
    echo
    echo "======================================"
    print_success "Installation completed successfully!"
    echo "======================================"
    echo
    echo "To use the converter:"
    echo "  1. Activate the virtual environment:"
    echo "     source venv/bin/activate"
    echo "  2. Run the converter:"
    echo "     python pdf_to_csv_converter.py input.pdf output.csv"
    echo
    echo "For help:"
    echo "     python pdf_to_csv_converter.py --help"
    echo
}

# Run main function
main "$@"