# Architecture

**Analysis Date:** 2026-04-16

## Pattern Overview

**Overall:** Content-first Claude Code plugin with a supporting Python script layer. The toolkit is primarily **declarative markdown** (skills + shared references) augmented by **imperative stdlib-Python utilities** (validators, scaffolders, doc sync). A small JSON "knowledge base" under `data/` is the single source of truth for Claude Code schema facts.

**Key Characteristics:**
- Zero runtime dependencies (Python stdlib + system `jq`/`grep`/`find`)
- Self-describing: schemas for validation are read from `data/version-manifest.json`, not hard-coded
- Self-maintaining: `scripts/docs_fetcher.py` refreshes the canonical-doc cache and the manifest on demand
- Skills communicate with users; scripts communicate with files. No inter-process coordination.

## Layers

**Plugin manifest layer:**
- Location: `.claude-plugin/plugin.json`
- Purpose: Identifies the plugin to Claude Code (name, version, author). No `commands`/`skills`/`hooks` sub-manifests — Claude Code discovers them by directory convention.

**Skill layer (primary user-facing surface):**
- Location: `skills/extension-*/SKILL.md` (5 skills)
- Purpose: Workflow guidance invoked by Claude when user triggers match skill description
- Depends on: `references/*.md` (shared content), `scripts/*.py` (invoked by some skills)
- Used by: Claude Code host at session time

**Shared reference layer:**
- Location: `references/*.md` (7 files, ~1900 lines)
- Purpose: De-duplicated canonical facts consumed by multiple skills (frontmatter fields, templates, hooks reference, marketplace schema, tool permissions, storage locations). `references/schema-definitions.md` is auto-updated by sync.
- Depends on: `data/version-manifest.json` (source of truth for schemas)

**Data / knowledge-base layer:**
- Location: `data/`
- Files:
  - `version-manifest.json` — schemas, deprecations, valid values; mutated by sync
  - `canonical-sources.json` — URLs + sync policy
  - `cache/*.{txt,meta.json}` — fetched documentation bodies & metadata
- Purpose: Machine-readable facts consumed by scripts and `schema-definitions.md` regeneration

**Script / tooling layer:**
- Location: `scripts/` (9 files — 8 Python, 1 Bash)
- Purpose: Stateless CLIs for validation, pattern detection, token estimation, doc sync, scaffolding, marketplace management, extension inventory, reference linting
- Depends on: `data/` (schemas, sources), `~/.claude/` (for `--all` inventory scans)
- Common root discovery: every script uses `SCRIPT_DIR = Path(__file__).parent; TOOLKIT_ROOT = SCRIPT_DIR.parent`

## Data Flow

**Skill invocation (user → Claude → skill → references):**
1. User types a trigger phrase matching a skill's `description`
2. Claude Code loads matching `SKILL.md` from `skills/<name>/`
3. Skill body directs Claude to read specific `references/*.md` files progressively
4. Skill may instruct Claude to run a `scripts/*.py` tool with specific args

**Doc sync (`/extension-sync` → `docs_fetcher.py sync`):**
1. Script reads `data/canonical-sources.json` for URL list + sync policy
2. For each source, HTTPS GET via `urllib.request` (timeout 30s, 3 retries)
3. Writes body → `data/cache/<id>.txt`, metadata → `data/cache/<id>.meta.json`
4. Updates `data/version-manifest.json` `last_docs_sync`
5. `references/schema-definitions.md` is regenerated from manifest

**Validation (`validate_extension.py <path>`):**
1. Load `data/version-manifest.json` → `_SCHEMAS`
2. For each extension type (skills/agents/commands/plugins), pick required + optional frontmatter lists from manifest (fallback to inline defaults)
3. Parse markdown frontmatter / JSON manifest
4. Emit per-field errors/warnings; exit 0/1/2

