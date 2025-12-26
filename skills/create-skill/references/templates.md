# Skill Templates

## Minimal Skill

```markdown
---
name: simple-skill
description: This skill should be used when the user asks to "do X" or needs help with Y.
---

# Simple Skill

## Purpose
Brief description of what this skill provides.

## Workflow
1. Gather requirements
2. Execute task
3. Validate result
```

## Domain Expert Skill

```markdown
---
name: domain-expert
description: This skill should be used when the user asks about "topic A", "how to do B", or needs expertise in C domain.
---

# Domain Expert

## Expertise Areas
- **Area 1**: Description
- **Area 2**: Description
- **Area 3**: Description

## Common Workflows

### Workflow 1: Task Name
1. Step one
2. Step two
3. Step three

### Workflow 2: Another Task
1. First action
2. Second action

## Best Practices
- Practice 1
- Practice 2
- Practice 3

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Problem 1 | Fix 1 |
| Problem 2 | Fix 2 |

## Additional Resources
- `references/patterns.md` - Detailed patterns
- `references/api.md` - API reference
```

## Tool Integration Skill

```markdown
---
name: tool-integration
description: This skill should be used when the user asks to "use X tool", "integrate with Y", or needs help with Z API.
allowed-tools: Bash, Read, Write
---

# Tool Integration

## Overview
Integration with [Tool Name] for [purpose].

## Setup
Prerequisites and configuration steps.

## Core Operations

### Operation 1
```bash
# Command example
tool-command --option value
```

### Operation 2
```bash
# Another command
tool-command other-action
```

## Scripts
- `scripts/setup.sh` - Initial setup
- `scripts/validate.sh` - Validation utility

## Error Handling
| Error | Cause | Solution |
|-------|-------|----------|
| Error 1 | Cause | Fix |

## References
- `references/api-docs.md` - Full API documentation
- Official docs: [URL]
```

## Workflow Skill

```markdown
---
name: workflow-skill
description: This skill should be used when the user asks to "run workflow X", "automate Y process", or needs help with Z pipeline.
---

# Workflow: Name

## Overview
This workflow automates [process] for [purpose].

## Prerequisites
- Requirement 1
- Requirement 2

## Workflow Steps

### Phase 1: Preparation
1. Gather inputs
2. Validate requirements
3. Set up environment

### Phase 2: Execution
1. Execute main task
2. Handle errors
3. Log progress

### Phase 3: Completion
1. Validate outputs
2. Clean up
3. Report results

## Configuration
```yaml
# config.yaml template
setting1: value
setting2: value
```

## Troubleshooting
Common issues and solutions.

## References
- `references/detailed-steps.md` - Step-by-step guide
- `examples/sample-config.yaml` - Example configuration
```

## Code Pattern Skill

```markdown
---
name: code-patterns
description: This skill should be used when the user asks about "X pattern", "how to implement Y", or needs code examples for Z.
---

# Code Patterns: Domain

## Pattern Overview
Common patterns for [domain/technology].

## Patterns

### Pattern 1: Name
**Use when**: Situation description

```typescript
// Example implementation
function pattern1() {
  // Implementation
}
```

**Benefits**: Why use this pattern

### Pattern 2: Name
**Use when**: Situation description

```typescript
// Example implementation
function pattern2() {
  // Implementation
}
```

## Anti-Patterns
Things to avoid:
- Anti-pattern 1: Why it's bad
- Anti-pattern 2: Why it's bad

## References
- `references/examples.md` - More examples
- `references/advanced.md` - Advanced patterns
```

## Personal Advisor Skill

```markdown
---
name: advisor-name
description: This skill should be used when the user asks about "topic X", needs advice on Y, or wants guidance for Z decisions.
---

# Advisor: Name

## Expertise
Domain expertise and advisory focus.

## Advisory Approach
How advice is structured and delivered.

## Common Topics

### Topic 1
Guidance and recommendations.

### Topic 2
Guidance and recommendations.

## Decision Framework
How to approach decisions in this domain.

## Resources
- `references/guidelines.md` - Detailed guidelines
- `references/examples.md` - Case studies
```
