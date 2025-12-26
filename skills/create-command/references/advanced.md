# Advanced Command Patterns

## Dynamic Context with Bash

### Include Git State
```markdown
---
allowed-tools: Bash(git:*)
---

Branch: !`git branch --show-current`
Status: !`git status --short`
Recent: !`git log --oneline -5`

Based on this git state, suggest next actions.
```

### Environment Info
```markdown
---
allowed-tools: Bash(*)
---

Node: !`node --version`
NPM: !`npm --version`
PWD: !`pwd`

Check environment compatibility.
```

### Conditional Execution
```markdown
---
allowed-tools: Bash(*)
---

Package manager: !`test -f yarn.lock && echo "yarn" || echo "npm"`

Use the detected package manager for all commands.
```

## File Reference Patterns

### Multiple Static Files
```markdown
Compare configurations:
- Package: @package.json
- TypeScript: @tsconfig.json
- ESLint: @.eslintrc.js

Check for inconsistencies.
```

### Dynamic File Reference
```markdown
---
argument-hint: [directory]
---

Review all TypeScript files in @$1/:
- Architecture patterns
- Code consistency
- Potential improvements
```

### Glob-Style Context
```markdown
---
allowed-tools: Glob, Read
---

Find and review all test files matching **/\*.test.ts
```

## Argument Patterns

### Optional Arguments
```markdown
---
argument-hint: [file] [--verbose]
---

Review @$1 for issues.
$ARGUMENTS contains: check if --verbose present for detailed output.
```

### Named Arguments
```markdown
---
argument-hint: --env=VALUE --version=VALUE
---

Parse arguments from: $ARGUMENTS
Extract --env and --version values for deployment.
```

### Variadic Arguments
```markdown
---
argument-hint: [files...]
---

Review all specified files: $ARGUMENTS
Process each file mentioned.
```

## Tool Restrictions

### Read-Only Analysis
```markdown
---
allowed-tools: Read, Grep, Glob
---

Analyze without making changes.
```

### Git Operations Only
```markdown
---
allowed-tools: Bash(git:*)
---

Only git commands allowed.
```

### Specific Commands
```markdown
---
allowed-tools: Bash(npm:test, npm:lint, npm:build)
---

Only these npm scripts allowed.
```

### Multiple Tool Patterns
```markdown
---
allowed-tools: Read, Write, Edit, Bash(git:*, npm:test)
---

File operations plus specific bash commands.
```

## Subdirectory Organization

```
.claude/commands/
├── git/
│   ├── commit.md      # /commit
│   ├── pr.md          # /pr
│   └── rebase.md      # /rebase
├── test/
│   ├── unit.md        # /unit
│   ├── e2e.md         # /e2e
│   └── coverage.md    # /coverage
└── docs/
    ├── api.md         # /api
    └── readme.md      # /readme
```

Commands namespaced by directory in `/help` output.

## Error Handling

### Graceful Bash Failures
```markdown
---
allowed-tools: Bash(*)
---

Result: !`command-that-might-fail 2>&1 || echo "FAILED"`

Handle the result appropriately.
```

### Validation Pattern
```markdown
---
argument-hint: [required-arg]
---

Validate: $1 must be provided.
If missing, explain usage: /command [required-arg]
Otherwise proceed with task.
```

## Integration Patterns

### With Agents
```markdown
---
description: Deep review using agent
argument-hint: [file]
---

Launch the code-reviewer agent to analyze @$1 thoroughly.
```

### With Skills
```markdown
---
description: Apply domain knowledge
---

Use the relevant domain skill to process this request with specialized knowledge.
```

### Chained Commands
```markdown
---
description: Full workflow
allowed-tools: Bash(npm:*, git:*)
---

1. Run tests: !`npm test 2>&1 | tail -10`
2. If passing, run build: !`npm run build 2>&1 | tail -5`
3. Stage and prepare commit

Execute full pre-commit workflow.
```

## Best Practices

### Keep Commands Focused
- One command = one task
- Use agents for complex multi-step work
- Chain simple commands for workflows

### Document Arguments
- Always use `argument-hint`
- Validate required arguments
- Provide usage examples in comments

### Restrict Tools Appropriately
- Principle of least privilege
- Only grant needed access
- Use patterns like `Bash(git:*)` not `Bash(*)`

### Handle Errors Gracefully
- Use `|| true` or `|| echo "error"` in bash
- Provide helpful messages for failures
- Validate inputs before processing