**SessionStart hook flow (`quick_update_check.sh`):**
1. Claude Code invokes hook, passes JSON event on stdin (discarded via `cat > /dev/null`)
2. Reads `data/version-manifest.json` via `jq` for `last_docs_sync`
3. Computes age in days via inline `python3 -c`
4. Scans `~/.claude/**/*.sh` modified in last 24h for deprecated env-var patterns (`$TOOL_INPUT` etc.)
5. Emits `[extension-toolkit] ...` lines on stdout if stale or deprecated patterns found

**State Management:**
- All state is on disk. No in-memory coordination between scripts.
- `data/version-manifest.json` is the only mutable file in the repo at runtime (written by doc sync).

## Key Abstractions

**Extension type:**
- Represented in `scripts/validate_extension.py` `EXTENSION_TYPES` dict (skills, agents, commands, plugins)
- Each type has a glob pattern and required/optional frontmatter lists sourced from manifest

**Schema:**
- JSON subtree under `data/version-manifest.json` `schemas.<type>`
- Consumed by: `validate_extension.py`, `pattern_detector.py` (for deprecations), regeneration of `references/schema-definitions.md`

**Deprecation:**
- JSON object under `data/version-manifest.json` `deprecations[]` with fields `pattern`, `replacement`, `since`, `severity`
- Consumed by: `scripts/pattern_detector.py` (regex match on file content), `scripts/quick_update_check.sh` (grep for a hard-coded subset)

**Canonical source:**
- JSON object under `data/canonical-sources.json` `sources[]` with `id`, `url`, `purpose`, `extract[]`
- One-to-one with files under `data/cache/<id>.txt`

## Entry Points

**For users (via Claude Code):**
- Skill triggers — `/extension-starter`, `/extension-builder`, `/extension-rules`, `/extension-optimizer`, `/extension-sync`

**For scripts (CLI):**
- `scripts/validate_extension.py <path> | --all | --type <t> | --schema`
- `scripts/pattern_detector.py <path>`
- `scripts/token_counter.py <path> [--verbose]`
- `scripts/docs_fetcher.py {sync|check|show <id>}`
- `scripts/marketplace_manager.py {list|...} <marketplace-path>`
- `scripts/plugin_scaffolder.py <name> [--output <dir>]`
- `scripts/extension_report.py`
- `scripts/lint_references.py`

**For Claude Code hooks:**
- `scripts/quick_update_check.sh` — SessionStart handler

## Error Handling

**Strategy:** Unix exit codes + human-readable stderr. Python scripts use `argparse` for usage errors (exit 2), return 0 on success, 1 on validation/operation errors.

**Patterns:**
- `docs_fetcher.py` — `urllib.error` caught, retried up to `retry_count` with `timeout_seconds`
- `quick_update_check.sh` — `set -euo pipefail` but graceful fallbacks (`2>/dev/null`, `// empty` in jq) so hook never fails the session
- Schemas fall back to in-code defaults if `version-manifest.json` missing (see `validate_extension.py` load_schemas)

## Cross-Cutting Concerns

**Logging:** Plain stdout/stderr; no logging framework.

**Validation:** Centralized in `scripts/validate_extension.py`, driven by JSON schemas.

**Authentication:** None.

## Extension Points

- **Add a skill:** Create `skills/<name>/SKILL.md` with frontmatter. Optional subdirs `examples/`, `references/` for progressive disclosure (see `skills/extension-optimizer/references/`, `skills/extension-builder/examples/`).
- **Add a script:** Drop `scripts/<name>.py` using the `SCRIPT_DIR / TOOLKIT_ROOT` convention and stdlib only. Make executable.
- **Track new schema fact:** Edit `data/version-manifest.json`; validators and `references/schema-definitions.md` pick it up.
- **Track new canonical doc:** Add entry to `data/canonical-sources.json` `sources[]`; next `docs_fetcher.py sync` caches it.
- **Add a deprecation:** Append to `data/version-manifest.json` `deprecations[]`; `pattern_detector.py` picks it up automatically.

---

*Architecture analysis: 2026-04-16*
