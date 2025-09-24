# Reinforcement in Stigmergic Systems

## Overview

Reinforcement is the mechanism by which multi-agent systems manage scarce attention, accumulate evidence, and signal ownership without central coordination. It transforms individual observations into collective intelligence.

## Core Concept

In stigmergic systems, signals have **emergent strength** that changes over time based on:
- Initial emission strength (set once by emitter)
- Environmental decay (time-based fading)
- Collective reinforcement (positive or negative)

The emitter only controls the initial strength. After emission, the signal's fate is determined by environmental dynamics and collective agent behavior.

## Mathematical Model

Signal strength at time `t`:

```
S(t) = S₀ · D(t-t₀) + Σ[g(aᵢ, wᵢ, rᵢ) · D(t-tᵢ)]
```

Where:
- `S₀`: Initial strength when emitted
- `D(Δt)`: Decay function (e.g., `2^(-Δt/half_life)`)
- `aᵢ`: Reinforcement amount at event i
- `wᵢ`: Agent credibility weight [0,1]
- `rᵢ`: Reason for reinforcement
- `g()`: Combination function based on reason type

### Invariants
- If no reinforcements in interval (t₁,t₂], then S(t₂) ≤ S(t₁)
- S(t) ≥ 0 for all t
- S(t) ≤ S_cap if saturation is enabled

## Why Reinforce?

### 1. Attention Allocation
- Finite agent attention requires prioritization
- Strong signals attract more agents
- Weak signals fade from awareness

### 2. Evidence Accumulation
- Independent confirmations strengthen hypotheses
- Contradictory evidence weakens claims
- Truth emerges from collective assessment

### 3. Work Ownership
- Agents reinforce signals they're working on
- Prevents duplicate effort
- Shows liveness without direct communication

### 4. Priority Emergence
- Urgent items accumulate reinforcement
- Priority emerges from collective judgment
- No central scheduler needed

### 5. Active Forgetting
- Unused information naturally fades
- Relevant knowledge persists through reinforcement
- System automatically garbage-collects stale signals

## Types of Reinforcement

### Positive Reinforcement

| Reason | Math | Use Case |
|--------|------|----------|
| **EVIDENCE** | Log-odds update | New supporting data |
| **CONFIRMATION** | Additive with saturation | Independent verification |
| **OWNERSHIP** | Constant maintenance | Active work indicator |
| **URGENCY** | Additive with cap | Time-sensitive priority |

### Negative Reinforcement (Inhibition)

| Reason | Math | Use Case |
|--------|------|----------|
| **OBJECTION** | Subtractive | Consensus blocking |
| **CONTRADICTION** | Accelerated decay | Conflicting evidence |
| **DUPLICATE** | Strength transfer | Merge redundant signals |
| **OBSOLETE** | Immediate decay | Mark as outdated |

## Implementation Design

### Reinforcement Event Structure

```python
@dataclass(frozen=True)
class Reinforcement:
    signal_id: str           # Which signal to reinforce
    amount: float           # Magnitude (can be negative)
    by: str                 # Agent ID
    reason: ReinforcementReason
    weight: float = 1.0     # Agent credibility [0,1]
    note: str = ""          # Explanation/provenance
    at: datetime            # When reinforced (UTC)
```

### Reason Taxonomy

```python
class ReinforcementReason(Enum):
    # Positive reinforcement
    EVIDENCE = auto()       # New supporting data
    CONFIRMATION = auto()   # Independent verification
    OWNERSHIP = auto()      # Taking responsibility
    URGENCY = auto()        # Time-sensitive
    AGREEMENT = auto()      # Consensus building

    # Negative reinforcement
    OBJECTION = auto()      # Disagreement
    CONTRADICTION = auto()  # Conflicting evidence
    DUPLICATE = auto()      # Redundant signal
    OBSOLETE = auto()       # No longer relevant
```

### Combination Rules

Different reasons use different mathematical updates:

```python
def apply_reinforcement(signal: Signal, reinforcement: Reinforcement) -> float:
    """Calculate strength contribution based on reason."""

    base_amount = reinforcement.amount * reinforcement.weight

    if reinforcement.reason == ReinforcementReason.EVIDENCE:
        # Log-odds for truth accumulation
        return log_odds_update(signal.belief, base_amount)

    elif reinforcement.reason == ReinforcementReason.OWNERSHIP:
        # Constant maintenance to show active work
        return max(base_amount, signal.strength * 0.9)

    elif reinforcement.reason in [ReinforcementReason.OBJECTION,
                                  ReinforcementReason.CONTRADICTION]:
        # Inhibitory - reduces strength
        return -base_amount

    else:
        # Default: additive with optional saturation
        return min(base_amount, signal.cap - signal.strength)
```

## Domain-Specific Patterns

### Sociocratic Decision Making

```python
# Proposal accumulates consent
space.reinforce(proposal.id, amount=1.0,
                reason=AGREEMENT, by=agent.id)

# Objections block with explanation
space.reinforce(proposal.id, amount=-2.0,
                reason=OBJECTION, by=agent.id,
                note="Violates budget constraint")

# Decision when: S_consent ≥ threshold AND S_objection < block_threshold
```

### Portfolio Analysis

