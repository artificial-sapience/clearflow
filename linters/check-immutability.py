#!/usr/bin/env python
"""Check deep immutability compliance for mission-critical Python projects.

This script enforces deep immutability requirements for both ClearFlow and Sociocracy.
Zero tolerance for violations in mission-critical software.

Requirements enforced:
- All types SHALL be deeply immutable throughout the system
  - No mutable collections: list, dict, set, bytearray, collections.*
  - Use immutable alternatives: tuple, frozenset, Mapping, bytes, frozen dataclasses
  - Pydantic models must use frozen=True in ConfigDict
  - Dataclasses must use @dataclass(frozen=True)
  - No mutable default arguments
"""

import ast
import re
import sys
from pathlib import Path
from typing import NamedTuple, cast


# Auto-detect project from pyproject.toml
def detect_project() -> str:
    """Detect the project name.

    Returns:
        Project name string

    """
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding="utf-8")
        if 'name = "clearflow"' in content:
            return "clearflow"
        if 'name = "sociocracy"' in content:
            return "sociocracy"
    # Default to clearflow if can't detect
    return "clearflow"


PROJECT_NAME = detect_project()


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
        True if the line has a project-specific ignore comment for this specific code

    Format:
        # clearflow: ignore[IMM001]  - Specific code suppression for ClearFlow
        # sociocracy: ignore[IMM001]  - Specific code suppression for Sociocracy

    """
    lines = content.splitlines()
    if line_num <= 0 or line_num > len(lines):
        return False

    line = lines[line_num - 1]  # Convert to 0-indexed

    # Check for # PROJECT: ignore[CODE] pattern
    pattern = rf"#\s*{PROJECT_NAME}:\s*ignore\[{code}\]"
    return bool(re.search(pattern, line, re.IGNORECASE))


def _get_mutable_collection_info(node: ast.Subscript | ast.Name) -> tuple[str, str] | None:
    """Check if node is a mutable collection annotation and return info.

    Returns:
        Tuple of (type_name, suggestion) or None if not a mutable collection.

    """
    # Handle both Subscript (e.g., list[int]) and Name (e.g., dict) nodes
    if isinstance(node, ast.Subscript):
        if not isinstance(node.value, ast.Name):
            return None
        name = node.value.id
    else:  # node is ast.Name
        name = node.id

    # Map of mutable types to their immutable alternatives
    mutable_types = {
        "list": ("list", "tuple"),
        "List": ("List", "tuple"),
        "dict": ("dict", "Mapping or frozen dataclass"),
        "Dict": ("Dict", "Mapping or frozen dataclass"),
        "set": ("set", "frozenset"),
        "Set": ("Set", "frozenset"),
        "bytearray": ("bytearray", "bytes"),
        "deque": ("collections.deque", "tuple"),
        "defaultdict": ("collections.defaultdict", "Mapping or frozen dataclass"),
        "OrderedDict": ("collections.OrderedDict", "Mapping or frozen dataclass"),
        "Counter": ("collections.Counter", "frozen dataclass"),
        "ChainMap": ("collections.ChainMap", "Mapping or frozen dataclass"),
        "UserDict": ("collections.UserDict", "frozen dataclass"),
        "UserList": ("collections.UserList", "tuple"),
    }

    if name in mutable_types:
        return mutable_types[name]
    return None


def check_mutable_collections(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for mutable collection type annotations.

    Returns:
        List of violations for mutable collection usage in type annotations.

    """
    violations = ()

    # No exclusions - all Python code must pass immutability checks

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    for node in ast.walk(tree):
        # Check both Subscript (e.g., list[int]) and Name (e.g., dict) nodes
        if isinstance(node, (ast.Subscript, ast.Name)):
            mutable_info = _get_mutable_collection_info(node)
            if mutable_info and not has_suppression(content, node.lineno, "IMM001"):
                type_name, suggestion = mutable_info
                violations = (
                    *violations,
                    Violation(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        code="IMM001",
                        message=f"Using mutable type '{type_name}' in type annotation - use '{suggestion}' for immutability",
                        requirement="REQ-ARCH-004",
                    ),
                )

    return violations


def _is_dataclass_decorator(decorator: ast.expr) -> bool:
    """Check if decorator is @dataclass.

    Returns:
        True if decorator is a dataclass decorator, False otherwise.

    """
    if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
        return True
    if isinstance(decorator, ast.Call):
        if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
            return True
        if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "dataclass":
            return True
    return False


