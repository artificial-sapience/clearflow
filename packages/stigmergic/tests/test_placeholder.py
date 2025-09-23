"""Placeholder test for Stigmergic package.

This file exists to prevent coverage failures while the package is under development.
Once actual implementation begins, this should be replaced with real tests.
"""

from stigmergic import __version__, placeholder


def test_placeholder() -> None:
    """Placeholder test to indicate package is under development."""
    # This test exists to prevent coverage failures for the empty package
    # Remove this file when actual implementation and tests are added
    assert placeholder() == "Stigmergic package is under development"


def test_version() -> None:
    """Test that version is defined."""
    assert __version__ == "0.0.1"
