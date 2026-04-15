# Marketplace-aware Plugin Scaffolding

When creating a plugin, choose the right flow based on where the user is invoking from. Run `scripts/marketplace_register.py` for three-flow orchestration; it handles detection and writes `marketplace.json` correctly for each case.

## Detection: is the user inside an existing umbrella?

`marketplace_register.py` walks upward from `--plugin-path` looking for an ancestor `.claude-plugin/marketplace.json`. If found, it uses the register-into-existing flow automatically.

## Three flows

| Detected state | User choice | Action |
|----------------|-------------|--------|
| Ancestor marketplace found | n/a | Register new plugin entry into the existing marketplace.json (safe JSON append, idempotent) |
| Greenfield | standalone (default) | Scaffold plugin with its own `.claude-plugin/marketplace.json` at the plugin root; immediately installable |
| Greenfield | umbrella | Scaffold umbrella dir + first plugin entry |

## Invocation

**Standalone (default, greenfield):**
```bash
python3 scripts/plugin_scaffolder.py my-plugin \
    --output ./ \
    --author "Author Name" \
    --email "author@example.com"

# Result: ./my-plugin/.claude-plugin/{plugin.json,marketplace.json}
# Install with: /plugin marketplace add ./my-plugin
```

**Umbrella (greenfield, scaffolding a new umbrella and first plugin):**
```bash
python3 scripts/plugin_scaffolder.py my-plugin --output ./my-umbrella --marketplace none

python3 scripts/marketplace_register.py my-plugin \
    --plugin-path ./my-umbrella/my-plugin \
    --layout umbrella \
    --owner "Owner Name" \
    --marketplace-name my-umbrella \
    --umbrella-path ./my-umbrella
```

**Register into existing umbrella (detection):**
```bash
python3 scripts/plugin_scaffolder.py new-plugin --output . --marketplace none

python3 scripts/marketplace_register.py new-plugin \
    --plugin-path ./new-plugin \
    --layout auto \
    --owner "Owner Name"
```

## Safety guarantees

- Reserved marketplace names (per `data/version-manifest.json` `schemas.marketplace_manifest.reserved_names`) are rejected before any file is written.
- Plugin paths containing `../` or outside the marketplace root are rejected with a clear error.
- Duplicate plugin names within a marketplace raise `Plugin '<name>' already registered`.
- The one-level invariant is preserved: standalone writes `marketplace.json` at plugin root; register-into-existing writes nothing new at plugin root.

## Further references

- Schema: [`../../../references/marketplace-schema.md`](../../../references/marketplace-schema.md)
- CLI / auth / caching: [`../../../references/marketplaces.md`](../../../references/marketplaces.md)
- Validator: `scripts/marketplace_manager.py validate <marketplace-root>` (see `extension-optimizer` skill)
