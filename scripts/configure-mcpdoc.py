#!/usr/bin/env python3
"""Configure mcpdoc to serve ClearFlow's llms.txt documentation.

This script helps users configure mcpdoc (Model Context Protocol documentation server)
to serve ClearFlow's llms.txt to AI coding assistants like Claude Code, Cursor, and Windsurf.
"""

import json
import os
import platform
import subprocess  # noqa: S404  # Required for running uv/mcpdoc commands in dev setup
import sys
from pathlib import Path


def check_mcpdoc_installed() -> bool:
    """Check if mcpdoc is installed.

    Returns:
        bool: True if mcpdoc is installed, False otherwise.
    """
    try:
        result = subprocess.run(
            ["uv", "run", "mcpdoc", "--version"],  # noqa: S607  # Safe: hardcoded uv command with literal args
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    else:
        return result.returncode == 0


def install_mcpdoc() -> bool:
    """Install mcpdoc if not present.

    Returns:
        bool: True if installation succeeded, False otherwise.
    """
    print("📦 mcpdoc not found. Installing...")
    try:
        subprocess.run(
            ["uv", "add", "--dev", "mcpdoc"],  # noqa: S607  # Safe: hardcoded uv command with literal args
            check=True,
        )
    except subprocess.CalledProcessError:
        print("❌ Failed to install mcpdoc")
        print("   Please install manually: uv add --dev mcpdoc")
        return False
    else:
        print("✅ mcpdoc installed successfully")
        return True


def get_claude_config_path() -> Path:
    """Get the Claude Code configuration file path.

    Returns:
        Path: Path to the Claude Code configuration file.
    """
    system = platform.system()
    home = Path.home()

    if system == "Darwin":  # macOS
        primary = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        if primary.exists():
            return primary
        return home / ".claude.json"
    if system == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    # Linux and others
    return home / ".claude.json"


def update_claude_config(llms_url: str) -> bool:
    """Update Claude Code configuration to include ClearFlow mcpdoc server.

    Args:
        llms_url: URL to the llms.txt file.

    Returns:
        bool: True if configuration was updated successfully.
    """
    config_path = get_claude_config_path()

    # Create parent directory if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config or create new one
    if config_path.exists():
        with config_path.open(encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}

    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add or update ClearFlow configuration
    config["mcpServers"]["clearflow-docs"] = {
        "command": "uv",
        "args": ["run", "mcpdoc", "--urls", f"ClearFlow:{llms_url}"],
    }

    # Write updated config
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Updated Claude Code config: {config_path}")
    return True


def ensure_mcpdoc_installed() -> None:
    """Ensure mcpdoc is installed, exit if installation fails."""
    if not check_mcpdoc_installed():
        if not install_mcpdoc():
            sys.exit(1)
    else:
        print("✅ mcpdoc is already installed")


def get_documentation_url() -> str:
    """Get the GitHub documentation URL.

    Returns:
        str: The URL to the llms.txt file on GitHub.
    """
    llms_url = "https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/llms.txt"
    print(f"\n🌐 Using GitHub URL: {llms_url}")
    return llms_url


def configure_claude_if_requested(llms_url: str) -> None:
    """Ask about and perform Claude Code configuration if requested.

    Args:
        llms_url: URL to the llms.txt file.
    """
    print("\n🤖 Configure for Claude Code?")
    configure = input("Update Claude Code config to include ClearFlow? (y/n): ").strip().lower()

    if configure == "y":
        if update_claude_config(llms_url):
            print("\n✨ Configuration complete!")
            print("   Restart Claude Code to use ClearFlow documentation")
        else:
            print("\n⚠️  Configuration failed - use manual command above")
    else:
        print("\n✅ Setup complete!")
        print("   Use the manual command above to run mcpdoc")


def main() -> None:
    """Main configuration flow."""
    print("🚀 ClearFlow mcpdoc Configuration Helper\n")

    # Ensure mcpdoc is installed
    ensure_mcpdoc_installed()

    # Get documentation URL
    llms_url = get_documentation_url()

    # Show manual command
    print("\n📋 Manual command to run mcpdoc:")
    print(f"   mcpdoc --urls ClearFlow:{llms_url}")

    # Configure Claude if requested
    configure_claude_if_requested(llms_url)

    # Show test command
    print("\n🧪 Test the setup:")
    print(f"   mcpdoc --urls ClearFlow:{llms_url}")
    print("   Then in another terminal: curl http://localhost:8765/")


if __name__ == "__main__":
    main()