def _has_frozen_true(decorator: ast.expr) -> bool:
    """Check if decorator has frozen=True.

    Returns:
        True if decorator has frozen=True, False otherwise.

    """
    if not isinstance(decorator, ast.Call):
        return False
    for keyword in decorator.keywords:
        if keyword.arg == "frozen" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
            return True
    return False


def check_dataclass_frozen(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check that all dataclasses have frozen=True.

    Returns:
        List of violations for unfrozen dataclasses.

    """
    violations = ()

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if this class has @dataclass decorator
            has_dataclass = any(_is_dataclass_decorator(d) for d in node.decorator_list)
            if not has_dataclass:
                continue

            # Check if any decorator has frozen=True
            has_frozen = any(_has_frozen_true(d) for d in node.decorator_list)

            # If it's a dataclass but doesn't have frozen=True
            if not has_frozen and not has_suppression(content, node.lineno, "IMM002"):
                violations = (
                    *violations,
                    Violation(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        code="IMM002",
                        message=f"Dataclass '{node.name}' must have frozen=True",
                        requirement="REQ-ARCH-004",
                    ),
                )

    return violations


def _is_basemodel_class(base: ast.expr) -> bool:
    """Check if base class is BaseModel.

    Returns:
        True if base class is BaseModel, False otherwise.

    """
    if isinstance(base, ast.Name) and base.id == "BaseModel":
        return True
    return isinstance(base, ast.Attribute) and base.attr == "BaseModel"


def _has_model_config_target(targets: tuple[ast.expr, ...]) -> bool:
    """Check if any target is named model_config.

    Returns:
        True if model_config is targeted, False otherwise.

    """
    return any(isinstance(target, ast.Name) and target.id == "model_config" for target in targets)


def _is_config_dict_call(value: ast.expr) -> bool:
    """Check if value is a ConfigDict() call.

    Returns:
        True if value is a ConfigDict call, False otherwise.

    """
    return isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "ConfigDict"


def _has_frozen_true_keyword(keywords: tuple[ast.keyword, ...]) -> bool:
    """Check if keywords contain frozen=True.

    Returns:
        True if keywords contain frozen=True, False otherwise.

    """
    return any(
        keyword.arg == "frozen" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True
        for keyword in keywords
    )


def _is_frozen_config_assignment(item: ast.Assign) -> bool:
    """Check if assignment is model_config = ConfigDict(frozen=True).

    Returns:
        True if assignment is frozen model_config, False otherwise.

    """
    if not _has_model_config_target(tuple(item.targets)):
        return False
    if not _is_config_dict_call(item.value):
        return False
    if not isinstance(item.value, ast.Call):
        return False
    return _has_frozen_true_keyword(tuple(item.value.keywords))


def _has_frozen_config(node: ast.ClassDef) -> bool:
    """Check if class has model_config with frozen=True.

    Returns:
        True if model has frozen configuration, False otherwise.

    """
    return any(isinstance(item, ast.Assign) and _is_frozen_config_assignment(item) for item in node.body)


def _is_pydantic_model(node: ast.ClassDef, pydantic_classes: frozenset[str]) -> bool:
    """Check if class is a Pydantic model.

    Returns:
        True if class inherits from BaseModel, False otherwise.

    """
    for base in node.bases:
        if isinstance(base, ast.Name) and (base.id == "BaseModel" or base.id in pydantic_classes):
            return True
        if _is_basemodel_class(base):
            return True
    return False


def check_pydantic_frozen(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check that all Pydantic models have frozen=True in ConfigDict.

    Returns:
        List of violations for unfrozen Pydantic models.

    """
    violations = ()

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    # Track which classes inherit from BaseModel
    pydantic_class_names = ()
    classes_to_check = ()

    # Single pass: identify Pydantic models and collect them
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and _is_pydantic_model(node, frozenset(pydantic_class_names)):
            pydantic_class_names = (*pydantic_class_names, node.name)
            classes_to_check = (*classes_to_check, node)

    # Check each Pydantic model for frozen config
    return (
        *violations,
        *tuple(
            Violation(
                file=file_path,
                line=node.lineno,
                column=node.col_offset,
                code="IMM003",
                message=f"Pydantic model '{node.name}' must have frozen=True in ConfigDict",
                requirement="REQ-ARCH-004",
            )
            for node in classes_to_check
            if not _has_frozen_config(node)
        ),
    )


def _get_mutable_default_info(default: ast.expr) -> tuple[str, str] | None:
    """Get mutable type info if default is mutable, else None.

    Returns:
        Tuple of (type description, instance description) or None if not mutable.

    """
    if isinstance(default, ast.List):
        return "list", "use None or tuple"
    if isinstance(default, ast.Dict):
        return "dict", "use None or frozen dict"
    if isinstance(default, ast.Set):
        return "set", "use None or frozenset"
    return None


def check_mutable_defaults(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for mutable default arguments.

    Returns:
        List of violations for mutable defaults.

    """
    violations = ()

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return tuple(violations)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check default arguments
            for default in node.args.defaults:
                mutable_info = _get_mutable_default_info(default)
                if mutable_info:
                    mutable_type, suggestion = mutable_info
                    violations = (
                        *violations,
                        Violation(
                            file=file_path,
                            line=default.lineno,
                            column=default.col_offset,
                            code="IMM004",
                            message=f"Function '{node.name}' has mutable default argument ({mutable_type}) - {suggestion}",
                            requirement="REQ-ARCH-004",
                        ),
                    )

    return violations


def _has_temporary_markers(lines: tuple[str, ...]) -> bool:
    """Check if file has markers indicating intentional temporary list building.

    Returns:
        True if temporary markers are present, False otherwise.

    """
    for i, line in enumerate(lines):
        if "# Temporary" in line or "# temporary" in line or "# Building" in line:
            # This suggests intentional temporary list building
            for j in range(max(0, i - 2), min(len(lines), i + 3)):
                if "list[" in lines[j]:
                    return True
    return False


def _check_append_usage(node: ast.Attribute, lines: tuple[str, ...], file_path: Path) -> Violation | None:
    """Check for list.append() patterns.

    Returns:
        Violation if append usage found, None otherwise.

    """
    if node.attr == "append" and isinstance(node.value, ast.Name) and node.lineno <= len(lines):
        line = lines[node.lineno - 1]
        if "temporary" not in line.lower() and "building" not in line.lower():
            return Violation(
                file=file_path,
                line=node.lineno,
                column=node.col_offset,
                code="IMM005",
                message="Using '.append()' suggests mutable list building - use tuple comprehension instead",
                requirement="REQ-ARCH-004",
            )
    return None


def _should_skip_listcomp(node: ast.ListComp, lines: tuple[str, ...]) -> bool:
    """Check if list comprehension should be skipped.

    Returns:
        True if list comprehension should be skipped, False otherwise.

    """
    if node.lineno > len(lines):
        return False

    # Check current line and next few lines for asyncio patterns
    context_lines = lines[node.lineno - 1 : min(node.lineno + 3, len(lines))]
    context = " ".join(context_lines)

    # Skip if it's for asyncio.create_task or used with .join()
    if "asyncio.create_task" in context or ".join(" in context:
        return True

    # Skip if it's used for validation/checking (common patterns)
    skip_patterns = ["if ", "assert ", "raise ", "return len(", "!="]
    return any(word in context for word in skip_patterns)


def _collect_list_violations(
    tree: ast.Module, lines: tuple[str, ...], file_path: Path, content: str
) -> tuple[Violation, ...]:
    """Collect all list building violations from AST.

    Returns:
        Tuple of violations found.

    """
    violations = ()

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            violation = _check_append_usage(node, lines, file_path)
            if violation and not has_suppression(content, violation.line, "IMM005"):
                violations = (*violations, violation)
        elif isinstance(node, ast.ListComp) and not _should_skip_listcomp(node, lines):
            # Check for suppression comment
            if not has_suppression(content, node.lineno, "IMM006"):
                violations = (
                    *violations,
                    Violation(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        code="IMM006",
                        message="Using list comprehension - wrap in tuple() for immutability",
                        requirement="REQ-ARCH-004",
                    ),
                )

    return violations


def check_list_building(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for list building patterns that should use tuple comprehensions.

    Returns:
        List of violations for mutable list building.

    """
    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return ()

    lines = tuple(content.splitlines())

    # Check for temporary markers that allow list building
    if _has_temporary_markers(lines):
        return ()

    return _collect_list_violations(tree, lines, file_path, content)


def _check_typeddict_import(node: ast.ImportFrom, file_path: Path) -> tuple[Violation, ...]:
    """Check if node imports TypedDict.

    Returns:
        Tuple of violations for TypedDict imports.

    """
    if node.module != "typing":
        return ()

    return tuple(
        Violation(
            file=file_path,
            line=node.lineno,
            column=node.col_offset,
            code="IMM007",
            message="TypedDict imported - use frozen dataclasses for immutable state",
            requirement="REQ-ARCH-004",
        )
        for alias in node.names
        if alias.name == "TypedDict"
    )


def _is_typeddict_base(base: ast.expr) -> bool:
    """Check if a base class is TypedDict.

    Returns:
        True if base class is TypedDict, False otherwise.

    """
    if isinstance(base, ast.Name) and base.id == "TypedDict":
        return True
    return isinstance(base, ast.Subscript) and isinstance(base.value, ast.Name) and base.value.id == "TypedDict"


def _check_typeddict_inheritance(node: ast.ClassDef, file_path: Path) -> tuple[Violation, ...]:
    """Check if class inherits from TypedDict.

    Returns:
        Tuple of violations for TypedDict inheritance.

    """
    return tuple(
        Violation(
            file=file_path,
            line=node.lineno,
            column=node.col_offset,
            code="IMM007",
            message=f"Class '{node.name}' inherits from TypedDict - use @dataclass(frozen=True) instead",
            requirement="REQ-ARCH-004",
        )
        for base in node.bases
        if _is_typeddict_base(base)
    )


def check_typeddict_usage(file_path: Path, content: str) -> tuple[Violation, ...]:
    """Check for TypedDict usage that should be frozen dataclasses.

    Returns:
        List of violations for TypedDict usage.

    """
    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return ()

    violations = ()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            violations = (*violations, *_check_typeddict_import(node, file_path))
        elif isinstance(node, ast.ClassDef):
            violations = (*violations, *_check_typeddict_inheritance(node, file_path))

    return violations


def check_file(file_path: Path) -> tuple[Violation, ...]:
    """Check a single file for immutability violations.

    Returns:
        List of all immutability violations found in the file.

    """
    violations = ()

    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return tuple(violations)

    # Skip checking __pycache__ and .pyc files
    if "__pycache__" in str(file_path) or file_path.suffix == ".pyc":
        return tuple(violations)

    # Run all checks
    violations = (*violations, *check_mutable_collections(file_path, content))
    violations = (*violations, *check_dataclass_frozen(file_path, content))
    violations = (*violations, *check_pydantic_frozen(file_path, content))
    violations = (*violations, *check_mutable_defaults(file_path, content))
    violations = (*violations, *check_list_building(file_path, content))
    return (*violations, *check_typeddict_usage(file_path, content))


def scan_directory(directory: Path) -> tuple[Violation, ...]:
    """Scan directory recursively for Python files.

    Returns:
        List of all violations found in Python files within the directory.

    """
    violations = ()

    if not directory.exists():
        return tuple(violations)

    # Directories to exclude from scanning
    excluded_dirs = {".venv", "__pycache__", ".git", "node_modules", "venv", "env", ".env"}

    for file_path in directory.rglob("*.py"):
        # Skip files in excluded directories
        if any(part in excluded_dirs for part in file_path.parts):
            continue
        violations = (*violations, *check_file(file_path))

    return violations


def print_report(violations: tuple[Violation, ...]) -> None:
    """Print detailed violation report."""
    if not violations:
        print("✅ No immutability violations found!")
        return

    print(f"\n🚨 IMMUTABILITY VIOLATIONS DETECTED: {len(violations)}")
    print("=" * 70)

    # Group by code
    by_code = cast("dict[str, tuple[Violation, ...]]", {})
    for v in violations:
        if v.code not in by_code:
            by_code[v.code] = ()
        by_code[v.code] = (*by_code[v.code], v)

    code_descriptions = {
        "IMM001": "Mutable collection type annotations (list, dict, set, etc.)",
        "IMM002": "Dataclasses without frozen=True",
        "IMM003": "Pydantic models without frozen=True",
        "IMM004": "Mutable default arguments",
        "IMM005": "Mutable list building with append",
        "IMM006": "List comprehensions instead of tuples",
        "IMM007": "TypedDict usage instead of frozen dataclasses",
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
    print("Deep immutability violations detected!")
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
    items = sys.argv[1:] if len(sys.argv) > 1 else [PROJECT_NAME, "tests", "examples"]

    all_violations = ()
    for item in items:
        path = Path(item)
        if path.is_file() and path.suffix == ".py":
            # Single Python file
            violations = check_file(path)
            all_violations = (*all_violations, *violations)
        elif path.is_dir():
            # Directory - scan recursively
            violations = scan_directory(path)
            all_violations = (*all_violations, *violations)
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
