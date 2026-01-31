# Extension Audit Checklist

## Skills
- [ ] `skills/<name>/SKILL.md` with valid YAML frontmatter
- [ ] `name` and `description` fields present
- [ ] Third person ("Handles X" not "I help with X")
- [ ] Includes trigger phrases, under 500 chars
- [ ] Core content under 1500 tokens
- [ ] References linked and not orphaned

## Agents
- [ ] `agents/<name>.md` with valid frontmatter
- [ ] `name` and `description` fields
- [ ] 2-3 `<example>` blocks showing when to use
- [ ] `tools` or `disallowedTools` specified (minimum necessary)
- [ ] Under 2000 tokens

## Commands
- [ ] `commands/<name>.md`, under 200 tokens
- [ ] Clear, single-purpose instructions
- [ ] Optional: `description`, `argument-hint` in frontmatter

## Hooks
- [ ] Valid JSON config with valid event names
- [ ] Parse JSON from stdin (not env vars)
- [ ] Exit codes: 0=allow, 2=block
- [ ] Use `${CLAUDE_PLUGIN_ROOT}` for paths
- [ ] Fast (<5s), default to allow, handle errors

## Plugins
- [ ] `.claude-plugin/plugin.json` with name, description, version
- [ ] No empty directories, all files exist
- [ ] settings.local.json for dev permissions
- [ ] If marketplace: registered with valid path

## CLAUDE.md
- [ ] Under 2000 tokens, no stale rules
- [ ] Project-specific, actionable instructions

## Deprecated Patterns
- [ ] No `$TOOL_INPUT`/`$TOOL_OUTPUT`/`$TOOL_NAME` in scripts
- [ ] No `decision: block` (use exit 2)
- [ ] No `docs.anthropic.com` (use `code.claude.com`)
- [ ] No hardcoded paths, no first-person descriptions

## Token Budgets

| Type | Target | Max |
|------|--------|-----|
| Command | 50-150 | 200 |
| Skill | 500-1000 | 1500 |
| Skill+refs | 800-1500 | 3000 |
| Agent | 800-1500 | 2000 |

## Running Checks

```bash
python scripts/validate_extension.py --all
python scripts/pattern_detector.py --all
python scripts/token_counter.py --all --top 10
```
