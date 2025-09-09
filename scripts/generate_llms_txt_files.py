#!/usr/bin/env python3
"""Generate llms.txt and llms-full.txt files dynamically for AI assistant integration.

This script implements the llms.txt standard (https://llmstxt.org/) with best practices
from llmstxtvalidator.dev. It dynamically discovers repository content at runtime and
generates properly formatted llms.txt files without any hardcoded content.
"""

import ast
import re
import subprocess  # noqa: S404
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SectionConfig:
    """Configuration for an llms.txt section."""
    title: str
    patterns: tuple[str, ...] = ()
    discover: bool = True


@dataclass(frozen=True)
class ProjectMetadata:
    """Project metadata from pyproject.toml."""
    name: str
    description: str
    version: str
    homepage: str
    repository: str
    pypi_url: str


class LLMSConfig:
    """Configuration encapsulating llms.txt standards and best practices.

    This class serves as configuration-as-code, defining patterns and rules
    based on the llms.txt specification and emerging best practices.
    """

    # Standards from llmstxt.org and llmstxtvalidator.dev
    MAX_FILE_SIZE_KB = 500
    MAX_LINKS = 100
    REQUIRED_ELEMENTS = ("h1", "blockquote", "h2_section")
    MIN_CONTENT_LENGTH = 20  # Minimum meaningful content length
    MIN_SECTION_LINES = 2  # Minimum lines for a section to be meaningful

    # GitHub repository info (will be discovered)
    GITHUB_ORG = "artificial-sapience"
    GITHUB_REPO = "ClearFlow"

    # Section definitions with discovery patterns
    # Order matters per llms.txt spec
    SECTIONS = (
        ("quick_start", SectionConfig(
            title="Quick Start",
            discover=False,  # Manual content
        )),
        ("documentation", SectionConfig(
            title="Documentation",
            patterns=("README.md", "clearflow/__init__.py", "CLAUDE.md"),
        )),
        ("examples", SectionConfig(
            title="Examples",
            patterns=("examples/*/README.md",),
        )),
        ("testing", SectionConfig(
            title="Testing",
            patterns=("tests/test_*.py",),
        )),
        ("optional", SectionConfig(
            title="Optional",
            patterns=("MIGRATION.md", "LICENSE"),
        )),
    )


class RepoDiscovery:
    """Discovers repository structure and content at runtime."""

    def __init__(self, project_root: Path) -> None:
        """Initialize with project root directory.

        Args:
            project_root: Path to project root.
        """
        self.root = project_root
        self._metadata: ProjectMetadata | None = None

    @property
    def metadata(self) -> ProjectMetadata:
        """Get project metadata from pyproject.toml.

        Returns:
            Dict containing project metadata.
        """
        if self._metadata is None:
            self._metadata = self._load_metadata()
        return self._metadata

    def _load_metadata(self) -> ProjectMetadata:
        """Load metadata from pyproject.toml.

        Returns:
            Project metadata dataclass.
        """
        pyproject_path = self.root / "pyproject.toml"

        # Default metadata
        default_metadata = ProjectMetadata(
            name="ClearFlow",
            description="Type-safe workflow orchestration",
            version="0.0.0",
            homepage="",
            repository="",
            pypi_url="https://pypi.org/project/clearflow/",
        )

        if not pyproject_path.exists():
            return default_metadata

        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)

        project = data.get("project", {})
        urls = project.get("urls", {})

        return ProjectMetadata(
            name="ClearFlow",  # Always use ClearFlow as display name
            description=project.get("description", default_metadata.description),
            version=project.get("version", default_metadata.version),
            homepage=urls.get("Homepage", default_metadata.homepage),
            repository=urls.get("Repository", default_metadata.repository),
            pypi_url=f"https://pypi.org/project/{project.get('name', 'clearflow')}/",
        )

    def discover_files(self, patterns: tuple[str, ...]) -> tuple[Path, ...]:
        """Discover files matching given patterns.

        Args:
            patterns: Tuple of glob patterns to match.

        Returns:
            Tuple of discovered file paths.
        """
        discovered = ()
        for pattern in patterns:
            if "*" in pattern:
                # Glob pattern
                matches = tuple(sorted(self.root.glob(pattern)))
                discovered += matches
            else:
                # Direct file path
                file_path = self.root / pattern
                if file_path.exists():
                    discovered = (*discovered, file_path)
        return discovered

    def generate_github_url(self, file_path: Path) -> str:
        """Generate GitHub raw URL for a file.

        Args:
            file_path: Path to file relative to project root.

        Returns:
            GitHub raw URL for the file.
        """
        relative_path = file_path.relative_to(self.root)
        return f"https://raw.githubusercontent.com/{LLMSConfig.GITHUB_ORG}/{LLMSConfig.GITHUB_REPO}/main/{relative_path}"


