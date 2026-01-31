---
name: extension-sync
description: Syncs Claude Code documentation and updates schema definitions. Fetches canonical docs, detects API changes, tracks version compatibility. Use when checking for updates, syncing docs, verifying schema currency, or after Claude Code updates.
---

# Extension Sync

Keep the toolkit current with Claude Code changes.

## Quick Status

Check sync status:
```bash
cd ~/.claude/plugins/claude-extension-toolkit
python scripts/docs_fetcher.py check
```

## Sync Workflow

### 1. Fetch Latest Docs

```bash
python scripts/docs_fetcher.py sync
```

This:
- Fetches canonical documentation pages
- Caches content in `data/cache/`
- Updates `references/schema-definitions.md`
- Records sync timestamp in manifest

### 2. Review Changes

After sync, check for:
- New frontmatter fields
- New hook events
- Deprecated patterns
- Changed behaviors

### 3. Update Extensions

If changes affect your extensions:
1. Run `/extension-optimizer` to check
2. Apply migrations from `references/migrations.md`
3. Test affected extensions

## Canonical Sources

The toolkit tracks these official sources:

| Source | URL | Contains |
|--------|-----|----------|
| Skills | `code.claude.com/docs/en/skills` | Frontmatter schema |
| Best Practices | `platform.claude.com/docs/.../best-practices` | Description format |
| Subagents | `code.claude.com/docs/en/sub-agents` | Agent schema |
| Hooks | `code.claude.com/docs/en/hooks` | Events, input format |
| Plugins | `code.claude.com/docs/en/plugins` | Plugin structure |
| Plugins Reference | `code.claude.com/docs/en/plugins-reference` | Complete specs |

## Version Manifest

The toolkit maintains `data/version-manifest.json`:

```json
{
  "manifest_version": "1.0",
  "claude_code_version": "2.1.27",
  "last_docs_sync": "2026-01-31T12:00:00Z",
  "schemas": {
    "skill_frontmatter": {...},
    "agent_frontmatter": {...},
    "hooks": {...}
  },
  "deprecations": [...]
}
```

### Key Fields

- `last_docs_sync` - When docs were last fetched
- `schemas` - Current field definitions
- `deprecations` - Known deprecated patterns

## Automated Checks

The toolkit can check for staleness automatically.

### SessionStart Hook (Optional)

Add to `settings.json` to check on each session:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/scripts/quick_update_check.sh",
        "timeout": 5
      }]
    }]
  }
}
```

Outputs warnings if:
- Docs cache >7 days old
- Deprecated patterns in recent files

## Manual Sync

To force a full sync:

```bash
cd ~/.claude/plugins/claude-extension-toolkit

# Fetch all docs
python scripts/docs_fetcher.py sync

# Regenerate schema definitions
python scripts/docs_fetcher.py update-schemas

# Check your extensions against new schemas
python scripts/validate_extension.py --all
python scripts/pattern_detector.py --all
```

## What Gets Updated

| File | Purpose |
|------|---------|
| `data/version-manifest.json` | Schema versions, deprecations |
| `data/cache/*.txt` | Cached doc content |
| `references/schema-definitions.md` | Human-readable schema reference |

## Community Sources

The toolkit also tracks community resources:

| Source | Purpose |
|--------|---------|
| scottspence.com/posts/... | Skill activation workarounds |
| claude-plugins.dev | Community plugins registry |

These are informational only, not authoritative.

## Troubleshooting

### Sync Fails

If docs can't be fetched:
- Check network connectivity
- Verify URLs haven't changed
- Check `data/canonical-sources.json` for correct URLs

### Schema Mismatch

If validation finds unknown fields:
- May be new features not yet in manifest
- Run sync to update schemas
- Or add to manifest manually

### Cached Content Stale

Force refresh:
```bash
rm -rf data/cache/
python scripts/docs_fetcher.py sync
```
