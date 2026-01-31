# Extension Audit Checklist

Complete checklist for validating Claude Code extensions.

## Skills Checklist

### Structure
- [ ] Located in `skills/<name>/SKILL.md`
- [ ] Has valid YAML frontmatter
- [ ] `name` field present and matches directory
- [ ] `description` field present

### Description Quality
- [ ] Written in third person ("Handles X" not "I help with X")
- [ ] Includes trigger phrases ("when the user asks to...")
- [ ] Specific, not generic
- [ ] Under 500 characters

### Content
- [ ] Core content under 1500 tokens
- [ ] Uses progressive disclosure (references/ for details)
- [ ] Has clear workflow or quick reference
- [ ] Links to references are valid

### References (if present)
- [ ] References/ directory exists
- [ ] Each .md file is linked from SKILL.md
- [ ] No orphaned reference files
- [ ] No nested references (one level only)

## Agents Checklist

### Structure
- [ ] Located in `agents/<name>.md`
- [ ] Has valid YAML frontmatter
- [ ] `name` field present
- [ ] `description` field present

### Description Quality
- [ ] Contains `<example>` blocks (2-3 recommended)
- [ ] Examples show when to use agent
- [ ] Clear purpose statement

### Tool Restrictions
- [ ] `tools` or `disallowedTools` specified
- [ ] Minimum necessary permissions
- [ ] No unnecessary access (Bash, Write, etc.)

### Content
- [ ] Clear objectives
- [ ] Defined constraints
- [ ] Workflow or approach section
- [ ] Under 2000 tokens

## Commands Checklist

### Structure
- [ ] Located in `commands/<name>.md`
- [ ] Filename matches command name
- [ ] Under 200 tokens

### Frontmatter (optional but recommended)
- [ ] `description` for /help
- [ ] `argument-hint` if takes args
- [ ] Tool restrictions if needed

### Content
- [ ] Clear, focused instructions
- [ ] Single purpose
- [ ] Concise

## Hooks Checklist

### Configuration
- [ ] Valid JSON syntax
- [ ] Valid event names
- [ ] Matcher patterns valid (for PreToolUse, etc.)

### Scripts
- [ ] Parse JSON from stdin (not env vars)
- [ ] Handle missing fields gracefully
- [ ] Use proper exit codes (0=allow, 2=block)
- [ ] Have timeouts set
- [ ] Portable paths (use `${CLAUDE_PLUGIN_ROOT}`)

### Best Practices
- [ ] Fast execution (<5 seconds)
- [ ] Default to allow
- [ ] Clear block messages
- [ ] Error handling (`|| true` where appropriate)

## Plugins Checklist

### Structure
- [ ] Has `.claude-plugin/plugin.json`
- [ ] `name` field in manifest
- [ ] `description` field in manifest
- [ ] `version` field recommended

### Directories
- [ ] No empty skill/command/agent directories
- [ ] All referenced files exist
- [ ] README.md present

### Development
- [ ] settings.local.json for permissions
- [ ] Works with `--plugin-dir`
- [ ] Tested before distribution

### Marketplace
- [ ] Registered in marketplace.json
- [ ] Path matches actual location
- [ ] Version consistent

## CLAUDE.md Checklist

### Content
- [ ] Under 2000 tokens
- [ ] No stale rules
- [ ] Focused on what Claude needs
- [ ] Updated when project changes

### Format
- [ ] Clear sections
- [ ] Actionable instructions
- [ ] Project-specific, not generic

## Deprecated Patterns

Check for these issues:

- [ ] No `$TOOL_INPUT`, `$TOOL_OUTPUT`, `$TOOL_NAME` in scripts
- [ ] No `decision: block` in hook outputs
- [ ] No `docs.anthropic.com` URLs (use `code.claude.com`)
- [ ] No hardcoded absolute paths in plugins
- [ ] No first-person descriptions in skills

## Token Budgets

Verify extensions are within budget:

| Type | Target | Max |
|------|--------|-----|
| Command | 50-150 | 200 |
| Skill (SKILL.md) | 500-1000 | 1500 |
| Skill (with refs) | 800-1500 | 3000 |
| Agent | 800-1500 | 2000 |
| CLAUDE.md | 500-1000 | 2000 |

## Running the Checks

```bash
cd ~/.claude/plugins/claude-extension-toolkit

# Full validation
python scripts/validate_extension.py --all

# Deprecated patterns
python scripts/pattern_detector.py --all

# Token audit
python scripts/token_counter.py --all --top 10

# Reference links
python scripts/lint_references.py --all
```
