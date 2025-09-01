#!/usr/bin/env python3
"""Check deep immutability compliance for the ClearFlow project.

This script enforces deep immutability requirements.
Zero tolerance for violations in mission-critical software.

Requirements enforced:
- All types SHALL be deeply immutable throughout the system
  - Pydantic models must use frozen=True in ConfigDict
  - Dataclasses must use @dataclass(frozen=True)
  - Collections must use tuple instead of list
  - No mutable default arguments
"""

import ast
import re
import sys
from pathlib import Path
from typing import NamedTuple


class Violation(NamedTuple):
    """Immutability violation details."""

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
        code: The code to check for suppression (e.g., "IMM001")

    Returns:
        True if the line has a clearflow: ignore comment for this specific code

    Format:
        # clearflow: ignore[IMM001]  - Specific code suppression

    """
    lines = content.splitlines()
    if line_num <= 0 or line_num > len(lines):
        return False

    line = lines[line_num - 1]  # Convert to 0-indexed

    # Check for # clearflow: ignore[CODE] pattern
    pattern = rf"#\s*clearflow:\s*ignore\[{code}\]"
    return bool(re.search(pattern, line, re.IGNORECASE))


def check_list_annotations(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for list type annotations that should be tuple.

    Returns:
        List of violations for mutable list usage in type annotations.

    """
    violations = []
    
    # Skip this check for test files - they often need mutable collections
    # for tracking test state and assertions
    if "tests/" in str(file_path) or str(file_path).startswith("test_"):
        return tuple(violations)

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    for node in ast.walk(tree):
        # Check for list[] type annotations
        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name) and node.value.id == "list":
                # Check for suppression comment
                if not has_suppression(content, node.lineno, "IMM001"):
                    violations.append(
                        Violation(
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            code="IMM001",
                            message="Using 'list' in type annotation - use 'tuple[T, ...]' for immutable collections",
                            requirement="REQ-ARCH-004",
                        )
                    )
            # Check for List[] from typing
            elif isinstance(node.value, ast.Name) and node.value.id == "List":
                # Check for suppression comment
                if not has_suppression(content, node.lineno, "IMM001"):
                    violations.append(
                        Violation(
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            code="IMM001",
                            message="Using 'List' in type annotation - use 'tuple[T, ...]' for immutable collections",
                            requirement="REQ-ARCH-004",
                        )
                    )

    return tuple(violations)


