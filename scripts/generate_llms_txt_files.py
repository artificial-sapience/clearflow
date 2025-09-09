#!/usr/bin/env python3
"""Generate llms.txt and llms-full.txt files for AI assistant integration."""

import subprocess  # noqa: S404
import sys
from pathlib import Path


def generate_llms_txt(project_root: Path) -> Path:
    """Generate llms.txt with curated documentation links.

    Args:
        project_root: Path to project root.

    Returns:
        Path: Path to generated llms.txt file.
    """
    llms_txt_path = project_root / "llms.txt"

    # Define the content structure
    content = """# ClearFlow

> Compose type-safe flows for emergent AI.

## Quick Start

- [Install from PyPI](https://pypi.org/project/clearflow/): pip install clearflow

## Documentation

- [README](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/README.md): Complete overview and quickstart guide
- [Core API](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/clearflow/__init__.py): Complete implementation - Node, NodeResult, Flow, and exceptions in a single module
- [CLAUDE Guidelines](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/CLAUDE.md): Development guidelines and architectural principles

## Examples

- [Chat](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/examples/chat/README.md): Simple conversational flow with OpenAI integration
- [Portfolio Analysis](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/examples/portfolio_analysis/README.md): Financial data processing with type-safe transformations
- [RAG Pipeline](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/examples/rag/README.md): Retrieval-augmented generation workflow implementation

## Testing

- [Flow Tests](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/tests/test_flow.py): Complete flow orchestration patterns
- [Node Tests](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/tests/test_node.py): Node lifecycle and behavior
- [Error Handling](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/tests/test_error_handling.py): Error handling patterns
- [Type Transformations](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/tests/test_type_transformations.py): Type-safe state transformations
- [Flow Validation](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/tests/test_flow_builder_validation.py): Routing and validation rules

## Optional

- [Migration Guide](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/MIGRATION.md): Upgrading from v0.x to v1.x
- [License](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/LICENSE): MIT License
"""

    llms_txt_path.write_text(content)
    print(f"✅ Generated {llms_txt_path}")
    return llms_txt_path


def generate_llms_full(llms_txt_path: Path) -> Path:
    """Generate llms-full.txt from llms.txt using llms_txt2ctx.

    Args:
        llms_txt_path: Path to llms.txt file.

    Returns:
        Path: Path to generated llms-full.txt file.
    """
    llms_full_path = llms_txt_path.parent / "llms-full.txt"

    try:
        result = subprocess.run(  # noqa: S603
            ["uv", "run", "llms_txt2ctx", "--optional", "true", str(llms_txt_path)],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        )

        llms_full_path.write_text(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating llms-full.txt: {e}")
        print(f"   stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: llms_txt2ctx not found")
        print("   Install with: uv add --dev llms-txt")
        sys.exit(1)
    else:
        print(f"✅ Generated {llms_full_path}")
        return llms_full_path


def main() -> None:
    """Generate both llms.txt and llms-full.txt files."""
    project_root = Path(__file__).parent.parent

    print("🚀 Generating llms.txt files for AI assistant integration\n")

    # Generate llms.txt
    llms_txt_path = generate_llms_txt(project_root)

    # Generate llms-full.txt from llms.txt
    llms_full_path = generate_llms_full(llms_txt_path)

    # Display file sizes
    llms_size = llms_txt_path.stat().st_size / 1024
    full_size = llms_full_path.stat().st_size / 1024

    print("\n📊 File sizes:")
    print(f"   llms.txt: {llms_size:.1f} KB")
    print(f"   llms-full.txt: {full_size:.1f} KB")
    print("\n✨ Both files generated successfully!")


if __name__ == "__main__":
    main()
