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
| `Agent` | Launch subagents | (formerly Task, still works as alias) |
| `SendMessage` | Send message to running agent | Agent communication |
| `AskUserQuestion` | Interactive prompts | User interaction |
| `NotebookEdit` | Edit Jupyter notebooks | Modifies notebooks |
| `CronCreate` | Create scheduled task | Creates cron job |
| `CronDelete` | Delete scheduled task | Removes cron job |
| `CronList` | List scheduled tasks | None |
| `EnterPlanMode` | Switch to plan mode | Mode change |
| `ExitPlanMode` | Exit plan mode | Mode change |
| `EnterWorktree` | Enter git worktree | Creates worktree |
| `ExitWorktree` | Exit git worktree | Cleans up worktree |
| `LSP` | Query language server | None |
| `Skill` | Invoke a skill | Depends on skill |
| `TaskCreate` | Create background task | Spawns task |
| `TaskGet` | Get task status | None |
| `TaskList` | List tasks | None |
| `TaskOutput` | Read task output | None |
| `TaskStop` | Stop a task | Stops task |
| `TaskUpdate` | Update task state | Modifies task |
| `TodoWrite` | Write todo items | Creates todos |
| `ToolSearch` | Search available tools | None |
| `ListMcpResourcesTool` | List MCP resources | None |
| `ReadMcpResourceTool` | Read MCP resource | None |

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
  - Agent
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

### Restricting Spawnable Agents

Limit which agent types can be spawned:

```yaml
allowed-tools:
  - Agent(worker, researcher)
```

This allows the agent to only spawn `worker` and `researcher` subagent types.

## Permission Modes

Used in agent frontmatter `permissionMode`:

| Mode | Behavior |
|------|----------|
| `default` | Standard permission prompts |
| `acceptEdits` | Auto-approve file edits, prompt for others |
| `dontAsk` | Auto-approve most actions |
| `bypassPermissions` | Skip all permission prompts (dangerous) |
| `plan` | Require plan approval before execution |

## Tool Categories

**Filesystem:**
- Read, Write, Edit, Glob, Grep, NotebookEdit

**Network:**
- WebFetch, WebSearch

**Execution:**
- Bash, Agent

**Interactive:**
- AskUserQuestion

**Planning:**
- EnterPlanMode, ExitPlanMode, TodoWrite

**Scheduling:**
- CronCreate, CronDelete, CronList

**Agent Management:**
- Agent, SendMessage, TaskCreate, TaskGet, TaskList, TaskOutput, TaskStop, TaskUpdate

**Worktree:**
- EnterWorktree, ExitWorktree

**MCP:**
- ListMcpResourcesTool, ReadMcpResourceTool

**Discovery:**
- ToolSearch, Skill, LSP

## Best Practices

1. **Principle of least privilege**: Only allow tools the agent needs
2. **Prefer allowlist**: Use `tools` over `disallowedTools` when possible
3. **No Bash for untrusted input**: Be careful with agents that take user input to Bash
4. **Consider Agent carefully**: Agents with Agent can spawn other agents recursively
5. **MCP tool names**: Use qualified names for MCP tools: `mcp__serverName__toolName`

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
