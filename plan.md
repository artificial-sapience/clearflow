# Stigmergic Coordination Lean4 Specification Plan

## Current Focus: Formal Specification of Stigmergic MVP

### Immediate Tasks (In Progress)

1. **Fix Primitives.lean compilation** 🔄
   - Fix remaining upstreamableDecl linter issue for Metadata structure
   - Update all Metadata operations to use new structure format
   - Ensure compilation with zero linter suppressions (except minImports)

2. **Create Trace.lean specification** 📝
   - Define Trace structure with content, type, timestamp, creator, metadata
   - Add proper documentation following Lean4 standards
   - Include bijective correspondence for all operations
   - Add theorems for trace properties (persistence, immutability)

3. **Create Environment.lean** 📝
   - Define Environment as collection of traces
   - Implement deposit operation
   - Implement search/query operations
   - Add decay mechanics

4. **Create Agent.lean** 📝
   - Define Agent interface
   - Implement attraction calculation
   - Implement decide_action logic
   - Add agent state management

### Architecture Structure
```
Stigmergic/
├── Foundation/
│   ├── Primitives.lean    ✅ (needs linter fixes)
│   └── Trace.lean         📝 (next)
├── Core/
│   ├── Environment.lean   📝
│   ├── Agent.lean         📝
│   └── Attraction.lean    📝
└── Properties/
    ├── TraceProperties.lean
    └── Safety.lean
```

### Key Technical Decisions
- Using `abbrev Time := NNReal` for continuous mathematical time
- Strict adherence to Lean4 spec standards (no linter suppressions except minImports)
- Using latest Lean 4.23.0 and mathlib v4.23.0
- Following layered architecture from reference project
- All public declarations must have documentation
- All theorems must have proofs (no sorry)

### Documentation Requirements Per Module
- Module documentation with Overview, Main Definitions, Implementation Notes
- Every definition needs PURPOSE, PRECONDITIONS, POSTCONDITIONS, INVARIANTS
- Bijective correspondence between math and English
- No copyright/license headers (removed per standards)

## Completed Tasks ✅

- Lean4 specification standard cleanup (removed all "flourishing" references)
- Removed historical references from spec documents
- Set up Lean4 environment with latest versions (4.23.0)
- Created lakefile.lean with strict linting configuration
- Created Stigmergic.lean root module
- Started Primitives.lean with proper documentation