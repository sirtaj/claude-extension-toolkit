# Codebase Structure

**Analysis Date:** 2026-04-16

## Directory Layout

```
claude-extension-toolkit/
├── .claude-plugin/
│   └── plugin.json                    # Plugin manifest (name, version 3.0.0, author)
├── .claude/                           # Local Claude Code settings for plugin dev (gitignored contents)
├── .planning/
│   └── codebase/                      # GSD codebase-mapping docs (this folder)
├── .beads/                            # Beads task-tracker state (untracked)
├── .git                               # gitlink file — this repo is a submodule
├── .gitignore
├── LICENSE                            # MIT
├── README.md                          # Toolkit overview + install + script reference
│
├── skills/                            # User-facing skills (5)
│   ├── extension-starter/SKILL.md     # Decision tree + quick templates (123 lines)
│   ├── extension-builder/
│   │   ├── SKILL.md                   # Create skills/agents/plugins (250 lines)
│   │   └── examples/
│   │       └── code-reviewer.md       # Worked agent example
│   ├── extension-rules/SKILL.md       # CLAUDE.md, hooks, settings (268 lines)
│   ├── extension-optimizer/
│   │   ├── SKILL.md                   # Validate/audit/upgrade (181 lines)
│   │   └── references/
│   │       ├── migrations.md          # Before/after upgrade recipes
│   │       └── checklist.md           # Audit checklist
│   └── extension-sync/SKILL.md        # Doc sync + version manifest (180 lines)
│
├── references/                        # Shared markdown, consumed by multiple skills
│   ├── frontmatter.md                 # All frontmatter fields (260 lines)
│   ├── templates.md                   # Ready-to-use extension templates (429 lines)
│   ├── locations.md                   # Storage locations / priority order (111 lines)
│   ├── tools.md                       # Tool restrictions + permission patterns (226 lines)
│   ├── hooks.md                       # Hook events, schemas, exit codes (464 lines)
│   ├── marketplaces.md                # Marketplace schema + CLI (232 lines)
│   └── schema-definitions.md          # AUTO-GENERATED from data/version-manifest.json (148 lines)
│
├── data/                              # Machine-readable knowledge base
│   ├── version-manifest.json          # Schemas, deprecations, valid values (mutated by sync)
│   ├── canonical-sources.json         # Doc URLs + sync policy
│   └── cache/
│       ├── <id>.txt                   # Fetched doc body (8 sources)
│       └── <id>.meta.json             # Fetch metadata per source
│
└── scripts/                           # CLI utilities (Python stdlib + 1 Bash)
    ├── validate_extension.py          # Frontmatter/structure validator (544 lines)
    ├── extension_report.py            # Inventory ~/.claude extensions (470 lines)
    ├── lint_references.py             # Broken-link checker (343 lines)
    ├── marketplace_manager.py         # Marketplace.json helpers (318 lines)
    ├── docs_fetcher.py                # Canonical doc sync (288 lines)
    ├── pattern_detector.py            # Deprecated-pattern scanner (245 lines)
    ├── token_counter.py               # chars/4 token estimator (355 lines)
    ├── plugin_scaffolder.py           # New-plugin generator (197 lines)
    └── quick_update_check.sh          # SessionStart hook helper (63 lines, Bash)
```

## Directory Purposes

**`.claude-plugin/`:**
- Purpose: Plugin discovery by Claude Code
- Contains: `plugin.json` only
- Key files: `plugin.json` (name, version, author, keywords)

**`skills/`:**
- Purpose: Workflow-based user-facing skills auto-invoked by description match
- Contains: One subdirectory per skill, each with a mandatory `SKILL.md`
- Optional per-skill subdirs: `references/` (skill-private progressive disclosure), `examples/` (worked examples)
- Naming: `extension-<verb>` (starter, builder, rules, optimizer, sync)

**`references/`:**
- Purpose: Shared reference material consumed by multiple skills
- Contains: Flat `.md` files; no subdirectories
- Special: `schema-definitions.md` is regenerated from `data/version-manifest.json` by the sync script — do not hand-edit

**`data/`:**
- Purpose: Single source of truth for Claude Code schema facts and canonical doc URLs
- Contains: Two root JSON files + a `cache/` subdir
- Generated: `cache/*` is generated; `version-manifest.json`'s `last_docs_sync` is mutated by sync
- Committed: Yes (including cache, for offline availability)

