import Lake
open Lake DSL

package stigmergic where
  buildType := .debug

-- Mathlib dependency for Real numbers and mathematical foundations
require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.23.0"

@[default_target]
lean_lib Stigmergic where
  -- Strict options for compile-time discipline
  leanOptions := #[
    -- Implicit/binder discipline
    ⟨`autoImplicit, false⟩,              -- No automatic implicit arguments
    ⟨`relaxedAutoImplicit, false⟩,       -- No relaxed implicit patterns

    -- Documentation discipline
    ⟨`linter.all, true⟩,                 -- Enable all linters
    ⟨`linter.missingDocs, true⟩,         -- Require documentation for all declarations

    -- Other useful linters
    ⟨`linter.unusedVariables, true⟩,     -- Catch unused variables
    ⟨`linter.deprecated, true⟩,          -- Warn on deprecated features


    -- Pretty-printing
    ⟨`pp.unicode.fun, true⟩,             -- Use ↦ instead of =>
    ⟨`pp.proofs.withType, false⟩         -- Don't show types in proof terms
  ]

  -- Command-line arguments
  moreLeanArgs := #[
    "-DwarningAsError=true",              -- Make every warning fatal
    "-DmaxHeartbeats=200000"             -- Guard against runaway proofs
  ]
