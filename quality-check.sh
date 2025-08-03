#!/bin/bash
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

echo -e "${YELLOW}Running quality checks for clearflow${NC}"

print_header "Ensuring virtual environment"
# Check if virtual environment exists in current directory
if [ ! -d ".venv" ]; then
    echo "Creating new virtual environment in current directory..."
    uv venv .venv --seed
    check_step "Virtual environment setup"
else
    echo "Using existing virtual environment at ./.venv"
    check_step "Virtual environment check"
fi

print_header "Syncing dependencies"
# Sync dependencies using dependency groups (not extras)
uv sync --group dev
check_step "Dependencies synchronization"

print_header "Automatically fixing linting issues"
# Run ruff to automatically fix issues on clearflow and tests
uv run ruff check --fix clearflow tests
check_step "Ruff automatic fixes"

print_header "Running linting checks"
# Run ruff check with explicit exit-on-fix and fail the build if it finds issues
uv run ruff check --exit-non-zero-on-fix clearflow tests
check_step "Ruff linting"

print_header "Automatically applying formatting"
# Run ruff to automatically apply formatting
uv run ruff format clearflow tests
check_step "Ruff automatic formatting"

print_header "Running formatting checks"
# Run ruff format check
uv run ruff format --check clearflow tests
check_step "Ruff formatting check"

print_header "Running mypy type checks"
# Type errors are critical issues that must be fixed - treat ALL warnings as errors
uv run mypy --strict clearflow tests
check_step "Mypy type checking"

print_header "Running pyright type checks"
# Pyright errors are equally critical
uv run pyright clearflow tests
check_step "Pyright type checking"

# Check examples using dedicated script
echo -e "\n${YELLOW}==== Checking examples ====${NC}"
if [ -f "./check-examples.sh" ]; then
    ./check-examples.sh
    echo -e "${GREEN}✓ Example checks passed${NC}"
else
    echo -e "${YELLOW}No check-examples.sh found, skipping example checks${NC}"
fi

print_header "Running tests"
if [ -d "tests" ]; then
    echo "Running tests..."
    uv run pytest -x -v tests
    test_status=$?

    if [ $test_status -ne 0 ]; then
        echo -e "${RED}✗ Tests failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${YELLOW}No tests directory found, skipping tests${NC}"
fi


echo -e "\n${GREEN}All quality checks passed for clearflow! ✨ 🍰 ✨${NC}"