```python
# Evidence weighted by source independence
correlation = compute_source_correlation(new_data, existing_evidence)
weight = 1.0 - correlation  # Discount correlated sources

space.reinforce(market_signal.id,
                amount=confidence_delta,
                reason=EVIDENCE,
                weight=weight,
                note=f"Source: {data_source}")
```

### Collaborative Coding

```python
# Claim ownership of task
space.reinforce(task.id, amount=5.0,
                reason=OWNERSHIP, by=developer.id)

# CI results affect signal strength
if ci_passed:
    space.reinforce(pr.id, amount=1.0, reason=CONFIRMATION)
else:
    space.reinforce(pr.id, amount=-2.0, reason=OBJECTION,
                   note=f"Tests failed: {test_results}")
```

### Goal-Seeking Systems

```python
# Success propagates to causal chain
if goal.completed:
    for signal in causal_chain:
        distance = compute_causal_distance(signal, goal)
        amount = success_value * (discount_factor ** distance)
        space.reinforce(signal.id, amount=amount,
                       reason=EVIDENCE, note="Led to success")
```

## Safety & Governance

### Prevent Gaming

1. **Budget Constraints**: Agents have finite reinforcement per period
   ```python
   if agent.reinforcement_used_today >= agent.daily_budget:
       raise BudgetExceeded()
   ```

2. **Rate Limiting**: Cooldowns prevent spam
   ```python
   last_reinforcement = get_last(agent.id, signal.id)
   if (now - last_reinforcement.at) < cooldown_period:
       raise RateLimitExceeded()
   ```

3. **Reputation Weighting**: Trust affects influence
   ```python
   weight = compute_reputation(agent.id, domain)
   effective_amount = amount * weight
   ```

### Ensure Quality

1. **Required Provenance**: Evidence needs sources
   ```python
   if reason == EVIDENCE and not reinforcement.note:
       raise ProvenanceRequired()
   ```

2. **Diversity Requirements**: Prevent echo chambers
   ```python
   endorsers = get_reinforcing_agents(signal.id)
   if not has_role_diversity(endorsers):
       weight *= diversity_penalty
   ```

3. **Idempotency**: Prevent duplicate reinforcements
   ```python
   hash_key = hash((agent.id, signal.id, reason, floor(at.timestamp())))
   if hash_key in processed_reinforcements:
       return  # Already processed
   ```

## Key Design Principles

### 1. Emergent, Not Prescribed
Current strength emerges from collective behavior, not emitter control.

### 2. Bidirectional Influence
Support both amplification and inhibition for complete expressiveness.

### 3. Typed and Semantic
Different reasons trigger different mathematical updates.

### 4. Bounded and Safe
Caps, budgets, and rate limits prevent runaway dynamics.

### 5. Forgetful by Design
Without maintenance, everything fades - this enables adaptation.

## Example: Complete System

```python
class StigmergicSignalSpace:
    """Signal space with full reinforcement mechanics."""

    def __init__(self):
        self.signals: Dict[str, Signal] = {}
        self.reinforcements: List[Reinforcement] = []
        self.agent_budgets: Dict[str, float] = {}

    def emit(self, signal: Signal) -> None:
        """Add new signal to space."""
        self.signals[signal.id] = signal

    def reinforce(self,
                  signal_id: str,
                  amount: float,
                  by: str,
                  reason: ReinforcementReason,
                  weight: float = 1.0,
                  note: str = "") -> None:
        """Apply reinforcement with all safety checks."""

        # Check budget
        if not self._check_budget(by, amount):
            raise BudgetExceeded(f"Agent {by} exceeded reinforcement budget")

        # Check rate limit
        if not self._check_rate_limit(by, signal_id):
            raise RateLimitExceeded(f"Agent {by} reinforcing too frequently")

        # Apply reinforcement
        reinforcement = Reinforcement(
            signal_id=signal_id,
            amount=amount,
            by=by,
            reason=reason,
            weight=weight,
            note=note,
            at=datetime.utcnow()
        )

        self.reinforcements.append(reinforcement)
        self._update_budget(by, amount)

    def get_current_strength(self, signal_id: str, now: datetime) -> float:
        """Calculate emergent strength at time t."""
        signal = self.signals.get(signal_id)
        if not signal:
            return 0.0

        # Initial strength with decay
        age = (now - signal.timestamp).total_seconds()
        strength = signal.initialStrength * signal.decay_factor(age)

        # Apply all reinforcements
        for r in self.reinforcements:
            if r.signal_id == signal_id and r.at <= now:
                r_age = (now - r.at).total_seconds()
                r_contribution = self._compute_contribution(r, r_age)

                if r.reason in [ReinforcementReason.OBJECTION,
                               ReinforcementReason.CONTRADICTION]:
                    strength -= r_contribution
                else:
                    strength += r_contribution

        # Apply cap if configured
        if hasattr(signal, 'cap') and signal.cap:
            strength = min(strength, signal.cap)

        return max(0.0, strength)  # Ensure non-negative
```

## Conclusion

Reinforcement transforms stigmergic systems from simple message spaces into adaptive, intelligent environments. Through typed, weighted, and bounded reinforcement events, independent agents create collective intelligence where:

- Important signals persist through collective maintenance
- Truth emerges from accumulated evidence
- Consensus forms through endorsement and objection
- Work coordination happens without central control
- The system naturally forgets what no longer matters

This is not about "likes" or popularity - it's about creating a substrate for genuine collective intelligence.