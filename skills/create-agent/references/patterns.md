# Agent System Prompt Patterns

Design patterns for effective agent system prompts.

## Core Structure

Every agent prompt should include:

```markdown
You are [role] specializing in [domain].

**Responsibilities:**
[What the agent does]

**Process:**
[How the agent works]

**Output Format:**
[What to return]
```

## Role Definition Patterns

### Domain Expert
```markdown
You are a [domain] expert with deep knowledge of [specific areas].

Your expertise includes:
- Area 1
- Area 2
- Area 3
```

### Task Specialist
```markdown
You are a specialist focused on [specific task].

You excel at:
- Skill 1
- Skill 2
- Skill 3
```

### Process Executor
```markdown
You are an automation specialist that executes [process name].

Your workflow:
1. Step one
2. Step two
3. Step three
```

## Responsibility Patterns

### Enumerated List
```markdown
**Responsibilities:**
1. Primary responsibility
2. Secondary responsibility
3. Supporting responsibility
```

### Categorized
```markdown
**Core Duties:**
- Main task
- Secondary task

**Supporting Duties:**
- Support task
- Quality task
```

### Scoped
```markdown
**In Scope:**
- Task A
- Task B

**Out of Scope:**
- Not task X
- Not task Y
```

## Process Patterns

### Linear Process
```markdown
**Process:**
1. Gather inputs
2. Analyze
3. Execute
4. Validate
5. Report
```

### Iterative Process
```markdown
**Process:**
1. Initial assessment
2. Iterate:
   a. Apply change
   b. Verify
   c. Adjust if needed
3. Final validation
```

### Conditional Process
```markdown
**Process:**
1. Analyze the situation
2. If [condition A]:
   - Do X
   - Then Y
3. If [condition B]:
   - Do Z instead
4. Always finish with validation
```

## Output Format Patterns

### Structured Report
```markdown
**Output Format:**
Provide a report with:
- Summary (1-2 sentences)
- Findings (bulleted list)
- Recommendations (prioritized)
- Next steps (if applicable)
```

### Per-Item Format
```markdown
**Output:**
For each [item]:
- Name/identifier
- Status/assessment
- Details
- Action needed
```

### Diff/Change Format
```markdown
**Output:**
Show changes as:
- Before: [original]
- After: [modified]
- Reason: [why changed]
```

## Quality Guidelines Patterns

### Standards List
```markdown
**Quality Standards:**
- Be specific, not vague
- Include code examples
- Explain the reasoning
- Prioritize by importance
```

### Do/Don't
```markdown
**Guidelines:**
Do:
- Use clear language
- Provide examples
- Stay focused

Don't:
- Be vague
- Skip validation
- Overreach scope
```

## Context Awareness Patterns

### Tool Context
```markdown
You have access to: Read, Grep, Glob

Use these to:
- Read: Examine file contents
- Grep: Search for patterns
- Glob: Find files by name
```

### Project Context
```markdown
Adapt to the project:
- Follow existing code style
- Match documentation patterns
- Use project conventions
```

## Advanced Patterns

### Multi-Phase Agent
```markdown
**Phase 1: Discovery**
- Gather information
- Identify scope

**Phase 2: Analysis**
- Evaluate findings
- Categorize issues

**Phase 3: Action**
- Apply solutions
- Verify results
```

### Escalation Pattern
```markdown
**Decision Points:**
- If straightforward: proceed autonomously
- If uncertain: list options and ask
- If critical/irreversible: always confirm
```

### Collaboration Pattern
```markdown
**Handoff:**
When complete, summarize:
- What was done
- What remains
- Recommendations for next steps
```

## Description Example Patterns

### Simple Trigger
```yaml
description: Use this agent when the user needs [capability].
```

### Multiple Triggers
```yaml
description: Use this agent when the user needs [A], wants [B], or asks about [C].
```

### With Examples
```yaml
description: Use this agent when analyzing code quality. Examples:

<example>
user: "Review my code"
assistant: "I'll use the reviewer agent."
<commentary>Direct review request.</commentary>
</example>

<example>
user: "Is this implementation good?"
assistant: "Let me launch the reviewer agent to evaluate."
<commentary>Implicit review request.</commentary>
</example>
```

## Color Selection Guide

| Color | Meaning | Use For |
|-------|---------|---------|
| `blue` | Information, analysis | Code review, exploration |
| `cyan` | Documentation, neutral | Docs, info gathering |
| `green` | Success, creation | Test gen, building |
| `yellow` | Caution, validation | Refactoring, migration |
| `magenta` | Creative, generation | Content, design |
| `red` | Critical, security | Security, debugging |
