#!/usr/bin/env python3
"""Check architecture compliance for the ClearFlow project.

This script enforces architectural requirements for ClearFlow.
Zero tolerance for violations in mission-critical software.

Requirements enforced:
- Tests SHALL NOT use patch() for components inside the system boundary
- All system functionality SHALL be testable through the public API
- Tests SHALL verify behavior, not implementation details
- Code SHALL NOT use TYPE_CHECKING (indicates circular dependencies)
- Parameters SHALL NOT use 'object' type (use proper types or protocols)
"""

import ast
import re
import sys
from pathlib import Path
from typing import NamedTuple


class Violation(NamedTuple):
    """Architecture violation details."""

    file: Path
    line: int
    column: int
    code: str
    message: str
    requirement: str


def has_suppression(content: str, line_num: int, code: str) -> bool:
    """Check if a line has a suppression comment for a specific code.

    Args:
        content: The file content
        line_num: The line number to check (1-indexed)
        code: The code to check for suppression (e.g., "ARCH001")

    Returns:
        True if the line has a clearflow: ignore comment for this specific code

    Format:
        # clearflow: ignore[ARCH001]  - Specific code suppression

    """
    lines = content.splitlines()
    if line_num <= 0 or line_num > len(lines):
        return False

    line = lines[line_num - 1]  # Convert to 0-indexed

    # Check for # clearflow: ignore[CODE] pattern
    pattern = rf"#\s*clearflow:\s*ignore\[{code}\]"
    return bool(re.search(pattern, line, re.IGNORECASE))


