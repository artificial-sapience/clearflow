#!/bin/bash
set -e

# Parse command line arguments into categories
DIRS=""
FILES=""
TEST_SPECS=""
QUALITY_TARGETS=""

# Process each argument
if [ $# -gt 0 ]; then
    for arg in "$@"; do
        # Remove trailing slashes for consistency
        arg=$(echo "$arg" | sed 's|/$||')
        
        if [[ "$arg" == *"::"* ]]; then
            # Test specification like test.py::test_function
            TEST_SPECS="$TEST_SPECS $arg"
            # Extract base file for quality checks
            base_file="${arg%%::*}"
            FILES="$FILES $base_file"
        elif [[ -f "$arg" ]]; then
            # Regular file
            FILES="$FILES $arg"
        elif [[ -d "$arg" ]]; then
            # Directory
            DIRS="$DIRS $arg"
        else
            echo "Warning: $arg is not a file or directory, skipping"
        fi
    done
    
    # Build quality targets (dirs and files for quality checks)
    QUALITY_TARGETS="$DIRS $FILES"
else
    # No arguments - check everything
    QUALITY_TARGETS="clearflow tests examples linters"
fi

# Ensure we have something to check
if [ -z "$QUALITY_TARGETS" ]; then
    echo "Error: No valid targets found to check"
    exit 1
fi

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
        echo -e "${RED}MISSION-CRITICAL VIOLATION: Fix immediately before proceeding${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}Running MISSION-CRITICAL quality checks for: ${QUALITY_TARGETS}${NC}"
echo -e "${YELLOW}Standards: Aerospace/Healthcare/Financial grade${NC}"
echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
echo -e "${RED}⚠️  IMPORTANT: ALL violations must be FIXED, not suppressed${NC}"
echo -e "${RED}⚠️  AI ASSISTANTS: Never use # noqa, # type: ignore, or ignore lists${NC}"
echo -e "${RED}⚠️  without explicit user approval. FIX THE ROOT CAUSE.${NC}"
echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"

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
# Sync dependencies using dependency groups
uv sync --group dev
check_step "Dependencies synchronization"

# ============================================================
# CRITICAL: Architecture compliance MUST come FIRST
# This prevents any violations from being introduced
# ============================================================

print_header "🚨 ARCHITECTURE COMPLIANCE CHECK (ZERO TOLERANCE)"
echo "Enforcing clean architecture principles..."
python3 linters/check-architecture-compliance.py $QUALITY_TARGETS
check_step "Architecture compliance check"

print_header "🔒 IMMUTABILITY COMPLIANCE CHECK"
echo "Enforcing deep immutability requirements..."
python3 linters/check-immutability.py $QUALITY_TARGETS
check_step "Immutability compliance check"

# Only run test suite compliance if we're checking test files
if [ -d "tests" ] || [[ "$QUALITY_TARGETS" == *"test"* ]]; then
    print_header "🧪 TEST SUITE COMPLIANCE CHECK"
    echo "Enforcing test isolation and resource management..."
    python3 linters/check-test-suite-compliance.py $QUALITY_TARGETS
    check_step "Test suite compliance check"
fi

print_header "Automatically fixing linting issues"
# Run ruff to automatically fix issues on specified targets
uv run ruff check --fix $QUALITY_TARGETS
check_step "Ruff automatic fixes"

print_header "Running linting checks"
# Ruff auto-reads [tool.ruff] from pyproject.toml
# Only pass explicit targets if user provided them
if [ $# -gt 0 ]; then
    RUFF_ARGS="$QUALITY_TARGETS"
else
    RUFF_ARGS=""  # Let ruff use its configured paths
fi
if ! uv run ruff check --exit-non-zero-on-fix $RUFF_ARGS; then
    echo -e "${RED}✗ Linting violations detected${NC}"
    echo -e "${YELLOW}⚠️  DO NOT suppress with # noqa comments${NC}"
    echo -e "${YELLOW}⚠️  DO NOT add violations to ignore lists in pyproject.toml${NC}"
    echo -e "${YELLOW}⚠️  AI ASSISTANTS: Never suppress lints without explicit user approval${NC}"
    echo -e "${GREEN}✅ FIX THE ROOT CAUSE: Refactor code to comply with standards${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Ruff linting passed${NC}"

print_header "Automatically applying formatting"
# Run ruff to automatically apply formatting
uv run ruff format $QUALITY_TARGETS
check_step "Ruff automatic formatting"

print_header "Running formatting checks"
# Run ruff format check
uv run ruff format --check $QUALITY_TARGETS
check_step "Ruff formatting check"

print_header "Running mypy type checks"
# Mypy auto-reads [tool.mypy] from pyproject.toml including 'strict = true'
# Only pass explicit targets if user provided them
if [ $# -gt 0 ]; then
    MYPY_ARGS="$QUALITY_TARGETS"
else
    MYPY_ARGS=""  # Let mypy use its configured include paths
fi
if ! uv run mypy $MYPY_ARGS; then
    echo -e "${RED}✗ Type checking violations detected${NC}"
    echo -e "${YELLOW}⚠️  DO NOT suppress with # type: ignore comments${NC}"
    echo -e "${YELLOW}⚠️  DO NOT add to [tool.mypy.overrides] in pyproject.toml${NC}"
    echo -e "${YELLOW}⚠️  AI ASSISTANTS: Never suppress type errors without explicit user approval${NC}"
    echo -e "${GREEN}✅ FIX THE ROOT CAUSE: Add proper type annotations${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Mypy type checking passed${NC}"

print_header "Running pyright type checks"
# Pyright auto-reads [tool.pyright] from pyproject.toml
# Only pass explicit targets if user provided them
if [ $# -gt 0 ]; then
    PYRIGHT_ARGS="$QUALITY_TARGETS"
else
    PYRIGHT_ARGS=""  # Let pyright use its configured include paths
fi
# Force pyright to use latest version to avoid version warnings
if ! PYRIGHT_PYTHON_FORCE_VERSION=latest uv run pyright $PYRIGHT_ARGS; then
    echo -e "${RED}✗ Pyright type checking violations detected${NC}"
    echo -e "${YELLOW}⚠️  DO NOT suppress with # type: ignore or # pyright: ignore comments${NC}"
    echo -e "${YELLOW}⚠️  DO NOT weaken pyproject.toml settings${NC}"
    echo -e "${YELLOW}⚠️  AI ASSISTANTS: Never suppress type errors without explicit user approval${NC}"
    echo -e "${GREEN}✅ FIX THE ROOT CAUSE: Add proper type annotations${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Pyright type checking passed${NC}"

# Determine what tests to run based on the targets
TEST_TARGETS=""
should_run_tests=false
require_coverage=false

# Check if we should run tests
if [ $# -eq 0 ]; then
    # No args - run all tests with coverage
    should_run_tests=true
    require_coverage=true
    TEST_TARGETS="tests"
else
    # Check each item to see if it's test-related
    for item in $FILES $DIRS; do
        if [[ "$item" == test_*.py ]] || [[ "$item" == *_test.py ]]; then
            # Test file
            should_run_tests=true
            TEST_TARGETS="$TEST_TARGETS $item"
        elif [[ "$item" == *"tests"* ]]; then
            # Tests directory
            should_run_tests=true
            TEST_TARGETS="$TEST_TARGETS $item"
            # Full test directory requires coverage
            if [[ "$item" == "tests" ]]; then
                require_coverage=true
            fi
        fi
    done
    
    # If test specs were provided, run those specifically
    if [ -n "$TEST_SPECS" ]; then
        should_run_tests=true
        TEST_TARGETS="$TEST_SPECS"
        require_coverage=false  # No coverage for specific tests
    fi
fi

if [ "$should_run_tests" = true ]; then
    print_header "Running tests"
    
    if [ -n "$TEST_SPECS" ]; then
        # Running specific test specs
        echo "Running specific test(s): $TEST_SPECS"
        uv run pytest -xvs $TEST_SPECS
        test_status=$?
    elif [ "$require_coverage" = true ]; then
        # Running full test suite with coverage
        echo "Running all tests with coverage..."
        uv run pytest -xv --cov=clearflow --cov-report=term-missing --cov-fail-under=100 $TEST_TARGETS
        test_status=$?
        
        if [ $test_status -ne 0 ]; then
            echo -e "${RED}✗ Tests failed or coverage below 100%${NC}"
            echo -e "${RED}MISSION-CRITICAL: Must maintain 100% coverage${NC}"
            echo -e "${YELLOW}⚠️  DO NOT use # pragma: no cover to exclude lines${NC}"
            echo -e "${YELLOW}⚠️  DO NOT weaken coverage requirements${NC}"
            echo -e "${YELLOW}⚠️  AI ASSISTANTS: Never reduce coverage without explicit user approval${NC}"
            echo -e "${GREEN}✅ FIX THE ROOT CAUSE: Write proper tests for all code paths${NC}"
            exit 1
        fi
    else
        # Running specific test files without coverage requirement
        echo "Running test file(s): $TEST_TARGETS"
        uv run pytest -xv $TEST_TARGETS
        test_status=$?
        
        if [ $test_status -ne 0 ]; then
            echo -e "${RED}✗ Tests failed${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${YELLOW}Skipping tests (no test targets specified)${NC}"
fi

print_header "Security audit - CVE scanning"
# Skip CVE check for clearflow/ since it has zero dependencies
# Only run for full project or tests
if [[ "$QUALITY_TARGETS" == *"clearflow"* ]] && [[ "$QUALITY_TARGETS" != *"test"* ]]; then
    echo -e "${YELLOW}Skipping CVE scan (clearflow has zero dependencies)${NC}"
else
    echo "Checking for known CVE vulnerabilities in dependencies..."
    # PYSEC-2022-42969: py library ReDoS vulnerability - approved suppression for test dependency
    # The py library is a pytest dependency only used in testing, not in production code
    if ! uv run pip-audit --fix --desc --ignore-vuln PYSEC-2022-42969 2>/dev/null; then
        echo -e "${RED}✗ CVE vulnerabilities detected in dependencies${NC}"
        echo -e "${RED}MISSION-CRITICAL: Security vulnerabilities found${NC}"
        echo -e "${YELLOW}⚠️  Update vulnerable dependencies immediately${NC}"
        echo -e "${GREEN}✅ FIX THE ROOT CAUSE: Update to secure versions${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ CVE scan passed - no known vulnerabilities${NC}"
fi

print_header "Security audit - AST analysis with Bandit"
# Bandit auto-reads [tool.bandit] from pyproject.toml when installed with [toml] extra
echo "Checking for security issues (SQL injection, hardcoded passwords, etc.)..."
# Only run Bandit on Python files/directories in the targets
has_python_target=false
for target in $QUALITY_TARGETS; do
    if [[ -d "$target" ]] || [[ "$target" == *.py ]]; then
        has_python_target=true
        break
    fi
done

if [ "$has_python_target" = true ]; then
    # Bandit will use pyproject.toml config automatically
    # Exclude tests from security analysis
    bandit_targets=""
    for target in $QUALITY_TARGETS; do
        if [[ "$target" != *"test"* ]]; then
            bandit_targets="$bandit_targets $target"
        fi
    done
    if [ -n "$bandit_targets" ]; then
        uv run bandit -r $bandit_targets -f txt 2>&1 | tail -5
        check_step "Bandit security analysis"
    else
        echo -e "${YELLOW}Skipping Bandit (only test files in targets)${NC}"
    fi
else
    echo -e "${YELLOW}Skipping Bandit (no Python targets)${NC}"
fi

print_header "Code complexity check - Xenon"
# Check complexity thresholds (A grade requirement)
echo "Enforcing complexity grade A..."
# Only run on Python directories/files
xenon_targets=""
for target in $QUALITY_TARGETS; do
    if [[ -d "$target" ]] || [[ "$target" == *.py ]]; then
        xenon_targets="$xenon_targets $target"
    fi
done

if [ -n "$xenon_targets" ]; then
    if ! uv run xenon --max-average A --max-modules A --max-absolute A $xenon_targets 2>&1; then
        echo -e "${RED}✗ Functions exceeding complexity threshold${NC}"
        echo -e "${RED}MISSION-CRITICAL: Complexity violations detected${NC}"
        echo -e "${YELLOW}⚠️  DO NOT suppress or increase complexity thresholds${NC}"
        echo -e "${YELLOW}⚠️  AI ASSISTANTS: Never increase complexity limits without explicit user approval${NC}"
        echo -e "${GREEN}✅ FIX THE ROOT CAUSE: Refactor complex functions into simpler ones${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Xenon complexity check passed${NC}"
else
    echo -e "${YELLOW}Skipping Xenon (no Python targets)${NC}"
fi

print_header "Dead code detection - Vulture"
# Vulture doesn't auto-read pyproject.toml
echo "Checking for dead/unused code..."
# Only run on Python directories/files
vulture_targets=""
for target in $QUALITY_TARGETS; do
    if [[ -d "$target" ]] || [[ "$target" == *.py ]]; then
        vulture_targets="$vulture_targets $target"
    fi
done

if [ -n "$vulture_targets" ]; then
    vulture_output=$(uv run vulture $vulture_targets --min-confidence 80 2>&1)
    # Use grep -c but handle the case when it returns exit code 1 for no matches
    vulture_count=$(echo "$vulture_output" | grep -c "unused" || true)
    if [ "$vulture_count" -gt 0 ]; then
        echo -e "${RED}✗ Found $vulture_count dead code issues${NC}"
        echo "$vulture_output"
        echo -e "${RED}MISSION-CRITICAL: Dead code detected${NC}"
        echo -e "${YELLOW}⚠️  DO NOT suppress dead code warnings${NC}"
        echo -e "${GREEN}✅ FIX THE ROOT CAUSE: Remove unused code${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Dead code check passed - no unused code${NC}"
else
    echo -e "${YELLOW}Skipping Vulture (no Python targets)${NC}"
fi

print_header "Complexity metrics - Radon"
# Check cyclomatic complexity average
echo "Checking average complexity (must be ≤ A grade)..."
# Only run on Python directories/files
radon_targets=""
for target in $QUALITY_TARGETS; do
    if [[ -d "$target" ]] || [[ "$target" == *.py ]]; then
        radon_targets="$radon_targets $target"
    fi
done

if [ -n "$radon_targets" ]; then
    # Run radon on each target and aggregate results
    total_complexity=0
    total_items=0
    for target in $radon_targets; do
        if [[ -d "$target" ]] || [[ -f "$target" ]]; then
            result=$(uv run radon cc "$target" -a -j 2>/dev/null || echo "{}")
            # Extract average complexity for this target
            target_name=$(basename "$target")
            avg=$(echo "$result" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('$target_name', {}).get('average_complexity', 0))" 2>/dev/null || echo "0")
            if [ "$avg" != "0" ]; then
                total_complexity=$(echo "$total_complexity + $avg" | bc)
                total_items=$((total_items + 1))
            fi
        fi
    done
    
    if [ "$total_items" -gt 0 ]; then
        avg_cc=$(echo "scale=2; $total_complexity / $total_items" | bc)
        # Check if avg_cc is greater than 5 (A grade threshold)
        if python3 -c "import sys; sys.exit(0 if float('$avg_cc') <= 5 else 1)" 2>/dev/null; then
            echo -e "${GREEN}✓ Radon complexity check passed (avg: $avg_cc)${NC}"
        else
            echo -e "${RED}✗ Average complexity $avg_cc exceeds A grade (max 5)${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Radon complexity check passed (no measurable code)${NC}"
    fi
else
    echo -e "${YELLOW}Skipping Radon (no Python targets)${NC}"
fi

# Check examples only if they're in QUALITY_TARGETS
if [[ "$QUALITY_TARGETS" == *"examples"* ]]; then
    if [ -d "examples" ]; then
        print_header "Checking examples"
        echo "Running quality checks on examples..."
        
        # Run minimal checks on examples (they're allowed more flexibility)
        uv run ruff check examples/
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}⚠️  Examples have linting issues - consider fixing${NC}"
        fi
        
        uv run mypy examples/ || true  # Don't fail on example type issues
        echo -e "${GREEN}✓ Example checks complete${NC}"
    else
        echo -e "${YELLOW}Examples directory not found${NC}"
    fi
fi

echo -e "\n${GREEN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  MISSION-CRITICAL QUALITY CHECKS PASSED! 🚀✨🎯  ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"