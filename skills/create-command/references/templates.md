# Command Templates

Ready-to-use templates for common command patterns.

## Simple Commands

### Basic Review
```markdown
Review this code for potential issues, bugs, and improvements.
```

### Explain Code
```markdown
Explain this code in simple terms, focusing on the main logic and purpose.
```

### Summarize
```markdown
Summarize the recent changes and their purpose.
```

## Commands with Arguments

### Fix Issue
```markdown
---
description: Fix GitHub issue
argument-hint: [issue-number]
---

Fix issue #$ARGUMENTS following project conventions and best practices.
```

### Review File
```markdown
---
description: Review specific file
argument-hint: [file-path]
---

Review @$1 for:
1. Code quality
2. Potential bugs
3. Best practices
4. Test coverage
```

### Deploy
```markdown
---
description: Deploy to environment
argument-hint: [environment] [version]
---

Deploy version $2 to $1 environment following deployment checklist.
```

## Git Workflow Commands

### Commit
```markdown
---
description: Create conventional commit
allowed-tools: Bash(git:*)
---

Changes: !`git diff --cached --stat`

Create a conventional commit message for these staged changes.
Format: type(scope): description
```

### PR Review
```markdown
---
description: Review current PR changes
allowed-tools: Read, Bash(git:*)
---

Branch: !`git branch --show-current`
Changes: !`git diff main...HEAD --stat`

Review all changes in this branch for:
1. Code quality
2. Test coverage
3. Documentation
4. Breaking changes
```

### Changelog
```markdown
---
description: Generate changelog from commits
allowed-tools: Bash(git:*)
---

Recent commits: !`git log --oneline -20`

Generate a changelog entry from these commits, grouping by type.
```

## Code Quality Commands

### Lint Fix
```markdown
---
description: Fix linting issues
argument-hint: [file-path]
allowed-tools: Read, Write, Bash(npm:*)
---

Lint output: !`npm run lint -- $1 2>&1 || true`

Fix all linting issues in @$1.
```

### Type Check
```markdown
---
description: Fix TypeScript errors
allowed-tools: Read, Write, Bash(npx:*)
---

Errors: !`npx tsc --noEmit 2>&1 || true`

Fix all TypeScript errors reported above.
```

### Security Scan
```markdown
---
description: Security review
argument-hint: [file-path]
allowed-tools: Read, Grep
---

Review @$1 for security vulnerabilities:
- SQL injection
- XSS attacks
- Authentication issues
- Sensitive data exposure
- Input validation
```

## Documentation Commands

### Generate Docs
```markdown
---
description: Generate documentation for file
argument-hint: [source-file]
---

Generate comprehensive documentation for @$1:
- Module/class overview
- Function descriptions
- Parameter documentation
- Return values
- Usage examples
```

### Update README
```markdown
---
description: Update README with recent changes
allowed-tools: Read, Write
---

Current README: @README.md

Update the README to reflect current project state, ensuring:
- Accurate installation instructions
- Updated usage examples
- Current API documentation
```

## Testing Commands

### Write Tests
```markdown
---
description: Write tests for file
argument-hint: [source-file]
allowed-tools: Read, Write
---

Write comprehensive tests for @$1:
- Unit tests for all functions
- Edge cases
- Error handling
- Mocking where appropriate
```

### Test Coverage
```markdown
---
description: Improve test coverage
argument-hint: [file-path]
allowed-tools: Read, Write, Bash(npm:*)
---

Coverage: !`npm run test:coverage -- --collectCoverageFrom='$1' 2>&1 | tail -20`

Add tests to improve coverage for @$1.
```

## Multi-File Commands

### Compare Files
```markdown
---
description: Compare two files
argument-hint: [file1] [file2]
---

Compare @$1 with @$2:
- Key differences
- Breaking changes
- Improvements
- Recommendations
```

### Refactor
```markdown
---
description: Refactor with pattern
argument-hint: [file] [pattern]
---

Refactor @$1 applying the "$2" pattern:
- Identify applicable locations
- Apply consistently
- Verify no breaking changes
```
