#!/bin/bash

echo "=========================================="
echo "SmartFridge Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_header() {
    echo -e "${BLUE}▶${NC} $1"
}

# Check if pytest is installed
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "pytest not found. Installing testing dependencies..."
    pip install -q pytest pytest-cov pytest-mock coverage
    print_success "Testing dependencies installed"
fi

# Check if in correct directory
if [ ! -d "tests" ]; then
    echo "Error: tests/ directory not found. Run from project root."
    exit 1
fi

echo ""
print_header "Running tests with coverage..."
echo ""

# Run pytest with coverage
pytest -q --cov=. --cov-report=term --cov-report=xml --cov-report=html

RESULT=$?

echo ""
echo "=========================================="
if [ $RESULT -eq 0 ]; then
    print_success "All tests passed!"
else
    echo " Some tests failed"
fi
echo "=========================================="
echo ""

if [ $RESULT -eq 0 ]; then
    echo "📊 Coverage Reports Generated:"
    echo "   • Terminal output (above)"
    echo "   • XML: coverage.xml"
    echo "   • HTML: htmlcov/index.html"
    echo ""
    echo "To view HTML coverage report:"
    echo "   Open: htmlcov/index.html in your browser"
    echo ""
fi

exit $RESULT