# Skill Directory Structure

## Standard Layout

```
skill-name/
├── SKILL.md           # Required - core instructions (keep lean)
├── references/        # Detailed documentation (loaded on demand)
│   ├── api.md         # API/tool reference
│   ├── patterns.md    # Design patterns
│   ├── advanced.md    # Advanced techniques
│   └── examples.md    # Detailed examples
├── scripts/           # Executable utilities
│   ├── setup.sh       # Environment setup
│   ├── validate.sh    # Validation script
│   └── utils.py       # Helper scripts
└── examples/          # Working samples
    ├── config.yaml    # Example configuration
    └── sample-output/ # Sample outputs
```

## Location Priority

| Location | Scope | Priority |
|----------|-------|----------|
| `.claude/skills/` | Project-specific | Highest |
| `~/.claude/skills/` | User global | Lower |

Project skills override global skills with the same name.

## SKILL.md Guidelines

### Size Target
- **Ideal**: 500-1000 words
- **Maximum**: 1500 words
- **If larger**: Move details to `references/`

### Required Sections
1. **Frontmatter** - name, description, optional allowed-tools
2. **Purpose** - What this skill provides
3. **Core Workflow** - Main steps (high-level)
4. **Quick Reference** - Essential tables/lists
5. **Additional Resources** - Pointers to references/

### Content Placement

| In SKILL.md | In references/ |
|-------------|----------------|
| Overview and purpose | Detailed explanations |
| Core workflow steps | Step-by-step guides |
| Quick reference tables | Complete API reference |
| Common patterns (brief) | Pattern deep-dives |
| Troubleshooting summary | Full troubleshooting guide |

## References Directory

### Common Files

| File | Purpose |
|------|---------|
| `api.md` | Tool/API documentation |
| `patterns.md` | Design patterns and best practices |
| `templates.md` | Ready-to-use templates |
| `advanced.md` | Advanced techniques |
| `troubleshooting.md` | Problem solving guide |
| `examples.md` | Detailed usage examples |

### Naming Convention
- Use lowercase with hyphens: `api-reference.md`
- Be descriptive: `webhook-patterns.md` not `webhooks.md`
- Group related content in subdirectories if needed

## Scripts Directory

### Common Scripts

```bash
# setup.sh - Environment preparation
#!/bin/bash
# Check prerequisites and configure environment

# validate.sh - Validation utility
#!/bin/bash
# Validate inputs, configurations, or outputs

# generate.sh - Code/content generation
#!/bin/bash
# Generate boilerplate or templates
```

### Script Guidelines
- Include shebang line
- Add usage comments at top
- Handle errors gracefully
- Return meaningful exit codes

## Examples Directory

### Purpose
- Provide working, tested samples
- Show realistic usage scenarios
- Include comments explaining key parts

### Structure
```
examples/
├── basic/           # Minimal working example
│   └── config.yaml
├── advanced/        # Complex scenario
│   ├── config.yaml
│   └── scripts/
└── integration/     # Integration examples
    └── with-other-tool/
```

## Progressive Loading

### How It Works
1. Claude reads SKILL.md first (always loaded)
2. References are loaded only when needed
3. Use explicit pointers: "See `references/api.md` for details"

### Best Practices
- Keep SKILL.md self-sufficient for common tasks
- Use references for deep dives and edge cases
- Reference specific files, not just directories
- Include section hints: "See `references/api.md#authentication`"

## Minimal vs Full Structure

### Minimal (Simple Skills)
```
skill-name/
└── SKILL.md
```

### Standard (Most Skills)
```
skill-name/
├── SKILL.md
└── references/
    └── patterns.md
```

### Full (Complex Skills)
```
skill-name/
├── SKILL.md
├── references/
│   ├── api.md
│   ├── patterns.md
│   ├── advanced.md
│   └── troubleshooting.md
├── scripts/
│   └── setup.sh
└── examples/
    └── basic-config.yaml
```

## Symlink Strategy

For global skills managed in a separate repository:

```bash
# Link entire skills directory
ln -s ~/my-repo/skills ~/.claude/skills

# Or link individual skills
ln -s ~/my-repo/skills/my-skill ~/.claude/skills/my-skill
```
