# Roadmap

## Milestone: current

### Phase 1: Marketplace support

**Goal:** Close the marketplace-awareness gap across the toolkit's three surfaces so users can scaffold, validate, and consume toolkit-built extensions via local Claude Code marketplaces without hand-wiring config.

**Plans:** 5 plans

Plans:
- [ ] 01-01-schema-corrections-PLAN.md — Wave 0 prerequisite: fix 4 schema discrepancies in data/version-manifest.json, correct references/marketplaces.md author type, fix plugin_scaffolder.py mkdir bug
- [ ] 01-02-knowledgebase-docs-PLAN.md — Create references/marketplace-schema.md (canonical schema + two-layout explanation) and add Marketplace Support primer to README.md
- [ ] 01-03-scaffolder-three-flows-PLAN.md — New scripts/marketplace_register.py (upward-search detection + three flows) and extend plugin_scaffolder.py with --marketplace standalone default
- [ ] 01-04-validator-tiered-severity-PLAN.md — Extend scripts/marketplace_manager.py with tiered-severity validation (errors vs warnings), reserved-name check, author/metadata shape check
- [ ] 01-05-skill-integration-PLAN.md — Wire starter (decision framing), builder (three-flow execution), optimizer (tiered audit) skills to the new tooling

**Scope:**

- **Knowledgebase**
  - Add `references/marketplace-schema.md` documenting marketplace.json structure
  - Extend `data/version-manifest.json` with marketplace schema version + deprecations
  - Add canonical marketplace docs URL to `scripts/docs_fetcher.py sync` list

- **Tooling**
  - `extension-builder`: upward-search detection of ancestor marketplace.json
  - Three scaffolder flows: standalone (flat), new umbrella, register-into-existing
  - New `scripts/marketplace_register.py` helper for safe jq-append into an existing marketplace.json
  - `extension-optimizer` validator extended to check marketplace.json shape

- **Docs**
  - Marketplace primer in README (standalone vs umbrella patterns, when to pick which)
  - `extension-starter` skill surfaces the layout choice upfront
  - Install instructions use `/plugin marketplace add <path>` examples for both layouts

**Out of scope (v1):**
- Standalone → umbrella promotion/migration (seeded separately)
- Non-local marketplace types (git, http) unless the canonical schema requires them

**Depends on:** Research Q1 (canonical marketplace.json schema) resolved before implementation.

**Design reference:** `.planning/notes/marketplace-support-design.md`
