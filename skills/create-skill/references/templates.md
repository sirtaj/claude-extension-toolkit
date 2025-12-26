# Skill Templates

## Minimal

```markdown
---
name: my-skill
description: This skill should be used when the user asks to "do X" or needs help with Y.
---

# My Skill

## Purpose
Brief description.

## Workflow
1. Step one
2. Step two
```

## Domain Expert

```markdown
---
name: domain-expert
description: This skill should be used when the user asks about "topic A", needs help with B, or wants guidance on C.
---

# Domain Expert

## Expertise Areas
- **Area 1**: Description
- **Area 2**: Description

## Common Workflows

### Task Name
1. Step one
2. Step two

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Problem 1 | Fix 1 |

## Additional Resources
- `references/patterns.md` - Detailed patterns
```

## Tool Integration

```markdown
---
name: tool-integration
description: This skill should be used when the user asks to "use X tool" or needs help with Y API.
allowed-tools: Bash, Read, Write
---

# Tool Integration

## Setup
Prerequisites and configuration.

## Core Operations

### Operation 1
\`\`\`bash
tool-command --option value
\`\`\`

## Error Handling
| Error | Solution |
|-------|----------|
| Error 1 | Fix |

## References
- `references/api.md` - Full API docs
```