def check_dataclass_frozen(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check that all dataclasses have frozen=True.

    Returns:
        List of violations for unfrozen dataclasses.

    """
    violations = []

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if this class has @dataclass decorator
            has_dataclass = False
            has_frozen = False

            for decorator in node.decorator_list:
                # Check for @dataclass or @dataclass(...)
                is_dataclass = False
                if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                    is_dataclass = True
                    has_dataclass = True
                elif isinstance(decorator, ast.Call):
                    if (
                        isinstance(decorator.func, ast.Name)
                        and decorator.func.id == "dataclass"
                    ):
                        is_dataclass = True
                        has_dataclass = True
                    elif isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr == "dataclass":
                            is_dataclass = True
                            has_dataclass = True

                # If it's a dataclass call with arguments, check for frozen=True
                if is_dataclass and isinstance(decorator, ast.Call):
                    for keyword in decorator.keywords:
                        if keyword.arg == "frozen":
                            if (
                                isinstance(keyword.value, ast.Constant)
                                and keyword.value.value is True
                            ):
                                has_frozen = True

            # If it's a dataclass but doesn't have frozen=True
            if has_dataclass and not has_frozen:
                # Check for suppression comment
                if not has_suppression(content, node.lineno, "IMM002"):
                    violations.append(
                        Violation(
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            code="IMM002",
                            message=f"Dataclass '{node.name}' must have frozen=True",
                            requirement="REQ-ARCH-004",
                        )
                    )

    return tuple(violations)


def check_pydantic_frozen(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check that all Pydantic models have frozen=True in ConfigDict.

    Returns:
        List of violations for unfrozen Pydantic models.

    """
    violations = []

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    # Track which classes inherit from BaseModel
    pydantic_classes = set()

    # First pass: identify Pydantic models
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if inherits from BaseModel or another Pydantic model
            for base in node.bases:
                if isinstance(base, ast.Name):
                    if base.id == "BaseModel" or base.id in pydantic_classes:
                        pydantic_classes.add(node.name)
                elif isinstance(base, ast.Attribute):
                    if base.attr == "BaseModel":
                        pydantic_classes.add(node.name)

    # Second pass: check for frozen=True in ConfigDict
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in pydantic_classes:
            has_frozen_config = False

            # Look for model_config assignment
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "model_config":
                            # Check if it's ConfigDict with frozen=True
                            if isinstance(item.value, ast.Call):
                                if (
                                    isinstance(item.value.func, ast.Name)
                                    and item.value.func.id == "ConfigDict"
                                ):
                                    for keyword in item.value.keywords:
                                        if keyword.arg == "frozen":
                                            if (
                                                isinstance(keyword.value, ast.Constant)
                                                and keyword.value.value is True
                                            ):
                                                has_frozen_config = True

            if not has_frozen_config:
                violations.append(
                    Violation(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        code="IMM003",
                        message=f"Pydantic model '{node.name}' must have frozen=True in ConfigDict",
                        requirement="REQ-ARCH-004",
                    )
                )

    return tuple(violations)


def check_mutable_defaults(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for mutable default arguments.

    Returns:
        List of violations for mutable defaults.

    """
    violations = []

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check default arguments
            for default in node.args.defaults:
                if isinstance(default, ast.List):
                    violations.append(
                        Violation(
                            file=file_path,
                            line=default.lineno,
                            column=default.col_offset,
                            code="IMM004",
                            message=f"Function '{node.name}' has mutable default argument (list) - use None or tuple",
                            requirement="REQ-ARCH-004",
                        )
                    )
                elif isinstance(default, ast.Dict):
                    violations.append(
                        Violation(
                            file=file_path,
                            line=default.lineno,
                            column=default.col_offset,
                            code="IMM004",
                            message=f"Function '{node.name}' has mutable default argument (dict) - use None or frozen dict",
                            requirement="REQ-ARCH-004",
                        )
                    )
                elif isinstance(default, ast.Set):
                    violations.append(
                        Violation(
                            file=file_path,
                            line=default.lineno,
                            column=default.col_offset,
                            code="IMM004",
                            message=f"Function '{node.name}' has mutable default argument (set) - use None or frozenset",
                            requirement="REQ-ARCH-004",
                        )
                    )

    return tuple(violations)


def check_list_building(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for list building patterns that should use tuple comprehensions.

    Returns:
        List of violations for mutable list building.

    """
    violations = []

    # Skip this check for test files and scripts (they may need list building)
    if "tests/" in str(file_path) or "linters/" in str(file_path):
        return tuple(violations)

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    lines = content.splitlines()

    # Simple heuristic: if we see "list[" followed by "tuple(" on nearby lines, it's temporary
    for i, line in enumerate(lines):
        if "# Temporary" in line or "# temporary" in line or "# Building" in line:
            # This suggests intentional temporary list building
            for j in range(max(0, i - 2), min(len(lines), i + 3)):
                if "list[" in lines[j]:
                    # Mark this as acceptable temporary list building
                    return violations  # Skip this file's list building checks

    for node in ast.walk(tree):
        # Check for list.append() patterns
        if isinstance(node, ast.Attribute):
            if node.attr == "append" and isinstance(node.value, ast.Name):
                # Check if it's marked as temporary in comments
                if node.lineno <= len(lines):
                    line = lines[node.lineno - 1]
                    if (
                        "temporary" not in line.lower()
                        and "building" not in line.lower()
                    ):
                        violations.append(
                            Violation(
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                code="IMM005",
                                message="Using '.append()' suggests mutable list building - use tuple comprehension instead",
                                requirement="REQ-ARCH-004",
                            )
                        )

        # Check for list comprehensions that aren't wrapped in tuple()
        if isinstance(node, ast.ListComp):
            # Check if it's for asyncio tasks or string joining
            if node.lineno <= len(lines):
                # Check current line and next few lines for asyncio patterns
                context_lines = lines[
                    node.lineno - 1 : min(node.lineno + 3, len(lines))
                ]
                context = " ".join(context_lines)
                # Skip if it's for asyncio.create_task or used with .join()
                if "asyncio.create_task" in context or ".join(" in context:
                    continue
                # Skip if it's used for validation/checking (common patterns)
                if any(word in context for word in ["if ", "assert ", "raise ", "return len(", "!="]):
                    continue

            violations.append(
                Violation(
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    code="IMM006",
                    message="Using list comprehension - wrap in tuple() for immutability",
                    requirement="REQ-ARCH-004",
                )
            )

    return tuple(violations)


def check_file(file_path: Path) -> tuple[Violation, ...]:
    """Check a single file for immutability violations.

    Returns:
        List of all immutability violations found in the file.

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
    violations.extend(check_list_annotations(file_path, content))
    violations.extend(check_dataclass_frozen(file_path, content))
    violations.extend(check_pydantic_frozen(file_path, content))
    violations.extend(check_mutable_defaults(file_path, content))
    violations.extend(check_list_building(file_path, content))

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
        print("✅ No immutability violations found!")
        return

    print(f"\n🚨 IMMUTABILITY VIOLATIONS DETECTED: {len(violations)}")
    print("=" * 70)

    # Group by code
    by_code = {}
    for v in violations:
        if v.code not in by_code:
            by_code[v.code] = []
        by_code[v.code].append(v)

    code_descriptions = {
        "IMM001": "Mutable list type annotations",
        "IMM002": "Dataclasses without frozen=True",
        "IMM003": "Pydantic models without frozen=True",
        "IMM004": "Mutable default arguments",
        "IMM005": "Mutable list building with append",
        "IMM006": "List comprehensions instead of tuples",
    }

    for code, code_violations in sorted(by_code.items()):
        description = code_descriptions.get(code, "Unknown violation")
        print(f"\n{code}: {description} ({len(code_violations)} violations)")
        print("-" * 70)

        for v in sorted(code_violations, key=lambda x: (x.file, x.line)):
            file_path = str(v.file).replace(str(Path.cwd()) + "/", "")
            print(f"  {file_path}:{v.line}:{v.column}")
            print(f"    {v.message}")

    print("\n" + "=" * 70)
    print("SUMMARY:")
    for code in sorted(by_code.keys()):
        description = code_descriptions.get(code, "Unknown")
        print(f"  {code} ({description}): {len(by_code[code])} violations")
    print(f"\nTotal violations: {len(violations)}")
    print("\n" + "🚨" * 35)
    print("MISSION-CRITICAL: Deep immutability violations detected!")
    print("⚠️  All types must be deeply immutable for thread safety")
    print("⚠️  DO NOT suppress these checks")
    print("✅ FIX THE ROOT CAUSE:")
    print("   - Replace list with tuple in type annotations")
    print("   - Add frozen=True to all dataclasses")
    print("   - Add frozen=True to all Pydantic ConfigDict")
    print("   - Replace mutable defaults with None or immutable types")
    print("📝 NOTE TO AI ASSISTANTS: Fix violations, don't suppress them")
    print("🚨" * 35)


def main() -> None:
    """Execute the immutability compliance check."""
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