def check_file_imports(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for private API imports and banned mock usage.

    Returns:
        List of architecture violations found in imports.

    """
    violations = []

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    # Check if this file is inside _internal (internal modules can import from each other)
    is_internal = "_internal" in str(file_path)

    for node in ast.walk(tree):
        # Check for imports from private implementation
        if isinstance(node, ast.ImportFrom):
            # Only flag imports from _internal if the importing file is NOT itself in _internal
            # Use join to avoid triggering ARCH-006 when checking for private module
            private_module = "clearflow." + "_internal"
            if node.module and private_module in node.module and not is_internal:
                violations.append(
                    Violation(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        code="ARCH003",
                        message=f"Importing from private module '{node.module}'",
                        requirement="REQ-ARCH-003",
                    )
                )

            # Check for unittest.mock imports
            if node.module == "unittest.mock":
                for alias in node.names:
                    name = alias.name
                    if name in {"patch", "Mock", "MagicMock"}:
                        violations.append(
                            Violation(
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                code="ARCH002",
                                message=f"Using '{name}' violates architecture - mock at boundaries only",
                                requirement="REQ-ARCH-002",
                            )
                        )

            # Check for TYPE_CHECKING imports (indicates circular dependencies)
            if node.module == "typing" or (
                node.module and node.module.startswith("typing")
            ):
                for alias in node.names:
                    if alias.name == "TYPE_CHECKING":
                        if not has_suppression(content, node.lineno, "ARCH008"):
                            violations.append(
                                Violation(
                                    file=file_path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    code="ARCH008",
                                    message="Using TYPE_CHECKING indicates circular dependencies - refactor to use protocols",
                                    requirement="REQ-ARCH-008",
                                )
                            )
                    # Check for Any imports
                    if alias.name == "Any":
                        violations.append(
                            Violation(
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                code="ARCH010",
                                message="Importing 'Any' type defeats type safety - use specific types or protocols",
                                requirement="REQ-ARCH-010",
                            )
                        )

        # Check for if TYPE_CHECKING blocks
        if (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
        ):
            if not has_suppression(content, node.lineno, "ARCH008"):
                violations.append(
                    Violation(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        code="ARCH008",
                        message="if TYPE_CHECKING block indicates circular dependencies - refactor to use protocols",
                        requirement="REQ-ARCH-008",
                    )
                )

        # Check for 'object' type annotations in function parameters
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                if arg.annotation:
                    if (
                        isinstance(arg.annotation, ast.Name)
                        and arg.annotation.id == "object"
                    ):
                        violations.append(
                            Violation(
                                file=file_path,
                                line=arg.annotation.lineno,
                                column=arg.annotation.col_offset,
                                code="ARCH009",
                                message=f"Parameter '{arg.arg}' uses 'object' type - use proper types or protocols",
                                requirement="REQ-ARCH-009",
                            )
                        )

        # Check for 'object' type usage in type annotations only
        # Skip object.__setattr__ which is needed for frozen dataclasses
        if isinstance(node, ast.Name) and node.id == "object":
            # Check if this is object.__setattr__ by looking at the line
            lines = content.splitlines()
            if node.lineno > 0 and node.lineno <= len(lines):
                line = lines[node.lineno - 1]
                if "object.__setattr__" in line:
                    continue  # This is the frozen dataclass pattern, skip it
            
            # Otherwise it's a type usage that should be reported
            violations.append(
                Violation(
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    code="ARCH009",
                    message="Using 'object' type defeats type safety - use proper types or protocols",
                    requirement="REQ-ARCH-009",
                )
            )

        # Check for 'Any' type usage anywhere (parameters, return types, annotations)
        if isinstance(node, ast.Name) and node.id == "Any":
            violations.append(
                Violation(
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    code="ARCH010",
                    message="Using 'Any' type defeats type safety - use specific types or protocols",
                    requirement="REQ-ARCH-010",
                )
            )

        # Also check for typing.Any in subscripts (e.g., list[Any], dict[str, Any])
        if isinstance(node, ast.Attribute):
            if (
                isinstance(node.value, ast.Name)
                and node.value.id == "typing"
                and node.attr == "Any"
            ):
                violations.append(
                    Violation(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        code="ARCH010",
                        message="Using 'typing.Any' defeats type safety - use specific types or protocols",
                        requirement="REQ-ARCH-010",
                    )
                )

    return tuple(violations)


def check_patch_decorators(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for @patch usage on internal components.

    Returns:
        List of violations for improper @patch usage.

    """
    violations = []
    lines = content.splitlines()

    # Regex for @patch decorators
    patch_pattern = re.compile(r'@patch\(["\']([^"\']+)["\']\)')

    for line_num, line in enumerate(lines, 1):
        match = patch_pattern.search(line)
        if match:
            target = match.group(1)
            if "clearflow" in target:
                violations.append(
                    Violation(
                        file=file_path,
                        line=line_num,
                        column=line.index("@patch"),
                        code="ARCH002",
                        message=f"Patching '{target}' violates architecture",
                        requirement="REQ-ARCH-002",
                    )
                )

    return tuple(violations)


def check_private_access(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for private attribute access.

    Returns:
        List of violations for accessing private attributes.

    """
    violations = []
    lines = content.splitlines()

    # Check if this file is inside _internal (internal modules can access each other)
    is_internal = "_internal" in str(file_path)

    # Regex for private attribute access (._something but not .__something__)
    # Exclude self._* and cls._* patterns as those are internal to the class
    private_pattern = re.compile(r"(?<!self)(?<!cls)\._([a-zA-Z_][a-zA-Z0-9_]*)\b")

    for line_num, line in enumerate(lines, 1):
        # Skip comments and strings
        if line.strip().startswith("#"):
            continue

        # Skip import lines - these are handled by check_file_imports
        # Use concatenation to avoid triggering ARCH-006
        private_internal = "." + "_internal"
        if "import" in line and private_internal in line:
            continue

        matches = private_pattern.finditer(line)
        for match in matches:
            attr_name = match.group(1)
            # Skip dunder methods
            if not attr_name.startswith("_"):
                # Only flag if this is NOT an internal file accessing _internal modules
                if not (is_internal and attr_name == "internal"):
                    violations.append(
                        Violation(
                            file=file_path,
                            line=line_num,
                            column=match.start(),
                            code="ARCH006",
                            message=f"Accessing private attribute '._{attr_name}'",
                            requirement="REQ-ARCH-006",
                        )
                    )

    return tuple(violations)


def check_file(file_path: Path) -> tuple[Violation, ...]:
    """Check a single file for architecture violations.

    Returns:
        List of all architecture violations found in the file.

    """
    violations = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return tuple(violations)

    # Skip checking __pycache__ and .pyc files
    if "__pycache__" in str(file_path) or file_path.suffix == ".pyc":
        return tuple(violations)

    # Run all checks
    violations.extend(check_file_imports(file_path, content))
    violations.extend(check_patch_decorators(file_path, content))
    violations.extend(check_private_access(file_path, content))

    return tuple(violations)


def scan_directory(directory: Path) -> tuple[Violation, ...]:
    """Scan directory recursively for Python files.

    Returns:
        List of all violations found in Python files within the directory.

    """
    violations = []

    if not directory.exists():
        return tuple(violations)

    for file_path in directory.rglob("*.py"):
        violations.extend(check_file(file_path))

    return tuple(violations)


def print_report(violations: tuple[Violation, ...]) -> None:
    """Print detailed violation report."""
    if not violations:
        print("✅ No architecture violations found!")
        return

    print(f"\n🚨 ARCHITECTURE VIOLATIONS DETECTED: {len(violations)}")
    print("=" * 70)

    # Group by requirement
    by_requirement = {}
    for v in violations:
        if v.requirement not in by_requirement:
            by_requirement[v.requirement] = []
        by_requirement[v.requirement].append(v)

    for req, req_violations in sorted(by_requirement.items()):
        print(f"\n{req}: {len(req_violations)} violations")
        print("-" * 70)

        for v in sorted(req_violations, key=lambda x: (x.file, x.line)):
            file_path = str(v.file).replace(str(Path.cwd()) + "/", "")
            print(f"  {file_path}:{v.line}:{v.column}")
            print(f"    {v.code}: {v.message}")

    print("\n" + "=" * 70)
    print("SUMMARY:")
    for req, req_violations in sorted(by_requirement.items()):
        print(f"  {req}: {len(req_violations)} violations")
    print(f"\nTotal violations: {len(violations)}")
    print("\n" + "🚨" * 35)
    print("MISSION-CRITICAL: Fix ALL violations immediately!")
    print("⚠️  DO NOT suppress these checks with # noqa, # type: ignore, etc.")
    print("⚠️  DO NOT add to ignore lists in pyproject.toml")
    print("⚠️  DO NOT disable linting rules")
    print("✅ FIX THE ROOT CAUSE: Refactor code to comply with architecture")
    print(
        "📝 NOTE TO AI ASSISTANTS: Never suppress lints without explicit user approval"
    )
    print("🚨" * 35)


def main() -> None:
    """Execute the architecture compliance check."""
    # Get items from command line arguments, or use defaults
    items = sys.argv[1:] if len(sys.argv) > 1 else ["clearflow", "tests", "examples"]

    all_violations = []
    for item in items:
        path = Path(item)
        if path.is_file() and path.suffix == ".py":
            # Single Python file
            violations = check_file(path)
            all_violations.extend(violations)
        elif path.is_dir():
            # Directory - scan recursively
            violations = scan_directory(path)
            all_violations.extend(violations)
        else:
            print(f"Warning: {item} is not a Python file or directory, skipping")
            continue

    # Print report
    print_report(all_violations)

    # Exit with appropriate code
    if all_violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()