# Marketplace Audit

When auditing a plugin or marketplace directory, validate its `marketplace.json` using the tiered-severity checker.

## Run

```bash
python3 scripts/marketplace_manager.py validate <marketplace-root> --json
```

Output shape:
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Plugin 'x' missing optional field 'homepage'", "..."]
}
```

## Severity tiers

| Tier | Examples | Exit | Action |
|------|----------|------|--------|
| **Error** (exit 1) | Malformed JSON; missing required top-level fields; missing plugin-entry `name`/`source`; reserved name collision; unknown source type; `author` not `{name, email}` object; `metadata` not an object wrapper; source path outside marketplace root | blocks | Fix before shipping — plugin won't install |
| **Warning** (exit 0) | Missing optional `homepage`/`repository`/`license`/`keywords`/`description`; legacy `path` field; unknown metadata keys; duplicate plugin names within marketplace; schema drift | guides | Address when polishing; not install-blocking |

## Interpreting output

- `valid: true` with warnings: plugin installs; warnings are polish tasks (metadata completeness, duplicate-name hygiene).
- `valid: false`: do not ship. Each error maps to a concrete fix — see `../../../references/marketplace-schema.md` for the correct shape.
- Reserved name errors: pick a different marketplace name. The authoritative reserved list is in `data/version-manifest.json` `schemas.marketplace_manifest.reserved_names`.
- `author` shape errors: convert string authors to object `{name, email?}`.
- `metadata` shape errors: wrap flat top-level `description`/`version`/`pluginRoot` into `metadata: {...}`.

## Built-in validator (complementary)

Run Claude Code's built-in validator as well for syntax-level checks:
```bash
claude plugin validate <marketplace-root>
```

The toolkit's `marketplace_manager.py` handles semantic checks the built-in doesn't (reserved names, path-exists, author/metadata shape).

Reference: [`../../../references/marketplace-schema.md`](../../../references/marketplace-schema.md)
