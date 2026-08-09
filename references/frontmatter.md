# Frontmatter Reference

Complete reference for all extension frontmatter fields.

Verified against Claude Code 2.1.226 docs (2026-08-09).

## Skill Frontmatter

**Every skill field is optional.** Only `description` is recommended, so Claude
knows when to load the skill. Without one, Claude Code uses the first paragraph
of the markdown body.

```yaml
---
name: skill-name                      # Display label in skill listings
description: Third-person trigger...  # Recommended: activation conditions
when_to_use: "trigger phrases..."     # Extra activation context
allowed-tools:                        # Pre-approved tools for the invoking turn
  - Read
  - Grep
model: sonnet                         # sonnet, opus, haiku, fable, ID, or inherit
effort: high                          # low, medium, high, xhigh, max
context: fork                         # fork to run in a subagent context
agent: Explore                        # Subagent type to use with context: fork
background: true                      # With context: fork, run in background
hooks:                                # Skill-scoped hooks
  PreToolUse: [...]
argument-hint: "[filename] [format]"  # Autocomplete hint
arguments: [issue, branch]            # Named positional args for $name
disable-model-invocation: false       # Require explicit /skill
user-invocable: true                  # Show in the / menu
paths: ["src/**/*.ts"]                # Only auto-activate for matching files
---
```

### Field Details

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `name` | No | string | Display label in listings. Defaults to the directory name. In a **plugin** skill it also sets the last segment of the command (`/my-plugin:name`) |
| `description` | Recommended | string | What the skill does and when to use it, in third person |
| `when_to_use` | No | string | Trigger phrases or example requests, appended to `description` |
| `argument-hint` | No | string | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | No | string/list | Named positional arguments for `$name` substitution |
| `disable-model-invocation` | No | bool | Prevent auto-activation; require `/skill`. Also blocks preloading into subagents |
| `user-invocable` | No | bool | Set `false` to hide from the `/` menu. Default `true` |
| `allowed-tools` | No | string/list | Tools pre-approved for the invoking **turn** (grant clears on your next message). Does not restrict anything |
| `disallowed-tools` | No | string/list | Tools removed from the pool while the skill is active |
| `model` | No | string | Same values as `/model`, or `inherit`. With `context: fork`, sets the forked subagent's model |
| `effort` | No | enum | `low`, `medium`, `high`, `xhigh`, `max` |
| `context` | No | string | `fork` runs the skill in a forked subagent context |
| `agent` | No | string | Which subagent type to use when `context: fork` is set |
| `background` | No | bool | Only with `context: fork`. `false` waits for the result in the invoking turn. Default `true` |
| `hooks` | No | object | Skill-scoped hooks (the only place `once: true` is honored) |
| `paths` | No | string/list | Globs limiting when the skill auto-activates |
| `shell` | No | enum | `bash` (default) or `powershell` for `` !`command` `` blocks |
| `metadata` | No | map | Free-form data for your own tooling; Claude Code ignores it |
| `license` | No | string | Agent Skills spec field; accepted but not acted on |
| `compatibility` | No | string | Agent Skills spec field (≤500 chars); accepted but not acted on |

Boolean fields accept `yes`/`no`/`on`/`off`/`1`/`0` in any case as well as
`true`/`false`.

### Portability outside Claude Code

