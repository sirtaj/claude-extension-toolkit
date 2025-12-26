---
name: extension-audit
description: This skill should be used when the user asks to "audit extensions", "check my extensions", "review my Claude setup", "analyze extensions", "optimize extensions", "extension health check", "what extensions do I have", "are my extensions working", "fix my extensions", "clean up extensions", or needs help analyzing, validating, and improving Claude Code extensions (skills, agents, commands, hooks, plugins, CLAUDE.md).
---

# Claude Code Extension Audit

Analyze and improve all Claude Code extension types through updates, reorganization, and token optimization.

## Optimization Modes

| Mode | Focus | Use When |
|------|-------|----------|
| **Update** | Add new information | APIs changed, best practices evolved |
| **Reorganize** | Improve structure | Poor progressive disclosure, unclear flow |
| **Refactor** | Reduce tokens | Verbose prose, redundant sections |

## Invocation

| Command | Scope |
|---------|-------|
| `/extension-audit` | Audit all extensions |
| `/extension-audit [name]` | Single extension by name |
| `/extension-audit --skills` | Skills only |
| `/extension-audit --agents` | Agents only |
| `/extension-audit --commands` | Commands only |
| `/extension-audit --hooks` | Hooks only |
| `/extension-audit --plugins` | Plugins only |
| `/extension-audit --claude-md` | CLAUDE.md files only |
| `/extension-audit --validate` | Validation check only |
| `/extension-audit --tokens` | Token analysis only |

## Workflow

### Phase 1: Discovery

| Extension | Discovery Pattern |
|-----------|-------------------|
| Skills | `~/.claude/skills/**/SKILL.md` |
| Agents | `~/.claude/agents/*.md` |
| Commands | `~/.claude/commands/*.md` |
| Hooks | `~/.claude/settings.json` → `hooks` key |
| Plugins | `~/.claude/plugins/*/.claude-plugin/plugin.json` |
| CLAUDE.md | `~/.claude/CLAUDE.md`, project CLAUDE.md files |

**For each extension**:
1. Measure tokens (~chars/4)
2. Classify by type (see Extension Types below)
3. Present inventory table grouped by extension type

### Phase 2: Analysis

**Common checks** (all extensions):
- Token efficiency: prose→tables, verbose examples, redundant sections
- Structure clarity and section hierarchy
- Currency: API versions, documentation links

**Extension-specific checks**:

| Extension | Key Checks |
|-----------|------------|
| Skills | Size (500-1500 words), progressive disclosure (references/), persona voice |
| Agents | Size (800-2000 words), triggering examples, tool access, model selection |
| Commands | Conciseness, clear purpose, placeholder usage `{}`, frontmatter |
| Hooks | Event type validity, command safety, timeout values, matcher patterns |
| Plugins | plugin.json validity, bundled extensions coherence, dependency check |
| CLAUDE.md | Project relevance, no stale rules, clear structure |

See `references/analysis-checklist.md` for detailed criteria.

### Phase 3: Proposal
Present findings per extension:
```
## [Extension Type]: [name] ([subtype])
Current: ~XXXX tokens | Target: ~XXXX tokens (-XX%)

### Change 1 of N: [Title]
**Reason**: [Why this improves the extension]
**Before**: [excerpt]
**After**: [proposed]

Approve? [y]es / [n]o / [m]odify / [s]kip
```

### Phase 4: Approval
**CRITICAL**: Never edit without explicit approval.
- Present each change individually
- Wait for user response
- Track approved changes

### Phase 5: Execution
Apply approved edits via Edit tool. Verify each modification.

## Extension Types

### Skills
| Subtype | Examples | Characteristics |
|---------|----------|-----------------|
| Persona | finance-advisor, health-coach | User context, domain expertise |
| Technical | home-assistant, plasma-dev | API reference, progressive disclosure |
| Meta | create-skill, create-command, create-agent | Claude Code documentation |
| Utility | file-organizer, code-cleanup | Operational workflows |

### Agents
| Subtype | Examples | Characteristics |
|---------|----------|-----------------|
| Domain-Specialist | game-modder, python-debugger | Deep expertise, detailed prompts |
| Task-Runner | test-developer, file-organizer | Operational workflows |
| Collector | wiki-scraper, data-aggregator | Web scraping, data aggregation |

### Commands
| Subtype | Examples | Characteristics |
|---------|----------|-----------------|
| Text Transform | eli5, summarize, fix-grammar | Input `{}` placeholder, single output |
| Action | commit, review-pr | Multi-step execution |

### Hooks
| Event | Purpose |
|-------|---------|
| Notification | Desktop alerts (permission_prompt, idle_prompt) |
| Stop | Task completion actions |
| PreToolUse/PostToolUse | Tool interception |
| SessionStart | Environment setup |

### Plugins
| Component | Purpose |
|-----------|---------|
| plugin.json | Metadata, dependencies |
| commands/ | Bundled commands |
| skills/ | Bundled skills |
| agents/ | Bundled agents |
| hooks/ | Bundled hooks |

### CLAUDE.md
| Scope | Location |
|-------|----------|
| Global | `~/.claude/CLAUDE.md` |
| Project | `<project>/CLAUDE.md` |
| Nested | `<project>/src/CLAUDE.md` |

## Hybrid Approach

Consider using a **hybrid approach** for extension maintenance:

| Component | Purpose | Trigger |
|-----------|---------|---------|
| Health check agent | Quick scan, report issues only | Proactive (session start, periodic) |
| `/extension-audit` skill | Deep analysis with approval gates | Manual invocation |

A health check agent can run automatically and flag issues. For detailed analysis and fixes, invoke this skill manually.

## Python Utility Scripts

The toolkit includes Python scripts in `scripts/` to assist with analysis:

| Script | Purpose | Usage |
|--------|---------|-------|
| `validate_extension.py` | Validate frontmatter and structure | `python scripts/validate_extension.py --all` |
| `token_counter.py` | Estimate token usage with breakdown | `python scripts/token_counter.py --all --verbose` |
| `lint_references.py` | Check for broken internal links | `python scripts/lint_references.py --all` |
| `extension_report.py` | Generate comprehensive report | `python scripts/extension_report.py` |
| `sync_symlinks.py` | Manage AI/ → ~/.claude/ symlinks | `python scripts/sync_symlinks.py --check` |

### Script Integration

During **Phase 1 (Discovery)**, run:
```bash
cd ~/.claude/plugins/claude-extension-toolkit
python scripts/extension_report.py --json
```

During **Phase 2 (Analysis)**, run:
```bash
python scripts/validate_extension.py --all --json
python scripts/token_counter.py --all --top 10
python scripts/lint_references.py --all
```

All scripts output JSON with `--json` flag for programmatic use.

## References

| File | Contents |
|------|----------|
| `references/analysis-checklist.md` | Evaluation criteria for all extension types |
| `references/optimization-patterns.md` | Token reduction transforms |
| `references/extension-type-strategies.md` | Per-type optimization approaches |
