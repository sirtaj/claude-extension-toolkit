# Tool Reference

Built-in tools and restriction patterns for Claude Code extensions.

Verified against Claude Code 2.1.283 docs (2026-09-28).
Canonical docs: https://code.claude.com/docs/en/tools-reference

Tool names are the exact strings used in permission rules, subagent `tools`
lists, and hook matchers.

## Built-in Tools

| Tool | Purpose | Side Effects |
|------|---------|--------------|
| `Read` | Read file contents | None |
| `Write` | Create/overwrite files | Creates/modifies files |
| `Edit` | Modify file sections | Modifies files |
| `Glob` | Find files by pattern (see note below) | None |
| `Grep` | Search file contents, ripgrep syntax (see note below) | None |
| `Bash` | Execute shell commands | Depends on command |
| `PowerShell` | Execute PowerShell natively | Depends on command |
| `WebFetch` | Fetch URL content | None |
| `WebSearch` | Search the web | None |
| `Agent` | Launch subagents | (formerly Task, still works as alias) |
| `SendMessage` | Message a teammate, resumed subagent, or other session | Agent communication |
| `ListAgents` | List agents reachable via SendMessage (2.1.224+, cross-session messaging only) | None |
| `SubagentHandback` | Deliver a subagent's final report (auto mode, local non-fork subagents; 2.1.271+) | Agent communication |
| `AskUserQuestion` | Interactive prompts | User interaction |
| `NotebookEdit` | Edit Jupyter notebooks | Modifies notebooks |
| `Monitor` | Run a command in the background, feeding output lines back | Runs command |
| `Artifact` | Publish an HTML/Markdown file as a claude.ai artifact | Publishes externally |
| `SendUserFile` | Send session files to the user | Sends externally |
| `PushNotification` | Desktop notification (and phone push via Remote Control) | Notifies |
| `EndConversation` | End the session (main conversation only; 2.1.213+) | Ends session |
| `SendFeedback` | Draft a Claude Code feedback report for you to review (2.1.238+) | Queues local draft |
| `ShareOnboardingGuide` | Upload `ONBOARDING.md` from `/team-onboarding` and return a share link | Publishes externally |
| `CronCreate` | Create scheduled task | Creates session-scoped cron job |
| `CronDelete` | Delete scheduled task | Removes cron job |
| `CronList` | List scheduled tasks | None |
| `RemoteTrigger` | Create/update/run Routines on claude.ai | Modifies remote routines |
| `ScheduleWakeup` | Reschedule the next self-paced `/loop` iteration | Schedules |
| `EnterPlanMode` | Switch to plan mode | Mode change |
| `ExitPlanMode` | Present a plan for approval, exit plan mode | Mode change |
| `EnterWorktree` | Enter git worktree | Creates worktree |
| `ExitWorktree` | Exit git worktree | Cleans up worktree |
| `LSP` | Query language server | None |
| `Skill` | Invoke a skill | Depends on skill |
| `Workflow` | Run a dynamic workflow orchestrating many subagents | Spawns agents |
| `ReportFindings` | Report code-review findings as structured data (2.1.196+) | None |
| `TaskCreate` | Create a task (model-dependent default; see below) | Spawns task |
| `TaskGet` | Get task details | None |
| `TaskList` | List tasks | None |
| `TaskStop` | Stop a running background task or named agent | Stops task |
| `TaskUpdate` | Update task status/dependencies/details | Modifies task |
| `ToolSearch` | Search and load deferred tools | None |
| `WaitForMcpServers` | Wait for MCP servers still connecting | None |
| `ListMcpResourcesTool` | List MCP resources | None |
| `ReadMcpResourceTool` | Read MCP resource | None |

**Deprecated / disabled by default:**

| Tool | Status |
|------|--------|
| `TodoWrite` | Disabled by default since v2.1.142 in favor of the `Task*` tools; `CLAUDE_CODE_ENABLE_TASKS=0` restores it where task tools are available |
| `TaskOutput` | Deprecated in favor of `Read` on the task's output file path |
| `Task` | Renamed to `Agent` in v2.1.63; still accepted as an alias |

**Task-tracking tools availability (v2.1.268+):** `TaskCreate`, `TaskGet`, `TaskList`,
`TaskUpdate` (and `TodoWrite`) are provided by default only on Claude 3.x,
Opus 4 through 4.7, Sonnet 4 through 4.6, and Haiku 4.5. On newer models
(Opus 4.8+, Sonnet 5, Fable) and unrecognized model IDs they are absent unless
you opt in: `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`, naming one of them in
`--allowedTools`, or listing them in `--tools`. Background and cloud sessions
get them on every model. A subagent gets them only when the session has them.

