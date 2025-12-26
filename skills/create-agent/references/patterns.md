# Agent System Prompt Patterns

## Core Structure

```markdown
You are [role] specializing in [domain].

**Responsibilities:**
[What the agent does]

**Process:**
[How the agent works]

**Output Format:**
[What to return]
```

## Role Patterns

| Pattern | Template |
|---------|----------|
| Expert | `You are a [domain] expert with deep knowledge of [areas].` |
| Specialist | `You are a specialist focused on [task].` |
| Executor | `You are an automation specialist that executes [process].` |

## Responsibility Patterns

**Enumerated:**
```markdown
**Responsibilities:**
1. Primary task
2. Secondary task
3. Supporting task
```

**Scoped:**
```markdown
**In Scope:** Task A, Task B
**Out of Scope:** Not X, Not Y
```

## Process Patterns

| Type | Structure |
|------|-----------|
| Linear | Gather → Analyze → Execute → Validate → Report |
| Iterative | Assess → Loop(Apply, Verify, Adjust) → Validate |
| Conditional | Analyze → If A: do X, If B: do Y → Finish |

## Output Patterns

**Report:** Summary, Findings, Recommendations, Next steps

**Per-Item:** Name, Status, Details, Action needed

**Diff:** Before, After, Reason

## Description Examples

```yaml
# Simple
description: Use this agent when the user needs [capability].

# With examples (recommended)
description: Use this agent for [task].

<example>
user: "User request"
assistant: "Response using agent."
<commentary>Why appropriate.</commentary>
</example>
```

## Color Guide

| Color | Use For |
|-------|---------|
| `blue` | Analysis, review |
| `cyan` | Documentation, exploration |
| `green` | Creation, testing |
| `yellow` | Refactoring, validation |
| `red` | Security, debugging |
