# Analysis Checklist

Detailed evaluation criteria for all Claude Code extension types.

## Token Efficiency Checks

### Prose to Table Candidates
Score each skill 0-3 (0=none, 3=many opportunities)

Look for:
- Step-by-step instructions in paragraph form
- Feature comparisons described narratively
- Lists embedded in sentences
- Reference data explained verbosely

**Example transformation**:
```markdown
# Before (45 tokens)
You should use Web Search for current information,
Read for file content, and Bash for
any shell operations.

# After (25 tokens)
| Tool | Use For |
|------|---------|
| Web Search | Current information |
| Read | File content |
| Bash | Shell operations |
```

### Repeated Patterns
Check for content duplicated across skills:

- [ ] Context initialization steps (~150 tokens if duplicated)
- [ ] Search strategies (~200 tokens)
- [ ] Common wrap-up sections (~100 tokens)
- [ ] Tool usage instructions
- [ ] User context gathering

**Action**: Extract to shared reference if found in 2+ skills.

### Verbose Examples
Examples should demonstrate, not explain:

- [ ] Example responses over 200 tokens - trim to essential
- [ ] Example with commentary - remove meta-explanation
- [ ] Multiple examples showing same pattern - keep one
- [ ] Obvious examples - remove entirely

### Redundant Sections
Look for:
- [ ] Information repeated in different words
- [ ] SKILL.md duplicating references/ content
- [ ] Same instruction in multiple workflow steps
- [ ] "Always/Never" lists repeating earlier content

## Structure Checks

### Size Guidelines

| Metric | Red Flag | Target | Green |
|--------|----------|--------|-------|
| SKILL.md lines | >400 | 150-250 | <150 |
| SKILL.md tokens | >3000 | 800-1500 | <800 |
| References total | >5000 | 1000-3000 | varies |

### Progressive Disclosure

Check separation of concerns:

| Belongs in SKILL.md | Belongs in references/ |
|---------------------|----------------------|
| Core workflow (high-level) | Detailed patterns |
| Quick reference tables | Exhaustive lists |
| When to use each tool | API documentation |
| Key principles | Advanced techniques |

**Red flags**:
- [ ] API details in SKILL.md
- [ ] No references/ when SKILL.md >300 lines
- [ ] references/ duplicating SKILL.md content

### Section Hierarchy

Good structure:
```
# Skill Name          (H1 - one only)
## Major Section      (H2 - workflow phases)
### Subsection        (H3 - specific topics)
```

**Red flags**:
- [ ] Multiple H1 headings
- [ ] Jumping from H1 to H3
- [ ] Inconsistent heading levels
- [ ] Sections without clear purpose

## Currency Checks

### API Versions
For technical skills, verify:

- [ ] Framework versions (Qt, KDE, etc.)
- [ ] API endpoint URLs
- [ ] Method signatures
- [ ] Configuration schemas
- [ ] External service integrations

**Action**: Web search `[technology] documentation [year]` to find current versions.

### Documentation Links
Check all URLs:

- [ ] Links resolve (not 404)
- [ ] Content is current (not deprecated docs)
- [ ] Official sources preferred
- [ ] Version-specific links when appropriate

### Best Practices

Web search for:
- `[technology] best practices [year]`
- `[technology] anti-patterns`
- `[technology] migration guide` (if version changed)

## Agent-Specific Checks

### Frontmatter Validation

| Field | Check |
|-------|-------|
| `name` | Matches filename (without .md) |
| `description` | Clear triggering conditions, includes examples |
| `model` | Appropriate for task complexity |
| `color` | Optional, for visual distinction |

### Description Quality

The description field is critical for agent triggering. Check:

- [ ] Clear "when to use" conditions
- [ ] 2-4 triggering examples with context
- [ ] Examples show user message AND assistant response
- [ ] Commentary explains why agent is appropriate
- [ ] No overlapping triggers with other agents

**Red flags**:
- [ ] Vague descriptions ("use for complex tasks")
- [ ] Missing examples
- [ ] Examples without commentary
- [ ] Overlaps with existing agents

### System Prompt Structure

Good agent structure:
```
# Role/Identity statement
## Core Responsibilities (numbered)
## Operational Guidelines
## Output Format
## Edge Cases (if needed)
## Quality Assurance
```

**Size guidelines**:

| Metric | Red Flag | Target | Green |
|--------|----------|--------|-------|
| Total lines | >200 | 80-150 | <80 |
| Total tokens | >3000 | 1000-2000 | <1000 |

### Tool Access Review