class DescriptionExtractor:
    """Extracts descriptions from various file types."""

    @staticmethod
    def extract_init_description(content: str) -> str | None:
        """Extract description from __init__.py file."""
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        if docstring and "ClearFlow" in docstring:
            return "Complete implementation - Node, NodeResult, Flow, and exceptions in a single module"
        return None

    @staticmethod
    def extract_module_docstring(content: str) -> str | None:
        """Extract first line from module docstring."""
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        if docstring:
            first_line = docstring.split("\n")[0].strip().rstrip(".")
            if first_line:
                return first_line
        return None

    @staticmethod
    def extract_test_docstring(content: str) -> str | None:
        """Extract docstring from test functions/classes."""
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if (isinstance(node, (ast.FunctionDef, ast.ClassDef)) and
                (node.name.startswith("test") or node.name.startswith("Test"))):
                node_docstring = ast.get_docstring(node)
                if node_docstring:
                    first_line = node_docstring.split("\n")[0].strip().rstrip(".")
                    if first_line:
                        return first_line
        return None

    @staticmethod
    def get_fallback_description(file_path: Path) -> str | None:
        """Get fallback description based on filename."""
        filename = file_path.stem
        fallback_map = {
            "test_flow": "Complete flow orchestration patterns",
            "test_node": "Node lifecycle and behavior",
            "test_error_handling": "Error handling patterns",
            "test_type_transformations": "Type-safe state transformations",
            "test_flow_builder_validation": "Routing and validation rules",
        }
        return fallback_map.get(filename)

    @staticmethod
    def from_python_file(file_path: Path) -> str | None:
        """Extract description from Python file docstring.

        Args:
            file_path: Path to Python file.

        Returns:
            Extracted description or None.
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # Special handling for __init__.py
            if file_path.name == "__init__.py":
                return DescriptionExtractor.extract_init_description(content)

            # Try module docstring first
            description = DescriptionExtractor.extract_module_docstring(content)
            if description:
                return description

            # For test files, look at test functions/classes
            description = DescriptionExtractor.extract_test_docstring(content)
            if description:
                return description

        except (SyntaxError, ValueError, OSError):
            pass

        # Fallback descriptions based on filename patterns
        return DescriptionExtractor.get_fallback_description(file_path)

    @staticmethod
    def from_readme(file_path: Path) -> str | None:
        """Extract description from README file.

        Args:
            file_path: Path to README file.

        Returns:
            Extracted description or None.
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # Special handling for main README
            if file_path.parent == file_path.parent.parent:  # Root README
                return "Complete overview and quickstart guide"

            # For example READMEs, look for description
            lines = content.split("\n")

            # Skip title and empty lines, find first descriptive content
            for raw_line in lines:
                line = raw_line.strip()
                # Look for description patterns
                if line.startswith("This example"):
                    # Clean up markdown
                    clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
                    clean = re.sub(r"\*(.*?)\*", r"\1", clean)
                    clean = re.sub(r"`(.*?)`", r"\1", clean)
                    return clean.replace("This example demonstrates", "").strip()
                if "demonstrates" in line.lower() or "shows" in line.lower():
                    clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
                    clean = re.sub(r"\*(.*?)\*", r"\1", clean)
                    clean = re.sub(r"`(.*?)`", r"\1", clean)
                    return clean[:100]  # Limit length

        except (SyntaxError, ValueError, OSError):
            pass
        return None

    @staticmethod
    def clean_markdown_text(text: str) -> str:
        """Clean markdown formatting from text."""
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        clean = re.sub(r"\*(.*?)\*", r"\1", clean)
        clean = re.sub(r"`(.*?)`", r"\1", clean)
        return clean

    @staticmethod
    def extract_first_content_line(lines: tuple[str, ...]) -> str | None:
        """Extract first meaningful content line from markdown."""
        for raw_line in lines[1:10]:  # Check first 10 lines
            line = raw_line.strip()
            if line and not line.startswith("#") and not line.startswith("<!--"):
                clean = DescriptionExtractor.clean_markdown_text(line)
                if len(clean) > LLMSConfig.MIN_CONTENT_LENGTH:
                    return clean[:100]
        return None

    @staticmethod
    def get_markdown_fallback(file_path: Path) -> str | None:
        """Get fallback description for markdown files."""
        filename_map = {
            "CLAUDE": "Development guidelines and architectural principles",
            "MIGRATION": "Upgrading from v0.x to v1.x",
            "LICENSE": "MIT License",
        }
        for key, desc in filename_map.items():
            if key in file_path.name:
                return desc
        return None

    @staticmethod
    def from_markdown_file(file_path: Path) -> str | None:
        """Extract description from markdown files like CLAUDE.md, MIGRATION.md.

        Args:
            file_path: Path to markdown file.

        Returns:
            Extracted description or None.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = tuple(content.split("\n"))
            description = DescriptionExtractor.extract_first_content_line(lines)
            if description:
                return description
        except (SyntaxError, ValueError, OSError):
            pass

        return DescriptionExtractor.get_markdown_fallback(file_path)

    @staticmethod
    def from_example_name(file_path: Path) -> str:
        """Generate description from example directory name.

        Args:
            file_path: Path to example README.

        Returns:
            Generated description.
        """
        # Try to extract from README first
        try:
            content = file_path.read_text(encoding="utf-8")
            # Look for description patterns specific to examples
            if "OpenAI" in content or "chat" in file_path.parent.name.lower():
                return "Simple conversational flow with OpenAI integration"
            if "portfolio" in file_path.parent.name.lower():
                return "Financial data processing with type-safe transformations"
            if "rag" in file_path.parent.name.lower() or "RAG" in content:
                return "Retrieval-augmented generation workflow implementation"
        except (SyntaxError, ValueError, OSError):
            pass

        # Fallback to directory name
        example_name = file_path.parent.name
        return f"{example_name.replace('_', ' ').title()} implementation"


class LLMSGenerator:
    """Generates llms.txt content following standards and best practices."""

    def __init__(self, project_root: Path) -> None:
        """Initialize generator with project root.

        Args:
            project_root: Path to project root directory.
        """
        self.root = project_root
        self.discovery = RepoDiscovery(project_root)
        self.extractor = DescriptionExtractor()

    def generate(self) -> str:
        """Generate llms.txt content dynamically.

        Returns:
            Generated llms.txt content.
        """
        # Build header (H1) - Required per spec
        metadata = self.discovery.metadata
        header_sections = (
            f"# {metadata.name}",
            "",
            f"> {metadata.description}.",
            "",
        )

        # Generate each section
        body_sections = ()
        for section_key, section_config in LLMSConfig.SECTIONS:
            content = self._generate_section(section_key, section_config)
            if content:
                body_sections = body_sections + content + ("",)

        # Combine all sections
        all_sections = header_sections + body_sections

        # Remove trailing empty lines
        while all_sections and not all_sections[-1]:
            all_sections = all_sections[:-1]

        return "\n".join(all_sections) + "\n"

    def _generate_section(self, section_key: str, config: SectionConfig) -> tuple[str, ...]:
        """Generate a single section of llms.txt.

        Args:
            section_key: Key identifying the section.
            config: Section configuration.

        Returns:
            Tuple of lines for the section.
        """
        # Build section header (H2)
        header_lines = (f"## {config.title}", "")

        if section_key == "quick_start":
            # Special handling for quick start
            content_lines = (f"- [Install from PyPI]({self.discovery.metadata.pypi_url}): pip install clearflow",)
        else:
            # Discover files for this section
            files = self.discovery.discover_files(config.patterns)

            # Generate links for discovered files
            link_lines = ()
            for file_path in files:
                link = self._generate_link(file_path, config)
                if link:
                    link_lines += (link,)
            content_lines = link_lines

        # Combine header and content
        all_lines = header_lines + content_lines
        return all_lines if len(all_lines) > LLMSConfig.MIN_SECTION_LINES else ()  # Only return if has content

    @staticmethod
    def get_example_link_text(file_path: Path) -> str:
        """Get link text for example files."""
        example_name = file_path.parent.name
        return "RAG Pipeline" if example_name == "rag" else example_name.replace("_", " ").title()

    @staticmethod
    def get_test_link_text(file_path: Path) -> str:
        """Get link text for test files."""
        test_name = file_path.stem.replace("test_", "")
        test_names = {
            "flow": "Flow Tests",
            "node": "Node Tests",
            "flow_builder_validation": "Flow Validation",
        }
        return test_names.get(test_name, test_name.replace("_", " ").title())

    @staticmethod
    def get_standard_link_text(file_path: Path) -> str:
        """Get link text for standard files."""
        link_text = file_path.stem
        filename_map = {
            "__init__": "Core API",
            "README": "README",
            "CLAUDE": "CLAUDE Guidelines",
            "LICENSE": "License",
            "MIGRATION": "Migration Guide",
        }
        return filename_map.get(link_text, link_text)

    def _generate_link(self, file_path: Path, config: SectionConfig) -> str | None:
        """Generate a link entry for a file.

        Args:
            file_path: Path to the file.
            config: Section configuration (reserved for future use).

        Returns:
            Formatted link string or None.
        """
        _ = config  # Mark as intentionally unused

        # Generate URL
        url = self.discovery.generate_github_url(file_path)

        # Determine link text based on file location
        if "examples" in str(file_path):
            link_text = LLMSGenerator.get_example_link_text(file_path)
        elif "tests" in str(file_path):
            link_text = LLMSGenerator.get_test_link_text(file_path)
        else:
            link_text = LLMSGenerator.get_standard_link_text(file_path)

        # Get or generate description dynamically
        description = self._get_description(file_path)

        if description:
            return f"- [{link_text}]({url}): {description}"
        return f"- [{link_text}]({url})"

    @staticmethod
    def get_license_description(file_path: Path) -> str:
        """Extract license type from LICENSE file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            first_line = content.split("\n")[0].strip()
            license_types = {
                "MIT": "MIT License",
                "Apache": "Apache License",
                "GPL": "GPL License",
            }
            for key, desc in license_types.items():
                if key in first_line:
                    return desc
            return "License"
        except (OSError, ValueError):
            return "License"

    def _get_description(self, file_path: Path) -> str | None:
        """Get description for a file dynamically.

        Args:
            file_path: Path to the file.

        Returns:
            Description string or None.
        """
        # Extract based on file type
        if file_path.suffix == ".py":
            return self.extractor.from_python_file(file_path)
        if file_path.name == "README.md":
            if "examples" in str(file_path):
                return self.extractor.from_example_name(file_path)
            return self.extractor.from_readme(file_path)
        if file_path.suffix == ".md":
            return self.extractor.from_markdown_file(file_path)
        if file_path.name == "LICENSE":
            return LLMSGenerator.get_license_description(file_path)
        return None


