#!/bin/bash

# Check all examples with strict quality standards

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Print section header
print_header() {
    echo -e "\n${YELLOW}==== $1 ====${NC}"
}

# Check command success and print result
check_step() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 passed${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}🔍 Checking examples...${NC}"

# Check if examples directory exists
if [ ! -d "examples" ]; then
    echo "✓ No examples directory found, skipping example checks"
    exit 0
fi

# Function to check Python files in an example directory
check_python_example() {
    local example_dir="$1"
    local example_name=$(basename "$example_dir")
    
    echo -e "\n${YELLOW}Checking example: $example_name${NC}"
    
    # Check if requirements.txt exists
    if [ -f "$example_dir/requirements.txt" ]; then
        echo "Found requirements.txt"
        
        # Create a temporary virtual environment for this example
        temp_venv="$example_dir/.temp_venv"
        echo "Creating temporary virtual environment..."
        uv venv "$temp_venv" --seed --quiet
        
        # Install the example's requirements
        echo "Installing example dependencies..."
        uv pip install -r "$example_dir/requirements.txt" --python "$temp_venv/bin/python" --quiet
        
        # Install ClearFlow itself
        uv pip install -e . --python "$temp_venv/bin/python" --quiet
        
        # Install dev dependencies for type checking
        uv pip install mypy pyright ruff --python "$temp_venv/bin/python" --quiet
    else
        echo "No requirements.txt found, using base environment"
        temp_venv=".venv"
    fi
    
    # Find Python files in this example
    python_files=$(find "$example_dir" -name "*.py" -type f | grep -v __pycache__ | grep -v .temp_venv || true)
    
    if [ -z "$python_files" ]; then
        echo "No Python files found in $example_name"
        return
    fi
    
    # Run strict checks on Python files
    print_header "Linting $example_name Python files"
    "$temp_venv/bin/ruff" check $python_files \
        --ignore=T201 \
        --ignore=CPY001 \
        --ignore=INP001 \
        --ignore=EXE001 \
        --fix
    check_step "Ruff linting for $example_name"
    
    print_header "Formatting $example_name Python files"
    "$temp_venv/bin/ruff" format $python_files
    check_step "Ruff formatting for $example_name"
    
    print_header "Type checking $example_name with mypy"
    "$temp_venv/bin/mypy" --strict $python_files \
        --ignore-missing-imports \
        --python-executable "$temp_venv/bin/python"
    check_step "Mypy type checking for $example_name"
    
    print_header "Type checking $example_name with pyright"
    PYRIGHT_PYTHON_FORCE_VERSION=latest "$temp_venv/bin/pyright" $python_files \
        --pythonpath "$temp_venv/bin/python"
    check_step "Pyright type checking for $example_name"
    
    # Clean up temporary venv if we created one
    if [ "$temp_venv" != ".venv" ] && [ -d "$temp_venv" ]; then
        echo "Cleaning up temporary virtual environment..."
        rm -rf "$temp_venv"
    fi
}


# Process each example directory
for example_dir in examples/*/; do
    if [ -d "$example_dir" ]; then
        # Check Python files with strict rules
        check_python_example "$example_dir"
    fi
done

echo -e "\n${GREEN}✓ All example checks complete!${NC}"