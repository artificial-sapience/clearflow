import Stigmergic.Core.Agent
import Stigmergic.Core.AgentDecisions
import Stigmergic.Core.SignalSpace
import Stigmergic.Core.SignalSpaceDecisions
import Stigmergic.Foundation.Primitives
import Stigmergic.Foundation.PrimitivesDecisions
import Stigmergic.Foundation.Signal
import Stigmergic.Foundation.SignalDecisions
import Stigmergic.Meta.Decision
import Stigmergic.Properties.Safety
import Stigmergic.Properties.Emergence

set_option linter.minImports false -- This is a top-level import file

/-!
# Stigmergic Coordination System

Root module for the formal specification of stigmergic coordination.

## Overview

This system provides a mathematically rigorous specification for
coordination through environmental signals, implementing the theoretical
framework described in stigmergic-coordination-theory.md.

## Module Structure

- `Stigmergic.Foundation` - Basic types (signals, time, identifiers)
- `Stigmergic.Core` - Agent and space mechanics
- `Stigmergic.Properties` - Safety theorems and emergence properties
- `Stigmergic.Meta` - Normative decision tracking

-/
