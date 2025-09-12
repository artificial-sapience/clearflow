# ClearFlow Quality Improvements Plan

## Current Sprint: Type Safety and Architecture Compliance

### 🔥 Immediate Task
**Fix AbstractMessageMeta Type Annotations** (Priority: HIGH - Architecture Violation)
- [ ] Replace `Any` types in metaclass with specific types
- [ ] Maintain functionality while satisfying architecture linter
- **Status**: Architecture linter blocking with ARCH010 violations

### 📐 Type Safety Issues  
**Resolve Pyright Type Errors** (Priority: HIGH - Type Safety)
- [ ] Fix ~35 type errors in `test_message_flow.py` (flow routing types)
- [ ] Fix ~41 type errors in `test_observer.py` (observable flow types)
- [ ] Other test files have similar routing type issues
- **Status**: Command/Event abstract classes fixed, but flow typing remains

## Recently Completed (This Session)

### ✅ PLR6301 Test Method Conversion (COMPLETED)
- Converted 48 test methods to standalone functions
- Files updated: `test_message.py` (16), `test_message_flow.py` (11), `test_message_node.py` (10), `test_observer.py` (11)
- All tests still passing (86/86)
- Removed unnecessary `async` from non-async functions

### ✅ Command/Event Abstract Classes (COMPLETED)
- Implemented custom `AbstractMessageMeta` metaclass
- Prevents direct instantiation of `Command()` and `Event()`
- Clean UX - no boilerplate methods required in subclasses
- Clear error messages guide users to create concrete types
- Resolved 9 pyright errors in `conftest_message.py`

## System Health
- **86/86 tests passing** ✅
- **98.57% coverage** (down from 100% due to new metaclass code)
- **Architecture violations**: 4 (Any type usage in metaclass)
- **Pyright errors**: ~76 remaining (mostly flow routing types)