- [ ] Listed tools match actual needs
- [ ] No overly broad access ("All tools") when specific tools suffice
- [ ] Missing tools that would be needed
- [ ] Tool access matches task complexity

### Model Selection

| Model | Use When |
|-------|----------|
| haiku | Fast, simple tasks; high-volume operations |
| sonnet | Balanced complexity; most agents |
| opus | Complex reasoning; nuanced decisions |

Check:
- [ ] Model matches task complexity
- [ ] Consider cost vs. quality tradeoff
- [ ] Haiku for collector/scraping tasks
- [ ] Sonnet/Opus for domain expertise

## Command-Specific Checks

### Structure Validation

| Field | Check |
|-------|-------|
| Description line | Present, concise (1 line) |
| Placeholder `{}` | Used for input if text-transform command |
| Instructions | Clear, numbered steps if multi-step |
| Output directive | Explicit (e.g., "Return only the...") |

### Command Types

| Type | Characteristics | Example |
|------|-----------------|---------|
| Text Transform | `{}` placeholder, single output | eli5, summarize |
| Action | Multi-step, no placeholder | commit, review-pr |

**Red flags**:
- [ ] Missing description line
- [ ] Verbose instructions (>10 lines)
- [ ] Unclear output format
- [ ] Mixed concerns (transform + action)

### Size Guidelines

| Metric | Red Flag | Target | Green |
|--------|----------|--------|-------|
| Lines | >20 | 5-15 | <10 |
| Tokens | >200 | 50-150 | <100 |

---

## Hook-Specific Checks

### Event Type Validation

| Event | Valid Matchers |
|-------|----------------|
| Notification | `permission_prompt`, `idle_prompt` |
| Stop | (none required) |
| PreToolUse | Tool patterns |
| PostToolUse | Tool patterns |
| SessionStart | (none required) |

### Hook Configuration

- [ ] Event type is valid
- [ ] Matcher pattern is correct (if required)
- [ ] Command is safe (no destructive operations)
- [ ] Timeout is reasonable (1-30 seconds)
- [ ] Hook type is `command` (currently only supported type)

**Red flags**:
- [ ] Missing timeout
- [ ] Destructive commands (rm, etc.)
- [ ] Invalid event type
- [ ] Overly complex command chains

---

## Plugin-Specific Checks

### plugin.json Validation

| Field | Required | Check |
|-------|----------|-------|
| `name` | Yes | Unique, descriptive |
| `version` | Yes | Semver format |
| `description` | Yes | Clear purpose |
| `author` | No | Attribution |
| `dependencies` | No | Valid references |

### Bundled Extensions

- [ ] Commands in `commands/` are valid
- [ ] Skills in `skills/` have SKILL.md
- [ ] Agents in `agents/` have frontmatter
- [ ] Hooks in `hooks/hooks.json` are valid
- [ ] MCP config in `.mcp.json` is valid (if present)

### Coherence Check

- [ ] All bundled extensions relate to plugin purpose
- [ ] No conflicting extensions
- [ ] Shared patterns extracted (if duplicated)
- [ ] README.md documents usage

---

## CLAUDE.md Specific Checks

### Structure

| Section | Purpose |
|---------|---------|
| Project Overview | Brief description |
| Coding Standards | Style rules |
| Architecture | Key patterns |
| Commands/Tools | Available scripts |

### Content Quality

- [ ] No stale rules (outdated framework versions)
- [ ] Rules match actual project structure
- [ ] No contradictory instructions
- [ ] Concise (<500 lines for most projects)
- [ ] No duplicated system-level info

**Red flags**:
- [ ] Deprecated framework references
- [ ] Rules that conflict with codebase
- [ ] Verbose explanations (should be terse)
- [ ] Personal notes mixed with project rules

### Scope Appropriateness

| Scope | Should Contain |
|-------|----------------|
| Global (`~/.claude/`) | User preferences, cross-project patterns |
| Project root | Project-specific rules, architecture |
| Nested (src/) | Subsystem-specific rules only |

---

## Scoring Summary

For each extension, produce:

```markdown
## [Extension Type]: [Name] Analysis

| Category | Score | Notes |
|----------|-------|-------|
| Token Efficiency | X/10 | [key findings] |
| Structure | X/10 | [key findings] |
| Currency | X/10 | [key findings] |
| Type-Specific | X/10 | [relevant checks] |

**Priority**: [HIGH/MEDIUM/LOW]
**Estimated Token Savings**: ~XXX (-XX%)
**Changes Proposed**: X
```
