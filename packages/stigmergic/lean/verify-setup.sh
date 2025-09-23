#!/bin/bash
# Script to verify Lean 4 setup for Stigmergic Coordination

echo "=== Verifying Lean 4 Setup for Stigmergic Coordination ==="
echo

# Check if we're in the right directory
if [ ! -f "lakefile.lean" ]; then
    echo "Error: Not in the lean directory. Please run this script from packages/stigmergic/lean/"
    exit 1
fi

# Check Lean installation
echo "1. Checking Lean 4 installation..."
if command -v lean &> /dev/null; then
    echo "✓ Lean found at: $(which lean)"
    lean --version
else
    echo "✗ Lean not found. Please install Lean 4 first."
    echo "  Visit: https://leanprover.github.io/lean4/doc/setup.html"
    exit 1
fi
echo

# Check Lake installation
echo "2. Checking Lake installation..."
if command -v lake &> /dev/null; then
    echo "✓ Lake found at: $(which lake)"
    lake --version
else
    echo "✗ Lake not found. It should come with Lean 4."
    exit 1
fi
echo

# Update Lake packages
echo "3. Updating Lake packages..."
if lake update; then
    echo "✓ Lake update successful"
else
    echo "✗ Lake update failed"
    exit 1
fi
echo

# Build the project
echo "4. Building the project..."
if lake build; then
    echo "✓ Build successful!"
else
    echo "✗ Build failed. Check the error messages above."
    exit 1
fi
echo

# Verify key modules
echo "5. Verifying key modules..."
echo "   Checking Foundation layer..."
lake build Stigmergic.Foundation.Primitives > /dev/null 2>&1 && echo "   ✓ Primitives" || echo "   ✗ Primitives"

echo

echo "=== Setup Verification Complete ==="
echo
echo "Your Lean 4 environment is properly configured!"
echo "You can now start developing Stigmergic Coordination specifications."
echo
echo "Next steps:"
echo "- Open this directory in VS Code with the Lean 4 extension"
echo "- Start with Stigmergic/Foundation/Primitives.lean to see basic patterns"
echo "- Run 'lake build' to verify your changes compile"