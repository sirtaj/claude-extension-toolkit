# Research Questions

## Open

### Q1: Canonical marketplace.json schema (2026-04-16)

**Question:** What is the canonical schema for Claude Code's `marketplace.json`, and where is it officially documented?

**Needed for:** Marketplace support phase — feeds `references/marketplace-schema.md`, `data/version-manifest.json` entry, and the URL added to `scripts/docs_fetcher.py sync`.

**Must resolve before tooling work starts.** Without the authoritative schema, `extension-builder` scaffolding and the validator's marketplace.json checks are guesses.

**Sub-questions:**
- Required vs optional top-level fields
- Plugin entry shape (name, source, version, description, categories?)
- Source types supported (local path, git, http?) and their fields
- How versioning/compatibility with Claude Code releases is expressed
- Schema evolution history — are there deprecated fields to track in version-manifest?