**Glob / Grep absent by default on macOS, Linux, and WSL:** Claude searches
with `find`/`grep` through `Bash` instead (those calls reach hooks and
permission rules as `Bash`). The tools come back when named in `--tools` or
`--allowedTools` at launch (a settings allow rule doesn't count), when `Bash`
is removed from the session, or for a subagent that lists `Glob`/`Grep` in
`tools` and leaves out `Bash`. On Windows they're in the default set.

**Always-present:** `EndConversation` can't be removed by deny/ask rules,
`--disallowedTools`, or `--tools` while any other tool remains, and
`PreToolUse` hooks don't run for it. Subagents never get it.

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

### Rule Specifiers

Permission rules, `--allowedTools`/`--disallowedTools`, skill `allowed-tools`,
and hook `if` conditions all use `ToolName(specifier)`:

| Rule format | Applies to |
|-------------|-----------|
| `Bash(npm run *)` | Bash, Monitor |
| `PowerShell(Get-ChildItem *)` | PowerShell |
| `Read(~/secrets/**)` | Read, Grep, Glob, LSP |
| `Edit(/src/**)` | Edit, Write, NotebookEdit |
| `Skill(deploy *)` | Skill |
| `Agent(Explore)` | Agent |
| `WebFetch(domain:example.com)` | WebFetch |

Other tools (e.g. `WebSearch`, `ExitPlanMode`, `ShareOnboardingGuide`) take
only the bare name. An `Edit(...)` allow also grants read on that path; a
`Read(...)` deny also blocks Edit and Write there. Hook `matcher` fields use
bare tool names, not this format.

### Restricting Spawnable Agents

Limit which agent types can be spawned:

```yaml
tools:
  - Agent(worker, researcher)
```

This allowlist applies **only** to an agent running as the main thread via
`claude --agent`. In a subagent definition, a bare `Agent` lets it spawn
subagents while the depth limit allows, and any type list in the parentheses is
ignored. Omitting `Agent` entirely blocks subagent spawning.

To block specific agents while allowing the rest, use `permissions.deny`.

### Tools Removed from Subagents

Some tools are stripped from every subagent regardless of the `tools` list, and
background subagents (the default) keep an even smaller built-in set. See
`references/frontmatter.md` → "Tools Available to Subagents" for both lists.

## Permission Modes

Used in agent frontmatter `permissionMode`:

| Mode | Behavior |
|------|----------|
| `default` | Manual mode: standard permission checking with prompts (only reads run unprompted) |
| `manual` | Alias for `default` (2.1.200+) |
| `acceptEdits` | Auto-accept file edits and common filesystem commands in the working directory |
| `auto` | A background classifier reviews commands and protected-directory writes |
| `dontAsk` | Auto-**deny** prompts. Explicitly allowed tools still work |
| `bypassPermissions` | Skip permission prompts (dangerous) |
| `plan` | Plan mode: read-only exploration (plus classifier-approved commands when auto mode is available); edits blocked until a plan is approved |

A parent using `bypassPermissions` or `acceptEdits` takes precedence and can't
be overridden by a subagent. Under `auto`, a subagent's `permissionMode` is
ignored entirely — the classifier evaluates its calls with the parent's rules.
Plugin subagents ignore `permissionMode` altogether.

As of v2.1.283, `auto` is the built-in starting mode for interactive terminal
and VS Code sessions (`-p` and the Agent SDK still start in `default`).

## Tool Categories

**Filesystem:**
- Read, Write, Edit, Glob, Grep, NotebookEdit

**Network:**
- WebFetch, WebSearch

**Execution:**
- Bash, PowerShell, Monitor, Agent, Workflow

**Interactive:**
- AskUserQuestion, EndConversation, SendFeedback

**Planning:**
- EnterPlanMode, ExitPlanMode

**Scheduling:**
- CronCreate, CronDelete, CronList, RemoteTrigger, ScheduleWakeup

**Agent Management:**
- Agent, SendMessage, ListAgents, SubagentHandback, TaskCreate, TaskGet, TaskList, TaskStop, TaskUpdate

**Worktree:**
- EnterWorktree, ExitWorktree

**MCP:**
- ListMcpResourcesTool, ReadMcpResourceTool, WaitForMcpServers

**Output / sharing:**
- Artifact, SendUserFile, PushNotification, ReportFindings, ShareOnboardingGuide

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
