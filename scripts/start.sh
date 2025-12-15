#!/bin/bash

# SmartFridge - Application Startup Script
# Starts the Flask backend for use with GitHub Pages frontend

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${CYAN}======================================"
    echo "  SmartFridge - Backend Startup"
    echo "======================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_section() {
    echo ""
    echo -e "${BLUE}→ $1${NC}"
}

# Main execution
print_header

# Check if running in Codespaces
if [ -n "$CODESPACES" ]; then
    print_info "Running in GitHub Codespaces environment"
    ENVIRONMENT="codespaces"
else
    print_info "Running in local environment"
    ENVIRONMENT="local"
fi

# Check Python installation
print_section "Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.12 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Check PostgreSQL
print_section "Checking PostgreSQL..."
if sudo service postgresql status > /dev/null 2>&1; then
    print_success "PostgreSQL is running"
else
    print_error "PostgreSQL is not running"
    echo ""
    echo "To fix this, run:"
    echo "  ./setup_and_fix_postgres.sh"
    echo ""
    exit 1
fi

# Verify database exists
print_section "Verifying database..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw smartfridge; then
    RECIPE_COUNT=$(sudo -u postgres psql -d smartfridge -t -c "SELECT COUNT(*) FROM recipe;" 2>/dev/null | tr -d ' ')
    if [ -n "$RECIPE_COUNT" ] && [ "$RECIPE_COUNT" -gt 0 ]; then
        print_success "Database 'smartfridge' ready ($RECIPE_COUNT recipes)"
    else
        print_error "Database exists but may not be initialized"
        echo ""
        echo "To initialize the database, run:"
        echo "  ./setup_and_fix_postgres.sh"
        echo ""
        exit 1
    fi
else
    print_error "Database 'smartfridge' not found"
    echo ""
    echo "To create and initialize the database, run:"
    echo "  ./setup_and_fix_postgres.sh"
    echo ""
    exit 1
fi

# Check and install dependencies
print_section "Checking Python dependencies..."
if python3 -c "import flask" 2>/dev/null; then
    print_success "Dependencies already installed"
else
    print_info "Installing dependencies from requirements.txt..."
    pip install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
fi

# Check .env file
print_section "Checking configuration..."
if [ -f ".env" ]; then
    print_success "Configuration file (.env) found"
else
    print_info "Creating default .env file..."
    cat > .env << 'EOF'
# SmartFridge Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smartfridge
DB_USER=postgres
DB_PASSWORD=

# Flask Configuration
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
EOF
    print_success "Default .env file created"
    print_info "Remember to update SECRET_KEY for production!"
fi

# Display startup information
echo ""
echo -e "${CYAN}======================================"
echo "  Starting Flask Backend Server"
echo "======================================${NC}"
echo ""

if [ "$ENVIRONMENT" = "codespaces" ]; then
    print_info "Backend will start on port 5000"
    print_info "Codespaces will automatically forward the port"
    echo ""
    print_info "Your frontend is deployed at:"
    echo "  ${YELLOW}GitHub Pages URL${NC} (e.g., https://klb4mv-a11y.github.io/SmartFridge)"
    echo ""
    print_info "Backend API will be accessible at:"
    echo "  ${YELLOW}Codespaces forwarded URL${NC} (check Ports tab)"
    echo ""
    print_info "Make sure your frontend API_BASE_URL points to the forwarded port!"
else
    print_info "Backend starting on http://localhost:5000"
    echo ""
    print_info "API Health Check:"
    echo "  curl http://localhost:5000/health"
    echo ""
    print_info "If using the frontend locally:"
    echo "  Open frontend/index.html in your browser"
    echo "  OR serve with: cd frontend && python3 -m http.server 8080"
fi

echo ""
print_info "Press Ctrl+C to stop the server"
echo ""
echo -e "${CYAN}======================================${NC}"
echo ""

# Start the Flask application
python3 api.py

# This will only execute if Flask exits
echo ""
print_info "Flask server stopped"