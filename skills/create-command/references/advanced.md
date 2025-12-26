# Advanced Command Patterns

## Dynamic Context

```markdown
---
allowed-tools: Bash(git:*)
---
Branch: !`git branch --show-current`
Status: !`git status --short`
[Your instructions using this context]
```

## Argument Patterns

| Pattern | Syntax | Example |
|---------|--------|---------|
| All args | `$ARGUMENTS` | `Fix #$ARGUMENTS` |
| Positional | `$1`, `$2` | `Deploy $1 to $2` |
| Optional | Check in prompt | `$ARGUMENTS contains: check for --verbose` |

## Tool Restriction Patterns

| Pattern | Effect |
|---------|--------|
| `Read, Grep, Glob` | Read-only analysis |
| `Bash(git:*)` | Git commands only |
| `Bash(npm:test, npm:lint)` | Specific npm scripts |
| `Read, Write, Bash(git:*)` | Files + git |

## Subdirectory Organization

```
.claude/commands/
├── git/commit.md      # /commit
├── git/pr.md          # /pr
└── test/unit.md       # /unit
```

## Error Handling

```markdown
---
allowed-tools: Bash(*)
---
Result: !`command 2>&1 || echo "FAILED"`
Handle the result appropriately.
```

## Best Practices

- One command = one task
- Always use `argument-hint` for args
- Use `|| true` in bash for graceful failures
- Restrict tools to minimum needed
