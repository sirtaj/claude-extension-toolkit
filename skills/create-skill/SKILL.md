---
name: create-skill
description: This skill should be used when the user asks to "create a skill", "add a skill", "write a SKILL.md", or needs help with skill structure, progressive disclosure, references, or scripts.
---

# Creating Skills

Skills are modular packages providing specialized knowledge and workflows.

## Locations

| Location | Scope |
|----------|-------|
| `~/.claude/skills/` | Global (all projects) |
| `.claude/skills/` | Project-specific |

## Structure

```
skill-name/
├── SKILL.md           # Required - core instructions
├── references/        # Detailed docs (loaded on demand)
├── scripts/           # Executable utilities
└── examples/          # Working samples
```

## Minimal Skill

```markdown
---
name: my-skill
description: This skill should be used when the user asks to "do X" or needs help with Y.
---

# My Skill

## Purpose
Brief description.

## Workflow
1. First step
2. Second step
```

## Frontmatter

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Identifier |
| `description` | Yes | Trigger conditions (third person) |
| `allowed-tools` | No | Restrict tool access |

**Style**: Use imperative form (`Parse the file.` not `You should parse the file.`)

## Description Format

Write in third person with trigger phrases:
```yaml
description: This skill should be used when the user asks to "create a PDF", "rotate pages", or needs help with PDF manipulation.
```

## Progressive Disclosure

Keep SKILL.md lean (~500-1500 words). Move details to `references/`:

| SKILL.md | references/ |
|----------|-------------|
| Core workflow | Detailed patterns |
| Quick reference | Advanced techniques |
| Pointers to resources | API documentation |

## Additional Resources

### Reference Files
- `references/templates.md` - Skill templates
- `references/structure.md` - Directory patterns

### Official Documentation
- [Skills Guide](https://docs.anthropic.com/en/docs/claude-code/skills)
