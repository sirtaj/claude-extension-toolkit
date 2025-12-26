# Rules Templates

Ready-to-use templates for CLAUDE.md, settings, and hooks.

## CLAUDE.md Templates

### TypeScript Project

```markdown
# Project Name

## Tech Stack
- TypeScript 5.x
- Node.js 20+
- PostgreSQL 15

## Coding Standards
- Use strict TypeScript (`strict: true`)
- Prefer `const` over `let`
- Use async/await over callbacks
- Document public APIs with JSDoc

## Project Structure
- `src/` - Source code
- `src/types/` - Type definitions
- `tests/` - Test files (Jest)
- `docs/` - Documentation

## Commands
- `npm run build` - Compile TypeScript
- `npm test` - Run tests
- `npm run lint` - ESLint check

## Notes
- Environment variables in `.env.local`
- Database migrations in `prisma/migrations/`
```

### Python Project

```markdown
# Project Name

## Tech Stack
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL

## Coding Standards
- Type hints required
- Black for formatting
- Ruff for linting
- Docstrings for public functions

## Project Structure
- `src/` - Source code
- `src/models/` - SQLAlchemy models
- `src/api/` - FastAPI routes
- `tests/` - Pytest tests

## Commands
- `uv run pytest` - Run tests
- `uv run ruff check .` - Lint
- `uv run black .` - Format

## Notes
- Use `uv` for dependency management
- Alembic for migrations
```

### React Project

```markdown
# Project Name

## Tech Stack
- React 18
- TypeScript
- Vite
- TailwindCSS

## Coding Standards
- Functional components only
- Custom hooks for shared logic
- CSS-in-JS via Tailwind classes
- React Query for data fetching

## Project Structure
- `src/components/` - React components
- `src/hooks/` - Custom hooks
- `src/pages/` - Page components
- `src/api/` - API clients
- `src/types/` - TypeScript types

## Commands
- `npm run dev` - Development server
- `npm run build` - Production build
- `npm test` - Vitest tests

## Notes
- State management: Zustand
- Forms: React Hook Form
- Routing: React Router v6
```

### Minimal Project

```markdown
# Project

## Standards
- Language: [language]
- Style: [formatter/linter]
- Tests: [framework]

## Structure
- `src/` - Source
- `tests/` - Tests

## Commands
- Build: [command]
- Test: [command]
```

## Settings Templates

### Development Settings

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Edit",
      "Bash(npm:*)",
      "Bash(git:*)",
      "Bash(node:*)"
    ]
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "cat .claude/context.md 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Restricted Settings

```json
{
  "permissions": {
    "allow": ["Read", "Grep", "Glob"],
    "deny": ["Write", "Edit", "Bash"]
  }
}
```

### Full Access with Safety

```json
{
  "permissions": {
    "allow": ["*"],
    "deny": [
      "Bash(rm:-rf*)",
      "Bash(sudo:*)",
      "Bash(chmod:777*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check for credentials, API keys, passwords. Deny if found."
          }
        ]
      }
    ]
  }
}
```

## Hook Templates

### Security Hooks

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'echo \"$TOOL_INPUT\" | grep -qE \"rm -rf|sudo|chmod 777|curl.*\\|.*sh\" && echo deny || echo approve'"
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Scan for secrets: API keys, passwords, tokens, private keys. Return 'deny' with reason if found, 'approve' if clean."
          }
        ]
      }
    ]
  }
}
```

### Quality Hooks

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the session: 1) Were tests run for code changes? 2) Was lint/format checked? Return 'block' with missing steps or 'approve'."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(echo '$TOOL_INPUT' | jq -r '.file_path'); [[ \"$FILE\" == *.ts ]] && npx prettier --write \"$FILE\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Context Hooks

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "echo '## Current State'; git status --short 2>/dev/null; echo '## Recent Activity'; git log --oneline -5 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Notification Hooks

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo '$TOOL_INPUT' | grep -q 'git push' && notify-send 'Claude' 'Code pushed to remote' || true"
          }
        ]
      }
    ]
  }
}
```

## Combined Configuration

### Full Development Setup

**.claude/settings.json:**
```json
{
  "permissions": {
    "allow": ["Read", "Write", "Edit", "Bash(npm:*)", "Bash(git:*)", "Bash(node:*)"]
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {"type": "command", "command": "cat .claude/context.md 2>/dev/null || true"}
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check for hardcoded secrets. Deny if found."
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Verify tests ran for code changes. Block with reason if not."
          }
        ]
      }
    ]
  }
}
```

**.claude/CLAUDE.md:**
```markdown
# Project

## Standards
- TypeScript strict mode
- ESLint + Prettier
- Jest for testing

## Structure
- `src/` - Source code
- `tests/` - Test files

## Workflow
1. Make changes
2. Run `npm test`
3. Run `npm run lint`
4. Commit with conventional commits
```

**.claude/context.md:**
```markdown
## Current Focus
- Feature: [current feature]
- Branch: [branch name]

## Recent Decisions
- [Decision 1]
- [Decision 2]

## Known Issues
- [Issue to be aware of]
```
