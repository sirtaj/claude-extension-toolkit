# Skill Directory Structure

## Layout

```
skill-name/
├── SKILL.md           # Required (500-1500 words)
├── references/        # Loaded on demand
│   └── *.md
├── scripts/           # Utilities
└── examples/          # Samples
```

## Location Priority

| Location | Scope |
|----------|-------|
| `.claude/skills/` | Project (higher priority) |
| `~/.claude/skills/` | Global |

## SKILL.md Content

| Include | Move to references/ |
|---------|---------------------|
| Purpose & overview | Detailed explanations |
| Core workflow | Step-by-step guides |
| Quick reference | Full API docs |
| Pointers to refs | Pattern deep-dives |

## Progressive Loading

1. Claude reads SKILL.md first (always)
2. References loaded only when needed
3. Use: "See `references/api.md#section` for details"

## Complexity Levels

**Minimal**: Just `SKILL.md`

**Standard**: `SKILL.md` + `references/patterns.md`

**Full**: All directories with scripts and examples
