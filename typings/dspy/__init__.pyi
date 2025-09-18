"""Minimal DSPy type stubs for ClearFlow examples.

This file contains ONLY the DSPy APIs we actually use.

APIs stubbed (based on actual usage):
- dspy.LM: Language model configuration
- dspy.configure: Global DSPy configuration
- dspy.Signature: Base class for prompt signatures
- dspy.InputField: Input field descriptor
- dspy.OutputField: Output field descriptor
- dspy.Predict: Prediction module
- dspy.ChainOfThought: Chain of thought reasoning module

If you need additional DSPy functionality:
1. Add it to the examples
2. Add the type stub here
3. Document what it's used for

This keeps our stubs maintainable and accurate.
"""
from typing import Any, Optional

from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass

# Language Model Configuration
class LM:
    """Language model interface for DSPy."""
    cache: bool  # Controls DSPy caching behavior

    def __init__(
        self,
        model: str,
        *,
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...

# Global Configuration
def configure(
    *,
    lm: Optional[LM] = None,
    **kwargs: Any
) -> None:
    """Configure global DSPy settings."""
    ...

# Field Descriptors
def InputField(
    *,
    desc: str = "",
    prefix: str = "",
    format: Any = None,
    **kwargs: Any
) -> Any:  # Returns Any to work with metaclass transformation
    """Define an input field in a DSPy signature."""
    ...

def OutputField(
    *,
    desc: str = "",
    prefix: str = "",
    format: Any = None,
    **kwargs: Any
) -> Any:  # Returns Any to work with metaclass transformation
    """Define an output field in a DSPy signature."""
    ...

# Signature Base Class
class SignatureMeta(ModelMetaclass):
    """Metaclass for DSPy signatures."""
    ...

class Signature(BaseModel, metaclass=SignatureMeta):
    """Base class for DSPy prompt signatures.
    
    Inherits from Pydantic BaseModel and uses metaclass
    transformation to convert field descriptors into typed attributes.
    """
    __doc__: str

# Prediction Modules
class Predict:
    """DSPy prediction module for executing signatures."""

    def __init__(
        self,
        signature: type[Signature] | str,
        **kwargs: Any
    ) -> None: ...

    def __call__(self, **kwargs: Any) -> Any:
        """Execute the prediction with given inputs."""
        ...

    def forward(self, **kwargs: Any) -> Any:
        """Forward pass through the prediction module."""
        ...

class ChainOfThought(Predict):
    """DSPy chain of thought module for step-by-step reasoning.

    Extends Predict to add reasoning field before output fields,
    enabling step-by-step thinking for better quality outputs.
    """

    def __init__(
        self,
        signature: type[Signature] | str,
        **kwargs: Any
    ) -> None: ...