#!/usr/bin/env python3
"""Reproduction of the Pydantic validation issue with abstract BaseModel.

This script demonstrates the issue where Pydantic fails to handle
a class that inherits from an abstract BaseModel and contains a field
of the same abstract type.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

# Type variables for generic processing
TIn = TypeVar("TIn")
TOut = TypeVar("TOut")


class AbstractProcessor(BaseModel, Generic[TIn, TOut], ABC):
    """Abstract base processor that combines BaseModel with ABC."""

    name: str

    @abstractmethod
    async def process(self, data: TIn) -> TOut:
        """Process input data."""
        ...


class ConcreteProcessor(AbstractProcessor[str, str]):
    """Concrete implementation."""

    prefix: str = "Processed"

    async def process(self, data: str) -> str:
        """Process with prefix."""
        return f"{self.prefix}: {data}"


class CompositeProcessor(AbstractProcessor[str, str]):
    """Processor that contains another processor - this fails!"""

    # This field has the same abstract type as the parent class
    sub_processor: AbstractProcessor[str, str]

    async def process(self, data: str) -> str:
        """Process by delegating to sub-processor."""
        result = await self.sub_processor.process(data)
        return f"Composite({result})"


def main() -> None:
    """Demonstrate the Pydantic validation issue."""
    print("Creating a concrete processor...")
    concrete = ConcreteProcessor(name="concrete")
    print(f"✅ Concrete processor created: {concrete.name}")

    print("\nCreating a composite processor with abstract field...")
    try:
        # This fails because Pydantic tries to instantiate AbstractProcessor
        composite = CompositeProcessor(
            name="composite",
            sub_processor=concrete
        )
        print(f"✅ Composite processor created: {composite.name}")
    except Exception as e:
        print(f"❌ Failed to create composite processor!")
        print(f"Error: {e}")
        print("\nThis happens because Pydantic's validation tries to")
        print("instantiate the abstract class during field validation.")


if __name__ == "__main__":
    main()