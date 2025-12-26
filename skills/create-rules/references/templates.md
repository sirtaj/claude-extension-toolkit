# Rules Templates

## CLAUDE.md

### Generic Project
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

### TypeScript
```markdown
# Project

## Tech Stack
TypeScript 5.x, Node.js 20+

## Standards
- Strict TypeScript, async/await, JSDoc for public APIs

## Structure
- `src/` - Source, `src/types/` - Types, `tests/` - Jest tests

## Commands
- `npm run build`, `npm test`, `npm run lint`
```

## Settings

### Development
```json
{
  "permissions": {
    "allow": ["Read", "Write", "Edit", "Bash(npm:*)", "Bash(git:*)"]
  }
}
```

### Read-Only
```json
{
  "permissions": {
    "allow": ["Read", "Grep", "Glob"],
    "deny": ["Write", "Edit", "Bash"]
  }
}
```

### Full with Safety
```json
{
  "permissions": {
    "allow": ["*"],
    "deny": ["Bash(rm:-rf*)", "Bash(sudo:*)"]
  }
}
```

## Hook Configurations

### Security
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "echo '$TOOL_INPUT' | grep -qE 'rm -rf|sudo' && echo deny || echo approve"}]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "prompt", "prompt": "Check for secrets. Deny if found."}]
      }
    ]
  }
}
```

### Quality Gates
```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{"type": "prompt", "prompt": "Verify tests ran for code changes. Block if not."}]
    }]
  }
}
```
