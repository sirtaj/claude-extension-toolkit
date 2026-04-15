# Phase 1: Marketplace support — Context

**Gathered:** 2026-04-16
**Status:** Ready for planning
**Source:** /gsd-discuss-phase (interactive)

<domain>
## Phase Boundary

Close the marketplace-awareness gap in claude-extension-toolkit across three surfaces:

- **Knowledgebase** — corrected marketplace.json reference, version-manifest entries, doc-fetcher URL (URL already present)
- **Tooling** — scaffolder detection + three flows, safe register helper, validator coverage
- **Docs** — marketplace primer, starter-skill integration, install instructions

In-scope outputs are enumerated in `.planning/ROADMAP.md` Phase 1. Out-of-scope: standalone → umbrella promotion (seeded separately), non-local marketplace source types beyond what the canonical schema requires.

</domain>

<decisions>
## Implementation Decisions

### Layouts (from design note — locked)

- Two layouts both supported: **standalone (flat)** and **umbrella (aggregating)**
- Invariant: marketplace.json lives at exactly one level per tree — never both plugin root and umbrella root simultaneously
- No promotion flow in v1 (deferred — see `.planning/seeds/marketplace-promotion-flow.md`)

### Scaffolder behavior (extension-builder)

- **Detection:** upward `pathlib.Path`-walk from CWD for ancestor `.claude-plugin/marketplace.json` (pure stdlib, no subprocess — matches zero-dep convention)
- **Three flows based on detection:**
  - Inside umbrella → register new plugin into existing marketplace.json via `scripts/marketplace_register.py` (safe jq-append style, but implemented in Python stdlib)
  - Greenfield, user picks standalone → scaffold plugin with its own marketplace.json at root
  - Greenfield, user picks umbrella → scaffold umbrella dir + first plugin entry
- **Standalone default: auto-create marketplace.json at plugin root.** Plugin is installable immediately with `/plugin marketplace add <plugin-dir>`. Promotion (future) will delete the inner file when moving into an umbrella.

### extension-starter integration

- extension-starter **surfaces the layout choice** as part of its existing quick-start decision flow, plus a short primer pointing at the new marketplace reference
- extension-starter does NOT perform detection or scaffolding — it hands control to extension-builder with the user's answer captured
- Clean separation: starter = decision framing; builder = execution

### Validator severity (extension-optimizer)

Tiered severity on marketplace.json issues:

**Hard errors (non-zero exit):**
- Malformed JSON
- Missing required top-level fields per canonical schema
- Missing required plugin-entry fields (`name`, `source`)
- Reserved marketplace name collisions (per official reserved-names list)
- Unknown/unsupported source type
- `author` not an object `{name, email}` (schema shape violation)
- `metadata` not an object wrapper (schema shape violation)

**Warnings (zero exit):**
- Missing optional plugin fields (`homepage`, `repository`, `license`, `keywords`, `description`)
- Schema-version drift vs `data/version-manifest.json`
- Unused/unknown metadata keys
- Duplicate plugin names within a marketplace

This keeps validator usable in CI without being noisy for routine dev edits.

### Schema-discrepancy fixes (Wave 0 — prerequisite)

All four discrepancies identified by research are fixed **up front in Wave 0**, before any scaffolder or validator code is written. Downstream tasks write against a corrected spec.

1. Remove `pip` source type from `data/version-manifest.json` (not in official schema)
2. Correct the reserved marketplace names list (7 names wrong — replace with official list)
3. Fix `metadata` shape — the manifest models it as a flat list; must be an `metadata: {}` object wrapper
4. Fix `author` shape in plugin entries — object `{name, email}`, not string. Also correct `references/marketplaces.md` where this is documented wrong

Also add to the manifest plugin entry: `homepage`, `repository`, `license`, `keywords` (documented optional fields currently untracked).

### Pre-existing bug (Wave 0 — fix before extending)

