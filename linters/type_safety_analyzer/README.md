# Type Safety Analyzer - LLM-Powered Code Analysis

An LLM-powered analyzer that detects magic strings and type safety issues that standard linters miss. Built with ClearFlow's message-driven architecture.

## Architecture

This analyzer demonstrates how ClearFlow can be used to orchestrate LLM-powered code analysis tasks. It follows the same patterns as the portfolio analysis example but applies them to static analysis.

### Flow Structure

```text
StartAnalysisCommand
    ↓
CodeParserNode → CodeParsedEvent
    ↓
IssueDetectorNode → IssuesIdentifiedEvent
    ↓
FixGeneratorNode → FixesGeneratedEvent
    ↓
FixApplierNode → AnalysisCompleteEvent
```

### Key Components

1. **Messages** (`messages.py`): Define the command and event types that flow through the system
   - `StartAnalysisCommand`: Initiates analysis with code and context
   - `CodeParsedEvent`: Contains extracted string literals
   - `IssuesIdentifiedEvent`: Lists detected type safety issues
   - `FixesGeneratedEvent`: Contains generated code fixes
   - `AnalysisCompleteEvent`: Terminal event with results

2. **DSPy Signatures** (`signatures.py`): Define LLM interfaces for analysis
   - `MagicStringDetectionSignature`: Identifies type safety issues
   - `CodeFixGenerationSignature`: Generates fixes for issues
   - `PatternLearningSignature`: Learns project-specific patterns

3. **Nodes** (`nodes.py`): Implement analysis stages
   - `CodeParserNode`: AST-based parsing (no LLM needed)
   - `IssueDetectorNode`: LLM-powered issue detection
   - `FixGeneratorNode`: LLM-powered fix generation
   - `FixApplierNode`: Applies fixes to files

4. **Flow** (`flow.py`): Orchestrates the analysis pipeline

## Installation

```bash
# Ensure you're in the ClearFlow project root
cd /path/to/clearflow

# Install dependencies with uv
uv sync --all-extras
```

## Usage

### From Project Root

```bash
# Analyze a file (default: OpenAI GPT-5 Nano)
uv run python -m linters.type_safety_analyzer.main path/to/file.py

# From within the analyzer directory
cd linters/type_safety_analyzer
uv run python -m main stress_test_cases.py

# Apply fixes to the file
uv run python -m main file.py --apply

# Use a different model
uv run python -m main file.py --model gemini-2.5-pro
```

### Available Models

- `gpt-5-mini-2025-08-07` (default) - Fast, good accuracy
- `gemini-2.5-pro` - Higher accuracy, slower
- `gemini-2.5-flash` - Baseline comparison

### Programmatic Usage

```python
import asyncio
from linters.type_safety_analyzer import (
    create_type_safety_flow,
    StartAnalysisCommand,
)

async def analyze():
    # Create the flow
    flow = create_type_safety_flow(apply_fixes=False)

    # Create analysis command
    command = StartAnalysisCommand(
        file_path="myfile.py",
        code_content=open("myfile.py").read(),
        available_literals={"NodeName": ["A", "B", "C"]},
    )

    # Run analysis
    result = await flow.run(command)
    print(result.summary)

asyncio.run(analyze())
```

## Environment Setup

Required environment variables:

```bash
# Create .env file in project root
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key  # Optional
```

## How It Works

1. **Code Parsing**: AST-based extraction of all string literals from Python code
2. **LLM Analysis**: Identifies magic strings that should be Literal types
3. **Fix Generation**: Creates type-safe replacements using Literal types
4. **Application**: Optionally applies fixes to the source file

## Advantages Over Rule-Based Linters

1. **Semantic Understanding**: The LLM understands the meaning and intent of code, not just patterns
2. **Project-Specific Learning**: Can learn and adapt to project conventions
3. **Intelligent Suggestions**: Provides context-aware fixes, not just error flags
4. **Evolution**: Improves as LLMs improve, without code changes
5. **Natural Language Explanations**: Can explain WHY something is an issue

## Example Output

```bash
$ cd linters/type_safety_analyzer
$ uv run python -m main stress_test_cases.py

======================================================================
🔍 Type Safety Analysis Started
======================================================================
📁 File: stress_test_cases.py
📏 Code size: 20931 bytes

📝 Parsing Python code...
✓ Found 454 string literals to analyze

🤖 Analyzing for type safety issues...
⚠️  Found 21 type safety issues:
  🟡 21 warnings

Line 28: Magic string used for status comparison
  Code: if status == "pending":
  Fix: Use Literal["pending", "approved", "rejected"]

Line 83: HTTP methods should use Literal type
  Code: if method not in {"GET", "POST", "PUT", "DELETE"}:
  Fix: Define HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]

✅ Analysis Complete
   Issues found: 21
   Fixes available: 21
```

## Configuration

The analyzer can be configured through:

- **Available Literals**: Pass known Literal types for the project
- **Project Context**: Provide domain-specific conventions
- **LLM Model**: Choose the model based on accuracy/cost trade-offs

## Testing

The `stress_test_cases.py` file contains comprehensive test patterns:

- Simple magic strings (`"pending"`, `"approved"`)
- HTTP methods and status codes
- Environment modes (`"production"`, `"staging"`)
- Complex nested patterns
- All pass static analysis but require AI-powered analysis to detect

```bash
# Test the analyzer on the stress test file
cd linters/type_safety_analyzer
uv run python -m main stress_test_cases.py
```

## Key Features

- **Zero false positives**: Only detects actual type safety issues
- **Context-aware**: Understands code semantics, not just patterns
- **Actionable fixes**: Provides concrete code replacements
- **Project-aware**: Can use existing Literal types from your codebase