Skills follow the [Agent Skills](https://agentskills.io) open standard. Only six
fields are valid outside Claude Code — for claude.ai uploads, the Skills API,
and `package_skill.py`:

`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`

Any other field causes a **hard error** on packaging or upload, not a silent
ignore. Restrict frontmatter to those six if the skill needs to travel.

### Name Validation

- Maximum 64 characters
- Lowercase letters, numbers, and hyphens only (`^[a-z0-9-]+$`)
- Combined `description` + `when_to_use` is truncated at 1,536 characters in the
  skill listing, so put the key use case first

### Description Best Practices

Write in **third person, prescriptive voice**:

```yaml
# Good
description: Creates PDF documents from markdown files. Use when converting docs, generating reports, or building documentation.

# Avoid
description: I can help you create PDFs from markdown.
description: This skill is for creating PDFs.
```

Include trigger phrases users might say:
```yaml
description: Analyzes Python code for type errors and linting issues. Use when the user mentions "type check", "lint", "ruff", or "pyright".
```

### Skill Variables

Variables available in skill content:

| Variable | Purpose |
|----------|---------|
| `$ARGUMENTS` | Full argument string passed to skill |
| `$ARGUMENTS[N]` | Nth argument (0-indexed) |
| `$N` | Shorthand for `$ARGUMENTS[N]` (e.g., `$0`, `$1`) |
| `$name` | Named argument declared in the `arguments` frontmatter list |
| `${CLAUDE_SESSION_ID}` | Current session identifier |
| `${CLAUDE_EFFORT}` | Active effort level: low, medium, high, xhigh, max |
| `${CLAUDE_SKILL_DIR}` | Directory containing the SKILL.md file |
| `${CLAUDE_PROJECT_DIR}` | Project root (same value hooks receive) |

`${CLAUDE_SKILL_DIR}` and `${CLAUDE_PROJECT_DIR}` are substituted in **both** the
markdown body and Bash rules in `allowed-tools`. Use the same variable in both
so a bundled script runs without a permission prompt:

```yaml
---
name: render-chart
description: Render a chart from a CSV file
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
---

Run `${CLAUDE_SKILL_DIR}/scripts/render.sh <csv-file>` to render the chart.
```

Escape a literal `$` before a digit or `ARGUMENTS` with a backslash: `\$1.00`.

### Dynamic Context Injection

Prefix a backtick-wrapped shell command with `!` to inject dynamic content:

```yaml
---
name: my-skill
description: Skill with dynamic context
---

Current git status:
!`git status --short`

Current branch:
!`git branch --show-current`
```

**Note:** The "ultrathink" keyword in skill content triggers extended thinking mode.

## Agent Frontmatter

```yaml
---
name: agent-name                      # Required: Agent tool identifier
description: |                        # Required: with <example> blocks
  Autonomous agent for task X.

  <example>
  user: "Do X"
  assistant: "I'll launch agent-name"
  </example>
tools:                                # Optional: allowed tools (default: inherit)
  - Read
  - Write
  - Bash
disallowedTools:                      # Optional: explicitly blocked tools
  - Agent
model: opus                           # Optional: override model
effort: high                           # Optional: low, medium, high, xhigh, max
color: cyan                           # Optional: display color
hooks:                                # Optional: agent-scoped hooks
  PostToolUse: [...]
permissionMode: auto                  # Optional: permission handling
skills:                               # Optional: preload skills
  - code-review
maxTurns: 50                           # Optional: max agentic turns
mcpServers:                            # Optional: MCP servers to load
  - server-name
memory: project                        # Optional: user, project, or local
background: false                      # Optional: always run in background
isolation: worktree                    # Optional: git worktree isolation
---
```

### Field Details

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `name` | Yes | string | Identifier for Agent tool `subagent_type`. Lowercase letters and hyphens. **Cannot contain `:`** — that's reserved for plugin-scoped names, and a file with one fails to load |
| `description` | Yes | string | When to use, with example blocks |
| `tools` | No | list | Allowlist. Inherits every tool available to subagents when omitted |
| `disallowedTools` | No | list | Denylist, applied before `tools` resolves. Accepts `mcp__<server>` patterns |
| `model` | No | string | `sonnet`, `opus`, `haiku`, `fable`, a full ID (`claude-opus-5`), or `inherit`. Defaults to `inherit` |
| `effort` | No | enum | `low`, `medium`, `high`, `xhigh`, `max` |
| `color` | No | enum | red, blue, green, yellow, purple, orange, pink, cyan |
| `hooks` | No | object | Agent-specific hook definitions |
| `permissionMode` | No | enum | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, or `manual` (alias for `default`) |
| `skills` | No | list | Skills preloaded into the agent's context at startup (full content, not just the description) |
| `maxTurns` | No | number | Maximum agentic turns before the subagent stops |
| `mcpServers` | No | list/object | Server names or inline definitions |
| `memory` | No | enum | Persistent memory scope: `user`, `project`, or `local` |
| `background` | No | bool | `true` always runs as a background task. Unset lets Claude choose, and it backgrounds by default |
| `isolation` | No | enum | `worktree` runs the agent in a temporary git worktree, branched from your default branch |
| `initialPrompt` | No | string | Auto-submitted first user turn when the agent runs as the **main** session agent (`--agent` or the `agent` setting) |

### Tools Available to Subagents

A subagent's tool pool is narrowed by two filters, so the same definition can
resolve to different tools in the foreground and the background.

**Removed from every subagent**, even when listed in `tools`:
`AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ScheduleWakeup`,
`TaskOutput`, `WaitForMcpServers`, `Workflow`, plus `ExitPlanMode` (unless
`permissionMode: plan`) and `Agent` at the depth limit.

**Background subagents** (the default) keep every MCP tool but only these
built-ins: `Read`, `Grep`, `Glob`, `Bash`, `PowerShell`, `Edit`, `Write`,
`NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`,
`EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, and
`Artifact`. Agent-team teammates additionally keep the task and cron tools.

If nothing in `tools` resolves to an available tool, the subagent refuses to
launch and the Agent tool returns an error naming the unresolved entries.

### Example Blocks

Agent descriptions should include `<example>` blocks showing when to use:

```yaml
description: |
  Analyzes code for security vulnerabilities.

  <example>
  user: "Check this code for security issues"
  assistant: "I'll launch the security-analyzer agent"
  </example>

  <example>
  user: "Is this SQL query safe?"
  assistant: "Let me use security-analyzer to check for injection"
  </example>
```

### Plugin Security Restrictions

Agent definitions shipped in plugins **ignore** these fields:
- `hooks` — cannot override hook configuration
- `mcpServers` — cannot inject MCP servers
- `permissionMode` — cannot change permission handling

These restrictions prevent plugins from escalating privileges.

## Command Frontmatter

Commands are merged into skills: `.claude/commands/foo.md` and
`.claude/skills/foo/SKILL.md` both create `/foo`, and a flat command file
supports **the same frontmatter as a skill**. Prefer `skills/` for new work —
only a skill directory can carry supporting files.

The fields that matter most for a flat command file:

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `description` | Recommended | string | Shown in the `/` menu |
| `allowed-tools` | No | string/list | Pre-approved tools for the invoking turn |
| `model` | No | string | Model override |
| `argument-hint` | No | string | Autocomplete hint |
| `disable-model-invocation` | No | bool | Set `true` for a command only you should trigger |

## Plugin Manifest (plugin.json)

The manifest is **optional**. Without one, components are auto-discovered in
their default directories and the plugin name comes from the directory name.
If you include a manifest, `name` is the only required field.

```json
{
  "name": "my-plugin",
  "displayName": "My Plugin",
  "description": "What this plugin provides",
  "version": "1.0.0",
  "author": {
    "name": "Author Name",
    "email": "author@example.com"
  },
  "keywords": ["tag1", "tag2"],
  "repository": "https://github.com/user/repo",
  "license": "MIT"
}
```

### Field Details

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `name` | Yes | string | Plugin identifier (kebab-case). Used for component namespacing |
| `displayName` | No | string | Human-readable name for UI surfaces; may contain spaces |
| `description` | No | string | What the plugin provides |
| `version` | No | string | Semantic version. **Setting it pins the plugin** — users only get updates when the string changes |
| `author` | No | object | `{"name": "...", "email"?, "url"?}` — must be object, not string |
| `keywords` | No | list | Discovery tags |
| `repository` | No | string | Source URL |
| `homepage` | No | string | Documentation URL |
| `license` | No | string | License identifier |
| `metadata` | No | object | Free-form; Claude Code never reads it |
| `defaultEnabled` | No | bool | `false` installs the plugin disabled. Default `true` |
| `$schema` | No | string | JSON Schema URL for editor autocomplete; ignored at load |

Component path fields — each replaces or supplements the default directory:
`skills`, `commands`, `agents`, `workflows`, `hooks`, `mcpServers`,
`outputStyles`, `lspServers`, plus `experimental.themes` and
`experimental.monitors`. Also available: `userConfig` (values prompted at enable
time), `channels`, and `dependencies` (other plugins, with optional semver
constraints).

Unrecognized top-level fields are ignored so one manifest can double as a
`package.json` or VS Code manifest. `claude plugin validate` reports them as
warnings; `--strict` turns warnings into errors.

## Valid Values

### Models
Aliases resolve per provider and update over time; pin with a full model ID.

- `opus` — most capable (Anthropic API: Opus 5, full ID `claude-opus-5`)
- `sonnet` — balanced (Anthropic API: Sonnet 5, full ID `claude-sonnet-5`)
- `haiku` — fastest, lowest cost (`claude-haiku-4-5-20251001`)
- `fable` — Claude Fable 5, for long autonomous sessions (`claude-fable-5`)
- `inherit` — use the parent/session model
- `opus[1m]` — Opus with a 1M-token context window
- `opusplan` — opus during plan mode, sonnet for execution

### Effort Levels
- `low`, `medium`, `high`, `xhigh`, `max` (available levels depend on the model)

### Agent Colors
- `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`

(`magenta` is **not** valid — it was never in the supported set.)

### Common Tool Lists

**Read-only:**
```yaml
allowed-tools: [Read, Glob, Grep, WebFetch, WebSearch]
```

**Code generation:**
```yaml
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
```

**Testing:**
```yaml
allowed-tools: [Read, Glob, Grep, Bash]
```
