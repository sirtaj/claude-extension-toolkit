---
name: extension-optimizer
description: Validates, audits, and upgrades Claude Code extensions. Detects deprecated patterns, checks schema compliance, and guides migrations. Use when auditing extensions, validating structure, upgrading hooks, or optimizing tokens. Triggers: "audit extensions", "validate skill", "check extensions", "upgrade hooks", "optimize tokens".
---

# Extension Optimizer

Analyze, validate, and improve Claude Code extensions.

## Quick Validation

Run toolkit scripts:

```bash
cd ~/.claude/plugins/claude-extension-toolkit

# Validate structure
${CLAUDE_PLUGIN_ROOT}/scripts/validate_extension.py <path>
${CLAUDE_PLUGIN_ROOT}/scripts/validate_extension.py --all

# Check for deprecated patterns
${CLAUDE_PLUGIN_ROOT}/scripts/pattern_detector.py <path>
${CLAUDE_PLUGIN_ROOT}/scripts/pattern_detector.py --all

# Count tokens
${CLAUDE_PLUGIN_ROOT}/scripts/token_counter.py <path>
${CLAUDE_PLUGIN_ROOT}/scripts/token_counter.py --all --top 10

# Validate marketplace
${CLAUDE_PLUGIN_ROOT}/scripts/marketplace_manager.py validate <marketplace-path>
```

## Audit Workflow

### 1. Discovery

Find all extensions:
```bash
# Skills
find ~/.claude -name "SKILL.md" -type f

# Agents
ls ~/.claude/agents/*.md

# Commands
ls ~/.claude/commands/*.md

# Plugins
ls ~/.claude/plugins/*/
```

### 2. Validation

Run comprehensive checks:

| Check | Script | What It Finds |
|-------|--------|---------------|
| Structure | `validate_extension.py` | Missing fields, invalid values |
| Patterns | `pattern_detector.py` | Deprecated patterns |
| Tokens | `token_counter.py` | Over-budget extensions |
| Links | `lint_references.py` | Broken references |

### 3. Report

For each issue found:
```
## [Type]: extension-name
Current: ~1500 tokens | Target: ~1000 (-33%)

### Issue 1: Deprecated env var usage
**Location**: hooks/check.sh:15
**Before**: `echo "$TOOL_INPUT" | ...`
**After**: `INPUT=$(cat); echo "$INPUT" | jq ...`

### Issue 2: Missing trigger phrases
**Location**: SKILL.md frontmatter
**Before**: `description: This skill handles X`
**After**: `description: Handles X. Use when the user asks to "do X" or mentions X.`
```

### 4. Apply Fixes

With approval, apply changes via Edit tool.

## Common Issues

### Deprecated Patterns

| Pattern | Issue | Fix |
|---------|-------|-----|
| `$TOOL_INPUT` | Env vars deprecated | Parse JSON from stdin |
| `$TOOL_OUTPUT` | Env vars deprecated | Parse JSON from stdin |
| `decision: block` | Old format | Use `permissionDecision: deny` |
| `docs.anthropic.com` | Old URL | Update to `code.claude.com` |
| `Task` tool | Renamed | Use `Agent` tool (Task still works as alias) |
| `$ARGUMENTS.0` | Old syntax | Use `$ARGUMENTS[0]` bracket syntax |
| Top-level `decision` | Old format | Use `hookSpecificOutput.permissionDecision` |
| Agent `resume` param | Removed | Use `SendMessage({to: agentId})` |

### Schema Issues

| Issue | Detection | Fix |
|-------|-----------|-----|
| Missing `name` | Frontmatter check | Add name field |
| Missing examples | Agent description | Add `<example>` blocks |
| Wrong tool list | Frontmatter check | Use current schema |
| Missing `maxTurns` | Agent check | Add if agent needs turn limits |

### Token Issues

| Type | Target | Max | If Over |
|------|--------|-----|---------|
| Skills | 500-1500 | 3000 | Move to references/ |
| Agents | 800-2000 | 3000 | Simplify objectives |
| Commands | 50-150 | 200 | Focus on essentials |

## Plugin Health

### Validate Plugin Structure

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/validate_extension.py <plugin-path>
```

Common issues:
- Missing `.claude-plugin/plugin.json`
- Empty skills/commands/agents directories
- Invalid JSON in manifests

### Marketplace Consistency

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/marketplace_manager.py validate <marketplace-path>
```

Checks:
- Plugin paths exist
- Plugin manifests valid
- Version consistency

## Marketplace audit

When auditing a plugin or marketplace directory, validate its `marketplace.json` using the tiered-severity checker.

### Run

```bash
python3 scripts/marketplace_manager.py validate <marketplace-root> --json
```

Output shape:
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Plugin 'x' missing optional field 'homepage'", "..."]
}
```

### Severity tiers

| Tier | Examples | Exit | Action |
|------|----------|------|--------|
| **Error** (exit 1) | Malformed JSON; missing required top-level fields; missing plugin-entry `name`/`source`; reserved name collision; unknown source type; `author` not `{name, email}` object; `metadata` not an object wrapper; source path outside marketplace root | blocks | Fix before shipping — plugin won't install |
| **Warning** (exit 0) | Missing optional `homepage`/`repository`/`license`/`keywords`/`description`; legacy `path` field; unknown metadata keys; duplicate plugin names within marketplace; schema drift | guides | Address when polishing; not install-blocking |

### Interpreting output

- `valid: true` with warnings: plugin installs; warnings are polish tasks (metadata completeness, duplicate-name hygiene).
- `valid: false`: do not ship. Each error maps to a concrete fix — see `references/marketplace-schema.md` for the correct shape.
- Reserved name errors: pick a different marketplace name. The authoritative reserved list is in `data/version-manifest.json` `schemas.marketplace_manifest.reserved_names`.
- `author` shape errors: convert string authors to object `{name, email?}`.
- `metadata` shape errors: wrap flat top-level `description`/`version`/`pluginRoot` into `metadata: {...}`.

### Built-in validator (complementary)

Run Claude Code's built-in validator as well for syntax-level checks:
```bash
claude plugin validate <marketplace-root>
```

The toolkit's `marketplace_manager.py` handles semantic checks the built-in doesn't (reserved names, path-exists, author/metadata shape).

Reference: [`references/marketplace-schema.md`](../../references/marketplace-schema.md)

## Upgrade Workflow

For major updates:

1. **Backup** current extensions
2. **Run** pattern detector
3. **Review** each finding
4. **Apply** fixes with approval
5. **Validate** after changes
6. **Test** extension behavior

See `references/migrations.md` for before/after examples.

## Token Optimization

### Progressive Disclosure

Move details from SKILL.md to references/:

| In SKILL.md | In references/ |
|-------------|----------------|
| Core workflow | Detailed patterns |
| Quick reference table | Complete API docs |
| Getting started | Advanced techniques |

### Reduce Duplication

- Share common content in `references/`
- Link instead of copy
- Use templates

### Simplify Content

- Remove redundant examples
- Consolidate similar sections
- Use tables instead of prose

## Additional Resources

- `references/migrations.md` - Before/after upgrade examples
- `references/checklist.md` - Complete audit checklist