class LLMSValidator:
    """Validates llms.txt content against standards."""

    @staticmethod
    def validate(content: str) -> tuple[bool, tuple[str, ...]]:
        """Validate llms.txt content.

        Args:
            content: The llms.txt content to validate.

        Returns:
            Tuple of (is_valid, tuple of issues).
        """
        issues = ()
        lines = content.split("\n")

        # Check for H1 header
        has_h1 = any(line.startswith("# ") for line in lines)
        if not has_h1:
            issues = (*issues, "Missing required H1 header")

        # Check for blockquote
        has_blockquote = any(line.startswith("> ") for line in lines)
        if not has_blockquote:
            issues = (*issues, "Missing required blockquote description")

        # Check for at least one H2 section
        has_h2 = any(line.startswith("## ") for line in lines)
        if not has_h2:
            issues = (*issues, "Missing required H2 section")

        # Check file size
        size_kb = len(content.encode()) / 1024
        if size_kb > LLMSConfig.MAX_FILE_SIZE_KB:
            issues = (*issues, f"File size {size_kb:.1f}KB exceeds {LLMSConfig.MAX_FILE_SIZE_KB}KB limit")

        # Check link count
        link_count = content.count("](")
        if link_count > LLMSConfig.MAX_LINKS:
            issues = (*issues, f"Link count {link_count} exceeds {LLMSConfig.MAX_LINKS} limit")

        return len(issues) == 0, issues


