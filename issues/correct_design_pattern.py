#!/usr/bin/env python3
"""Correct design pattern: Separate interface from data schema.

This demonstrates the proper solution to the Pydantic validation issue
by separating behavioral interfaces from data schemas.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

# Type variables for generic processing
TIn = TypeVar("TIn")
TOut = TypeVar("TOut")


# Step 1: Pure behavioral interface (no BaseModel)
class ProcessorInterface(Generic[TIn, TOut], ABC):
    """Pure behavioral interface without data validation."""

    @abstractmethod
    async def process(self, data: TIn) -> TOut:
        """Process input data."""
        ...


# Step 2: Combine interface with data schema
class BaseProcessor(BaseModel, ProcessorInterface[TIn, TOut], Generic[TIn, TOut], ABC):
    """Base processor combining data schema with behavior."""

    name: str

    class Config:
        arbitrary_types_allowed = True  # Allow interface types


# Step 3: Concrete implementation that contains abstract field
class CompositeProcessor(BaseProcessor[str, str]):
    """Processor that contains another processor - this now works!"""

    # This field uses the interface type, not the BaseModel type
    sub_processor: ProcessorInterface[str, str]

    async def process(self, data: str) -> str:
        """Process by delegating to sub-processor."""
        result = await self.sub_processor.process(data)
        return f"Composite({result})"


# Step 4: Another concrete implementation
class SimpleProcessor(BaseProcessor[str, str]):
    """Simple concrete processor."""

    prefix: str = "Simple"

    async def process(self, data: str) -> str:
        """Process with prefix."""
        return f"{self.prefix}({data})"


async def main() -> None:
    """Demonstrate that the pattern works."""
    # Create a simple processor
    simple = SimpleProcessor(name="simple")

    # Create a composite containing the simple processor
    # This works because sub_processor is typed as ProcessorInterface
    composite = CompositeProcessor(
        name="composite",
        sub_processor=simple
    )

    # Test processing
    result = await composite.process("test")
    print(f"Result: {result}")  # Output: Composite(Simple(test))

    print("✅ Success! No Pydantic validation errors.")
    print("\nKey insight: By typing the field as ProcessorInterface instead of")
    print("BaseProcessor, Pydantic doesn't try to instantiate the abstract class.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())