`scripts/plugin_scaffolder.py:68` writes to `.claude/settings.local.json` without ensuring `.claude/` exists. Fix before extending the file (add `parent.mkdir(parents=True, exist_ok=True)`).

### File/tool assignments

- **New file:** `scripts/marketplace_register.py` — upward-search detection + three-flow orchestration + safe JSON append (Python stdlib only)
- **New reference:** `references/marketplace-schema.md` — canonical marketplace.json schema derived from `code.claude.com/docs/en/plugin-marketplaces`
- **Extended:** `scripts/plugin_scaffolder.py`, `scripts/marketplace_manager.py` (both exist per research), `data/version-manifest.json`, `references/marketplaces.md`, `skills/extension-builder/SKILL.md`, `skills/extension-starter/SKILL.md`, `skills/extension-optimizer/SKILL.md`, `README.md`

### Claude's Discretion

- Exact wording of primer docs
- Specific error messages (must be actionable; format at planner's discretion)
- Internal code organization of `marketplace_register.py` (helpers, classes)
- Whether to expose a top-level CLI flag for non-interactive scaffolding (e.g., `--layout standalone`) — planner decides based on symmetry with existing scaffolder flags

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase artifacts
- `.planning/ROADMAP.md` — Phase 1 scope
- `.planning/notes/marketplace-support-design.md` — design decisions from exploration
- `.planning/phases/01-marketplace-support/01-RESEARCH.md` — verified schema + discrepancies + code inventory
- `.planning/seeds/marketplace-promotion-flow.md` — explicitly out-of-scope (don't design for it now)

### Codebase maps
- `.planning/codebase/STACK.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/STRUCTURE.md`

### External (official)
- `https://code.claude.com/docs/en/plugin-marketplaces` — canonical marketplace.json schema (cited in RESEARCH.md; mirror via `scripts/docs_fetcher.py sync`, already in `canonical-sources.json`)

### In-repo files to respect
- `data/version-manifest.json` — single source of truth for schema/deprecations
- `data/canonical-sources.json` — doc-fetcher URL list (already contains `plugin_marketplaces`)
- `scripts/docs_fetcher.py` — self-maintenance loop, don't break its contract
- `scripts/plugin_scaffolder.py` (fix bug + extend), `scripts/marketplace_manager.py` (extend)
- `skills/extension-builder/SKILL.md`, `skills/extension-starter/SKILL.md`, `skills/extension-optimizer/SKILL.md`

</canonical_refs>

<specifics>
## Specific Ideas

- Target runtime: Claude Code v2.1.77 (per plugin.json); marketplace schema version at that revision
- Coding convention throughout: Python 3 stdlib only, system `jq`/`grep`/`find` allowed; script pattern is `SCRIPT_DIR = Path(__file__).parent; TOOLKIT_ROOT = SCRIPT_DIR.parent`
- Install commands documented in primer should use real examples, e.g. `/plugin marketplace add ./my-plugin` and `/plugin install my-plugin@sirtaj-plugins`
- Primer should explicitly state the one-level invariant and point at the seeded promotion flow as the migration path

</specifics>

<deferred>
## Deferred Ideas

- **Standalone → umbrella promotion** (seeded at `.planning/seeds/marketplace-promotion-flow.md`) — trigger when real user hits the case
- **Non-interactive / CI flags for scaffolder** — planner may include if trivial; otherwise defer
- **Marketplace discovery/browse tooling** — out of scope; Claude Code handles discovery
- **Publishing/syndication helpers** (publishing a local marketplace to a remote registry) — not in scope; no current story for it
- **Validation of plugins referenced by marketplace.json** (cross-file validation: does each listed plugin dir actually exist and have a valid plugin.json?) — worth considering in planner if cheap, otherwise defer as follow-up

</deferred>

---

*Phase: 01-marketplace-support*
*Context gathered: 2026-04-16 via /gsd-discuss-phase*
