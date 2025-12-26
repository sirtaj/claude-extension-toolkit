# Optimization Patterns

## Prose to Table (40-60% savings)

```markdown
# Before
Use Glob for files, Grep for content, Read for viewing.

# After
| Need | Tool |
|------|------|
| Find files | Glob |
| Search content | Grep |
| View file | Read |
```

## Step Consolidation (50-70% savings)

```markdown
# Before
### Step 1: Check Config
First, read the configuration file...
### Step 2: Search Files
Next, search for related files...

# After
1. Read config file
2. Search related files
```

## Qualifier Removal (30-50% savings)

| Remove | Keep |
|--------|------|
| "You should consider using" | "Use" |
| "It is important to note" | (delete) |
| "In order to" | "To" |
| "Prior to doing X" | "Before X" |

## Example Trimming (60-80% savings)

**Keep**: Essential demos, non-obvious patterns, input/output pairs

**Remove**: Commentary, multiple similar examples, meta-explanation

## Progressive Disclosure (70-90% savings from SKILL.md)

| SKILL.md | references/ |
|----------|-------------|
| Core workflow (5-10 steps) | Detailed patterns |
| Quick reference tables | Exhaustive lists |
| Key principles (3-5) | Advanced techniques |

## Redundancy Elimination

Merge "Always/Never" sections into workflow steps. Delete repeated content.
