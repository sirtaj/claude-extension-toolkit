# Tool Reference

Built-in tools and restriction patterns for Claude Code extensions.

## Built-in Tools

| Tool | Purpose | Side Effects |
|------|---------|--------------|
| `Read` | Read file contents | None |
| `Write` | Create/overwrite files | Creates/modifies files |
| `Edit` | Modify file sections | Modifies files |
| `Glob` | Find files by pattern | None |
| `Grep` | Search file contents | None |
| `Bash` | Execute shell commands | Depends on command |
| `WebFetch` | Fetch URL content | None |
| `WebSearch` | Search the web | None |
| `Task` | Launch subagents | Spawns agent |
| `AskUserQuestion` | Interactive prompts | User interaction |
| `NotebookEdit` | Edit Jupyter notebooks | Modifies notebooks |

## Common Restriction Patterns

### Read-Only (Analysis)

For agents that should never modify files:

```yaml
allowed-tools:
  - Read
  - Glob
  - Grep
  - WebFetch
  - WebSearch
```

Use for: code review, documentation analysis, research

### Code Generation

For agents that create and modify code:

```yaml
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
```

Use for: code generation, refactoring, automation

### Testing Only

For agents that run tests but don't modify code:

```yaml
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
```

Use for: test runners, CI helpers

### Documentation

For agents that only work with docs:

```yaml
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
```

Use for: documentation generators, README updaters

### No Subagents

Prevent recursive agent spawning:

```yaml
disallowedTools:
  - Task
```

Use for: leaf agents that shouldn't delegate

### No External Access

Prevent network access:

```yaml
disallowedTools:
  - WebFetch
  - WebSearch
```

Use for: offline-only agents, security-sensitive tasks

## Permission Modes

Used in agent frontmatter `permissionMode`:

| Mode | Behavior |
|------|----------|
| `auto` | Use parent's permission settings |
| `bypassPermissions` | Skip permission prompts (dangerous) |

## Tool Categories

**Filesystem:**
- Read, Write, Edit, Glob, Grep, NotebookEdit

**Network:**
- WebFetch, WebSearch

**Execution:**
- Bash, Task

**Interactive:**
- AskUserQuestion

## Best Practices

1. **Principle of least privilege**: Only allow tools the agent needs
2. **Prefer allowlist**: Use `tools` over `disallowedTools` when possible
3. **No Bash for untrusted input**: Be careful with agents that take user input to Bash
4. **Consider Task carefully**: Agents with Task can spawn other agents

## Examples

**Security scanner (read-only, no network):**
```yaml
tools:
  - Read
  - Glob
  - Grep
disallowedTools:
  - WebFetch
  - WebSearch
```

**Code formatter (modify only, no shell):**
```yaml
tools:
  - Read
  - Write
  - Edit
  - Glob
disallowedTools:
  - Bash
```

**Research agent (network, no modifications):**
```yaml
tools:
  - Read
  - Glob
  - Grep
  - WebFetch
  - WebSearch
disallowedTools:
  - Write
  - Edit
  - Bash
```
