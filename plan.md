# Stigmergic Coordination Lean4 Specification Plan

## Next Session Tasks

1. **Create Properties Module** 📝
   - Create Properties/Safety.lean with safety theorems
   - Create Properties/Emergence.lean with emergence properties
   - Focus on essential stigmergic properties only

2. **Documentation & Cleanup** 📖
   - Review and update all normative decision files
   - Add README.md explaining the specification structure
   - Document the strength vs relevance design

3. **Integration Testing** 🔧
   - Create example usage scenarios
   - Verify the API is usable for LLM agent implementations

## Architecture Structure (Current)
```
Stigmergic/
├── Meta/
│   ├── Decision.lean                ✅ Complete
├── Foundation/
│   ├── Primitives.lean              ✅ Complete
│   ├── PrimitivesDecisions.lean     ✅ Complete
│   ├── Signal.lean                  ✅ Complete (with strength field)
│   └── SignalDecisions.lean         ✅ Complete
├── Core/
│   ├── SignalSpace.lean            ✅ Complete (using grind)
│   ├── SignalSpaceDecisions.lean   ✅ Complete
│   ├── Agent.lean                  ✅ Complete (simplified Relevance)
│   └── AgentDecisions.lean         ✅ Complete
└── Properties/
    ├── Safety.lean                  📝 TODO
    └── Emergence.lean               📝 TODO
```

## Key Design Decisions
- **Strength**: Intrinsic signal property (0-1) set by emitter
- **Relevance**: Agent's contextual interpretation = strength × semantic_match
- **Simplified types**: Using plain NNReal for Relevance to avoid proof complexity
- **Focused proofs**: Only prove essential stigmergic properties, not design choices