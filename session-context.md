# Session Context

## Branch: `support-state-type-transformations`

## Major Accomplishments This Session

### 1. RAG Example Implementation ✅
**Created a complete Retrieval-Augmented Generation example** following PocketFlow's pattern:
- Implemented two-phase architecture: offline indexing + online query
- Created proper state transformations with type safety
- Used immutable dataclasses throughout
- Added FAISS type stubs (minimal, only what we use)
- Structure: `examples/rag/` with models.py, nodes.py, utils.py, rag_flow.py, main.py

**Key Design Decisions:**
- Used tuple comprehensions instead of list.append() for immutability
- Fixed docstrings to document returns and raises
- Changed exception handling to avoid broad Exception catches

### 2. Type Stubs Investigation 🔍
**Discovered that most libraries have built-in types:**
- **NumPy 2.3.2**: Has built-in type annotations and `numpy.typing` module
- **OpenAI 1.106.1**: Includes `py.typed` marker with full type support
- **python-dotenv 1.1.1**: Also has `py.typed` marker
- **faiss-cpu**: Only one without types - we created minimal stubs

**Lesson**: Modern Python packages (2024-2025) mostly include type annotations directly.

### 3. Dependency Organization Overhaul 🏗️
**Switched from requirements.txt to pyproject.toml for each example:**

**Strategy Decision**: Option A - Modern approach
- Each example gets its own pyproject.toml
- Root pyproject.toml adds `[project.optional-dependencies.examples]`
- quality-check.sh uses `uv sync --extra examples`
- Removed all requirements.txt files

**Build System Consistency**: 
- Switched all examples from setuptools to **hatchling** (matching root)
- Hatchling is the 2025 best practice: lightweight, fast, minimal config

### 4. Dependency Conflict Discovery 🚨
**Critical Issue Found:**
- `dspy>=3.0.0` requires `rich>=13.7.1`
- `semgrep>=1.134.0` requires `rich>=13.5.2,<13.6.dev0`
- These are incompatible!

**Next Session Priority**: Update ALL dependencies to latest stable versions

## Current State

### Files Modified/Created:
- ✅ Created complete RAG example in `examples/rag/`
- ✅ Created pyproject.toml for all examples (chat, portfolio_analysis, rag)
- ✅ Added `examples` extra to root pyproject.toml
- ✅ Updated quality-check.sh to use `uv sync --extra examples`
- ✅ Removed all requirements.txt files
- ✅ Created FAISS type stubs in `typings/faiss/`
- ✅ Updated main README (removed "coming soon" from RAG)

### Known Issues:
- ❌ Dependency conflict between dspy and semgrep (rich version)
- ❌ Some pyright errors in RAG example (mostly import resolution)
- ❌ Need to verify all deps are latest 2025 versions

## Key Technical Decisions

1. **Use pyproject.toml everywhere** - It's 2025, this is the standard
2. **Hatchling for all** - Consistent, modern build backend
3. **Type stubs only when needed** - Most modern packages include types
4. **Immutability everywhere** - Even in examples, use tuple comprehensions
5. **Examples as semi-independent packages** - Each has its own pyproject.toml

## What's Next

See `plan.md` for prioritized task list. Critical items:
1. Fix dependency conflicts (rich version incompatibility)
2. Update all dependencies to latest stable versions
3. Complete RAG example quality checks
4. Prepare and submit PR