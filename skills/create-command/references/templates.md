# Command Templates

## Simple Commands

```markdown
Review this code for potential issues.
```

```markdown
---
description: Fix GitHub issue
argument-hint: [issue-number]
---
Fix issue #$ARGUMENTS following project conventions.
```

## File Operations

```markdown
---
description: Review specific file
argument-hint: [file-path]
---
Review @$1 for code quality, bugs, and best practices.
```

## Git Workflow

```markdown
---
description: Create conventional commit
allowed-tools: Bash(git:*)
---
Changes: !`git diff --cached --stat`
Create a conventional commit for these staged changes.
```

```markdown
---
description: Review PR changes
allowed-tools: Read, Bash(git:*)
---
Branch: !`git branch --show-current`
Changes: !`git diff main...HEAD --stat`
Review all changes for quality, tests, and breaking changes.
```

## With Tool Restrictions

```markdown
---
description: Security review
argument-hint: [file-path]
allowed-tools: Read, Grep
---
Review @$1 for SQL injection, XSS, auth issues, and input validation.
```

```markdown
---
description: Fix linting issues
argument-hint: [file-path]
allowed-tools: Read, Write, Bash(npm:*)
---
Lint output: !`npm run lint -- $1 2>&1 || true`
Fix all linting issues in @$1.
```