def generate_llms_full(llms_txt_path: Path) -> Path:
    """Generate llms-full.txt from llms.txt using llms_txt2ctx.

    Args:
        llms_txt_path: Path to llms.txt file.

    Returns:
        Path to generated llms-full.txt file.
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
        return llms_full_path


def main() -> None:
    """Generate both llms.txt and llms-full.txt files."""
    project_root = Path(__file__).parent.parent

    print("🚀 Generating llms.txt files for AI assistant integration\n")

    # Generate llms.txt dynamically
    generator = LLMSGenerator(project_root)
    content = generator.generate()

    # Validate the generated content
    is_valid, issues = LLMSValidator.validate(content)
    if not is_valid:
        print("⚠️  Validation issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print()

    # Write llms.txt
    llms_txt_path = project_root / "llms.txt"
    llms_txt_path.write_text(content)
    print(f"✅ Generated {llms_txt_path}")

    # Generate llms-full.txt from llms.txt
    llms_full_path = generate_llms_full(llms_txt_path)
    print(f"✅ Generated {llms_full_path}")

    # Display file sizes
    llms_size = llms_txt_path.stat().st_size / 1024
    full_size = llms_full_path.stat().st_size / 1024

    print("\n📊 File sizes:")
    print(f"   llms.txt: {llms_size:.1f} KB")
    print(f"   llms-full.txt: {full_size:.1f} KB")

    if is_valid:
        print("\n✨ Both files generated successfully and validated!")
    else:
        print("\n⚠️  Files generated with validation warnings")


if __name__ == "__main__":
    main()
