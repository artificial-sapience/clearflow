# Is This Really a Pydantic Bug?

## The Deeper Question

After extensive investigation, we need to ask: **Is this actually a bug in Pydantic, or is it a design pattern issue?**

## Pydantic's Perspective

Pydantic's primary job is data validation. When it encounters a field, it needs to:
1. Validate the type
2. Potentially reconstruct/coerce the value
3. Ensure the data meets all constraints

When Pydantic sees a field typed as an abstract class, it reasonably tries to validate that the value is an instance of that class. During this validation, it may attempt to reconstruct the object, which fails for abstract classes.

## The Design Pattern Problem

The real issue is that we're mixing two different concerns:

1. **Data Validation** (Pydantic's domain)
2. **Behavioral Contracts** (ABC's domain)

When we have:
```python
class Node(BaseModel, ABC):  # Mixing data + behavior
    name: str
    @abstractmethod
    async def process(...): ...

class Flow(Node):  # Inherits from Node
    starting_node: Node[...]  # Field of same abstract type - PROBLEMATIC!
```

We're asking Pydantic to validate a behavioral contract, which isn't really its job.

## The Correct Pattern

The solution is to separate these concerns:

```python
class _NodeInterface(ABC):  # Pure behavior
    @abstractmethod
    async def process(...): ...

class Node(BaseModel, _NodeInterface, ABC):  # Implements interface
    name: str  # Data schema

class Flow(Node):
    starting_node: _NodeInterface[...]  # Field uses interface, not BaseModel
```

## Why This Isn't a Bug

1. **Expected Behavior**: Pydantic is doing what it's designed to do - validate data
2. **Design Issue**: The problem is in our design pattern, not Pydantic's implementation
3. **Clear Solution**: Separating interfaces from schemas is a well-established pattern
4. **Documentation**: This pattern aligns with best practices for mixing validation and abstraction

## Conclusion

This is a **design pattern issue**, not a Pydantic bug. The framework is working as intended - we just need to use the correct architectural pattern for our use case.