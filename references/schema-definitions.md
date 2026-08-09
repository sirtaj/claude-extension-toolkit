# Schema Definitions

Auto-generated from `data/version-manifest.json` by `scripts/docs_fetcher.py update-schemas`. Do not edit by hand.

- Generated: 2026-08-09T18:23:45.682280Z
- Claude Code version: 2.1.226
- Last docs sync: 2026-08-09T18:23:45.681263Z

## Skill Frontmatter

| Field | Required |
|-------|----------|
| `description` | Recommended |
| `name` | No |
| `when_to_use` | No |
| `argument-hint` | No |
| `arguments` | No |
| `disable-model-invocation` | No |
| `user-invocable` | No |
| `allowed-tools` | No |
| `disallowed-tools` | No |
| `model` | No |
| `effort` | No |
| `context` | No |
| `agent` | No |
| `background` | No |
| `hooks` | No |
| `paths` | No |
| `shell` | No |
| `metadata` | No |
| `license` | No |
| `compatibility` | No |

## Agent Frontmatter

| Field | Required |
|-------|----------|
| `name` | Yes |
| `description` | Yes |
| `tools` | No |
| `disallowedTools` | No |
| `model` | No |
| `effort` | No |
| `color` | No |
| `hooks` | No |
| `permissionMode` | No |
| `skills` | No |
| `maxTurns` | No |
| `mcpServers` | No |
| `memory` | No |
| `background` | No |
| `isolation` | No |
| `initialPrompt` | No |

## Command Frontmatter

| Field | Required |
|-------|----------|
| `description` | No |
| `allowed-tools` | No |
| `model` | No |
| `argument-hint` | No |

## Plugin Manifest (plugin.json)

| Field | Required |
|-------|----------|
| `name` | Yes |
| `$schema` | No |
| `displayName` | No |
| `description` | No |
| `version` | No |
| `author` | No |
| `homepage` | No |
| `repository` | No |
| `license` | No |
| `keywords` | No |
| `metadata` | No |
| `defaultEnabled` | No |
| `skills` | No |
| `commands` | No |
| `agents` | No |
| `workflows` | No |
| `hooks` | No |
| `mcpServers` | No |
| `outputStyles` | No |
| `lspServers` | No |
| `userConfig` | No |
| `channels` | No |
| `dependencies` | No |
| `experimental` | No |

## Marketplace Manifest (marketplace.json)

| Field | Required |
|-------|----------|
| `name` | Yes |
| `owner` | Yes |
| `plugins` | Yes |
| `$schema` | No |
| `description` | No |
| `version` | No |
| `metadata` | No |
| `allowCrossMarketplaceDependenciesOn` | No |
| `renames` | No |

## Marketplace Plugin Entry

| Field | Required |
|-------|----------|
| `name` | Yes |
| `source` | Yes |
| `displayName` | No |
| `description` | No |
| `version` | No |
| `author` | No |
| `homepage` | No |
| `repository` | No |
| `license` | No |
| `keywords` | No |
| `metadata` | No |
| `category` | No |
| `tags` | No |
| `strict` | No |
| `relevance` | No |
| `defaultEnabled` | No |
| `skills` | No |
| `commands` | No |
| `agents` | No |
| `hooks` | No |
| `mcpServers` | No |
| `lspServers` | No |

## Hook Events

| Event | Can Block | Has Matcher |
|-------|-----------|-------------|
| `SessionStart` | No | Yes |
| `Setup` | No | Yes |
| `UserPromptSubmit` | Yes | No |
| `UserPromptExpansion` | Yes | Yes |
| `PreToolUse` | Yes | Yes |
| `PermissionRequest` | Yes | Yes |
| `PermissionDenied` | No | Yes |
| `PostToolUse` | No | Yes |
| `PostToolUseFailure` | No | Yes |
| `PostToolBatch` | Yes | No |
| `Notification` | No | Yes |
| `MessageDisplay` | No | No |
| `SubagentStart` | No | Yes |
| `SubagentStop` | Yes | Yes |
| `TaskCreated` | Yes | No |
| `TaskCompleted` | Yes | No |
| `Stop` | Yes | No |
| `StopFailure` | No | Yes |
| `TeammateIdle` | Yes | No |
| `InstructionsLoaded` | No | Yes |
| `ConfigChange` | Yes | Yes |
| `CwdChanged` | No | No |
| `DirectoryAdded` | No | Yes |
| `FileChanged` | No | Yes |
| `WorktreeCreate` | Yes | No |
| `WorktreeRemove` | No | No |
| `PreCompact` | Yes | Yes |
| `PostCompact` | No | Yes |
| `Elicitation` | Yes | Yes |
| `ElicitationResult` | Yes | Yes |
| `SessionEnd` | No | Yes |

## Valid Values

- **Model aliases**: `sonnet`, `opus`, `haiku`, `fable`
- **Model IDs**: `claude-opus-5`, `claude-sonnet-5`, `claude-fable-5`, `claude-haiku-4-5-20251001`
- **Model special**: `inherit`
- **Agent colors**: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`
- **Permission modes**: `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, `manual`
- **Hook handler types**: `command`, `http`, `mcp_tool`, `prompt`, `agent`
