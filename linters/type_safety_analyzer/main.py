#!/usr/bin/env python
"""Type safety analyzer using DSPy for comprehensive code analysis."""

import argparse
import asyncio
import os
import uuid
from pathlib import Path

import dspy
from dotenv import load_dotenv

from linters.type_safety_analyzer.flow import create_simple_analyzer_flow
from linters.type_safety_analyzer.messages import StartAnalysisCommand


def setup_llm(model: str = "gpt-5-mini-2025-08-07", *, enable_cache: bool = False) -> dspy.LM:
    """Configure DSPy with specified model.

    Args:
        model: Model name to use.
        enable_cache: Whether to enable DSPy caching.

    Returns:
        Configured DSPy LM instance.

    Raises:
        ValueError: If API key is not found in environment.

    """
    # Try multiple .env locations
    env_locations = [Path(".env"), Path("../.env"), Path("../../.env")]
    for env_path in env_locations:
        if env_path.exists():
            load_dotenv(env_path)
            break

    if model.startswith("gemini"):
        # Gemini setup
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            msg = "GOOGLE_API_KEY not found in environment"
            raise ValueError(msg)
        lm = dspy.LM(model=f"google/{model}", api_key=api_key, temperature=0.7)
    else:
        # OpenAI setup (default)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            msg = "OPENAI_API_KEY not found in environment"
            raise ValueError(msg)
        lm = dspy.LM(model=f"openai/{model}", api_key=api_key, temperature=1.0, max_tokens=16000)

    # Set cache control directly on LM instance
    lm.cache = enable_cache
    return lm


async def analyze_file(file_path: str, *, model: str = "gpt-5-mini-2025-08-07", enable_cache: bool = False) -> None:
    """Analyze a Python file for type safety issues."""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return

    # Minimal setup - observer handles all output
    lm = setup_llm(model, enable_cache=enable_cache)
    dspy.configure(lm=lm)

    flow = create_simple_analyzer_flow()

    code = path.read_text(encoding="utf-8")
    command = StartAnalysisCommand(
        file_path=str(path.absolute()),
        code_content=code,
        run_id=uuid.uuid4(),
    )

    await flow.process(command)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Type safety analyzer")
    parser.add_argument("file", help="Python file to analyze")
    parser.add_argument("--model", default="gpt-5-mini-2025-08-07", help="LLM model to use")
    parser.add_argument(
        "--cache", action="store_true", help="Enable DSPy caching (disabled by default for development)"
    )

    args = parser.parse_args()

    asyncio.run(analyze_file(args.file, model=args.model, enable_cache=args.cache))


if __name__ == "__main__":
    main()