**`scripts/`:**
- Purpose: Stateless CLI utilities; no package, no `__init__.py`
- Contains: Flat directory of executable Python 3 scripts + one Bash hook helper
- Convention: Each script discovers paths via `SCRIPT_DIR = Path(__file__).parent; TOOLKIT_ROOT = SCRIPT_DIR.parent`
- Entry: All use `if __name__ == "__main__"` with `argparse`

**`.planning/`:**
- Purpose: GSD (Get Shit Done) planning artifacts — codebase maps, phase plans
- Generated: Yes, by `/gsd-*` commands
- Committed: Typically yes

**`.beads/`:**
- Purpose: Beads task tracker database
- Committed: No (in `.gitignore`)

## Key File Locations

**Entry points:**
- `.claude-plugin/plugin.json` — plugin identity for Claude Code
- `skills/<name>/SKILL.md` — user-visible invocation targets
- `scripts/*.py` / `scripts/*.sh` — CLI entry points

**Configuration:**
- `data/version-manifest.json` — schema + deprecation configuration
- `data/canonical-sources.json` — doc-sync configuration

**Core logic:**
- `scripts/validate_extension.py` — structural validation
- `scripts/docs_fetcher.py` — self-maintenance loop
- `scripts/pattern_detector.py` — deprecation scanning

**Authoritative reference content:**
- `references/frontmatter.md`, `references/hooks.md`, `references/templates.md`

## Naming Conventions

**Files:**
- Python scripts: `snake_case.py` (e.g., `validate_extension.py`, `pattern_detector.py`)
- Shell scripts: `snake_case.sh` (e.g., `quick_update_check.sh`)
- Markdown references: `lowercase.md` (single word or hyphenated: `frontmatter.md`, `schema-definitions.md`)
- Skills: mandatory file name `SKILL.md` (uppercase)
- JSON data: `kebab-case.json` (e.g., `version-manifest.json`, `canonical-sources.json`)

**Directories:**
- Skill directories: `extension-<verb>` kebab-case, matches skill `name` frontmatter
- Cache entries: `<source_id>.txt` + `<source_id>.meta.json` where `<source_id>` matches `canonical-sources.json` `sources[].id` (snake_case)

**Planning docs:**
- `.planning/codebase/*.md` — UPPERCASE filenames (STACK.md, ARCHITECTURE.md, etc.)

## Where to Add New Code

**New skill:**
- Primary: `skills/<new-name>/SKILL.md` with frontmatter (name, description)
- Supporting content: `skills/<new-name>/references/*.md` (skill-private) or extend shared `references/` if cross-skill
- Examples: `skills/<new-name>/examples/*.md`

**New utility script:**
- Location: `scripts/<verb_noun>.py`
- Template: stdlib-only imports; `SCRIPT_DIR = Path(__file__).parent; TOOLKIT_ROOT = SCRIPT_DIR.parent`; `argparse`-based CLI with exit codes 0/1/2
- Make executable: `chmod +x`; shebang `#!/usr/bin/env python3`

**New shared reference:**
- Location: `references/<topic>.md`
- Update: README.md "Shared References" table and relevant skills that should surface it

**New canonical doc source:**
- Edit: `data/canonical-sources.json` `sources[]` (add `id`, `url`, `purpose`, `extract`)
- Run: `scripts/docs_fetcher.py sync` to populate `data/cache/<id>.{txt,meta.json}`

**New schema fact / deprecation:**
- Edit: `data/version-manifest.json` (`schemas.*` or `deprecations[]`)
- No code change needed — validators and pattern detector read from manifest

**New hook script:**
- Location: `scripts/<name>.sh` (Bash) or `scripts/<name>.py`
- Hook contract: read JSON from stdin; write status to stdout; exit 0 normally

## Special Directories

**`data/cache/`:**
- Purpose: Offline copy of fetched canonical documentation
- Generated: Yes (by `scripts/docs_fetcher.py sync`)
- Committed: Yes (intentional — guarantees offline operation; refreshed every 7 days per policy)

**`.beads/`:**
- Purpose: Beads task tracker internal state
- Generated: Yes
- Committed: No

**`.claude/`:**
- Purpose: Per-project Claude Code settings for developing the toolkit itself
- Committed: Directory present; contents per `.gitignore`

**`.planning/`:**
- Purpose: GSD planning artifacts
- Generated: Yes (by `/gsd-*` commands)
- Committed: Yes

---

*Structure analysis: 2026-04-16*
