# Update Project Memory

Please review our collaboration session and update @CLAUDE.md with any important learnings, patterns, or knowledge that should be preserved across sessions.

## Instructions

1. **Review what we accomplished** in this session
2. **Identify key learnings** that would help in future sessions
3. **Update CLAUDE.md** with:
   - Technical discoveries or gotchas
   - Workflow patterns that worked well
   - Common issues and their solutions
   - Documentation principles we established
   - Any project-specific knowledge gained

## Guidelines for updates

- **Be concise** - Only add what's truly valuable for future sessions
- **Be specific** - Include concrete examples, commands, or code patterns
- **Avoid repetition** - Don't duplicate existing content
- **Stay factual** - No opinions or philosophy, just technical facts
- **Keep it proportional** - CLAUDE.md should stay under 300 lines

## Areas to consider

- [ ] **Technical patterns**: New code patterns or architectural decisions
- [ ] **Workflow improvements**: Git, PR, or release process refinements  
- [ ] **Documentation style**: Any new style rules or examples discovered
- [ ] **Common pitfalls**: Issues we encountered and how to avoid them
- [ ] **Tool usage**: Specific commands or tool configurations that work well
- [ ] **Project conventions**: Naming, structure, or organization patterns

## Example additions

```markdown
## Session: [Date]

**Discovered**: Release workflow fails if draft release ID becomes stale
**Solution**: Always fetch draft by tag name, not cached ID

**Pattern**: When simplifying docs, remove "we/our" language
**Example**: "We provide X" → "ClearFlow provides X" → "X"
```

After updating, commit with:

```bash
git commit -m "docs: update CLAUDE.md with session learnings"
```
