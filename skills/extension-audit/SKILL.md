---
name: extension-audit
description: This skill should be used when the user asks to "audit extensions", "check my extensions", "optimize extensions", "extension health check", or needs help analyzing, validating, and improving Claude Code extensions.
---

# Extension Audit

Analyze and improve Claude Code extensions (skills, agents, commands, hooks, plugins, CLAUDE.md).

## Workflow

### 1. Discovery
Run utility scripts:
```bash
cd ~/.claude/plugins/claude-extension-toolkit
python scripts/validate_extension.py --all
python scripts/token_counter.py --all --top 10
python scripts/lint_references.py --all
```

### 2. Analysis

| Extension | Location | Checks |
|-----------|----------|--------|
| Skills | `~/.claude/skills/**/SKILL.md` | 500-1500 tokens, references/, frontmatter |
| Agents | `~/.claude/agents/*.md` | 800-2000 tokens, examples in description |
| Commands | `~/.claude/commands/*.md` | <200 tokens, clear purpose |
| Hooks | `settings.json` → hooks | Valid events, safe commands |
| Plugins | `~/.claude/plugins/*/plugin.json` | Valid manifest, coherent bundle |
| CLAUDE.md | Project root, `~/.claude/` | No stale rules, concise |

### 3. Proposal
```
## [Type]: [name]
Current: ~XXXX tokens | Target: ~XXXX (-XX%)

### Change 1: [Title]
**Before**: [excerpt]
**After**: [proposed]
Approve? [y/n/skip]
```

### 4. Execution
Apply approved changes via Edit tool. **Never edit without approval.**

## Token Targets

| Type | Target | Max |
|------|--------|-----|
| Skills | 800-1500 | 3000 |
| Agents | 1000-2000 | 3000 |
| Commands | 50-150 | 200 |

## Additional Resources

- `references/checklist.md` - Evaluation criteria
- `references/patterns.md` - Token optimization transforms
