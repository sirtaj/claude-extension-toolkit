---
phase: 01-marketplace-support
plan: 04
type: execute
wave: 2
depends_on: [01]
files_modified:
  - scripts/marketplace_manager.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "marketplace_manager.py validate reports tiered severity: hard errors (exit 1) vs warnings (exit 0)"
    - "Malformed JSON, missing required fields, missing plugin-entry name/source, reserved name collisions, unknown source types, wrong author shape, wrong metadata shape → hard errors"
    - "Missing optional fields (homepage, repository, license, keywords, description), schema-version drift, unknown metadata keys, duplicate plugin names → warnings"
    - "Validator reads reserved names and schema facts from data/version-manifest.json (single source of truth)"
    - "JSON output mode (--json) preserves severity tier info"
  artifacts:
    - path: "scripts/marketplace_manager.py"
      provides: "Extended validator with tiered severity, reserved-name check, author/metadata shape check, optional-field warnings"
      contains: "def _load_schema, reserved_names check, author object check, metadata object check, duplicate-name warning"
  key_links:
    - from: "scripts/marketplace_manager.py"
      to: "data/version-manifest.json"
      via: "reads schemas.marketplace_manifest.reserved_names, metadata_fields; schemas.marketplace_plugin_entry.optional, field_types.author, source_types"
      pattern: "version-manifest"
---

<objective>
Extend `scripts/marketplace_manager.py validate` with tiered-severity validation. Hard errors fail CI (exit 1); warnings surface guidance without blocking (exit 0). All schema facts come from `data/version-manifest.json` (corrected by Plan 01) — no hardcoded lists.

Purpose: Make the validator usable in CI without being noisy. Today it returns a flat errors list. Users need to distinguish "this won't install" from "you forgot a nice-to-have".

Output: Extended `scripts/marketplace_manager.py` with `validate_marketplace` returning `(errors, warnings)` instead of `(ok, errors)`, and CLI surfacing both with tiered severity.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/phases/01-marketplace-support/01-CONTEXT.md
@.planning/phases/01-marketplace-support/01-RESEARCH.md
@.planning/phases/01-marketplace-support/01-01-SUMMARY.md
@scripts/marketplace_manager.py
@data/version-manifest.json
</context>

<interfaces>
Current contract of validate_marketplace (from marketplace_manager.py):
```python
def validate_marketplace(marketplace_path: Path) -> Tuple[bool, List[str]]:
    # returns (is_valid, errors)
```

New contract (this plan changes):
```python
def validate_marketplace(marketplace_path: Path) -> Tuple[List[str], List[str]]:
    # returns (errors, warnings)
```

Callers to update: `main()` in the same file. No other file imports `validate_marketplace` (grep confirms). No downstream consumer breakage.
</interfaces>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Extend marketplace_manager.py with tiered-severity validation</name>
  <files>scripts/marketplace_manager.py</files>
  <read_first>
    - scripts/marketplace_manager.py (entire file, 319 lines — current validate_marketplace is lines 39-109)
    - data/version-manifest.json (read schemas.marketplace_manifest and schemas.marketplace_plugin_entry after Plan 01 corrections)
    - .planning/phases/01-marketplace-support/01-CONTEXT.md (Validator severity section — the authoritative hard-error / warning tier lists)
    - .planning/phases/01-marketplace-support/01-RESEARCH.md (Source Types section lines 75-88; Common Pitfalls)
  </read_first>
  <action>
    Edit `scripts/marketplace_manager.py`. Changes are confined to (a) a new `_load_schema` helper, (b) the `validate_marketplace` function body + signature, (c) the `main()` `validate` branch that consumes it. Do NOT change `add_plugin`, `list_plugins`, `_get_plugin_source`, or `_resolve_source_path`.

    **Change 1: Add module-level constants and schema loader.**

    After the existing imports and before `_get_plugin_source`, add:
    ```python
    SCRIPT_DIR = Path(__file__).parent
    TOOLKIT_ROOT = SCRIPT_DIR.parent
    VERSION_MANIFEST = TOOLKIT_ROOT / "data" / "version-manifest.json"


    def _load_schema() -> dict:
        """Load marketplace schema facts from version-manifest.json. Returns empty
        dicts on missing/malformed manifest so validator degrades gracefully."""
        try:
            with open(VERSION_MANIFEST) as f:
                schemas = json.load(f).get("schemas", {})
        except (OSError, json.JSONDecodeError):
            return {"marketplace_manifest": {}, "marketplace_plugin_entry": {}}
        return {
            "marketplace_manifest": schemas.get("marketplace_manifest", {}),
            "marketplace_plugin_entry": schemas.get("marketplace_plugin_entry", {}),
        }
    ```

    **Change 2: Replace the entire `validate_marketplace` function.**

    Replace lines 39-109 (the current `validate_marketplace`) with this implementation. The new signature returns `(errors, warnings)` — two lists of strings.

    ```python
    def validate_marketplace(marketplace_path: Path) -> Tuple[List[str], List[str]]:
        """Validate marketplace.json with tiered severity.

        Returns (errors, warnings). Errors block installation; warnings are guidance.
        Schema facts are loaded from data/version-manifest.json.
        """
        errors: List[str] = []
        warnings: List[str] = []

        schema = _load_schema()
        mk_schema = schema["marketplace_manifest"]
        plugin_schema = schema["marketplace_plugin_entry"]
        reserved = set(mk_schema.get("reserved_names", []))
        metadata_fields = set(mk_schema.get("metadata_fields", ["description", "version", "pluginRoot"]))
        plugin_optional = set(plugin_schema.get("optional", []))
        source_type_keys = set(plugin_schema.get("source_types", {}).keys())
        # Fields whose absence triggers a warning (per CONTEXT.md tier)
        warn_missing_plugin_optionals = {"description", "homepage", "repository", "license", "keywords"}

        manifest_file = marketplace_path / ".claude-plugin" / "marketplace.json"
        if not manifest_file.exists():
            errors.append(f"Missing {manifest_file}")
            return errors, warnings

        try:
            with open(manifest_file) as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in marketplace.json: {e}")
            return errors, warnings

        # --- Top-level required fields (HARD ERRORS) ---
        if "name" not in manifest:
            errors.append("Missing required 'name' field in marketplace.json")
        else:
            if manifest["name"] in reserved:
                errors.append(
                    f"Marketplace name '{manifest['name']}' is reserved by Anthropic. "
                    f"Reserved list: {sorted(reserved)}"
                )

        if "owner" not in manifest:
            errors.append("Missing required 'owner' field in marketplace.json")
        elif not isinstance(manifest["owner"], dict):
            errors.append("'owner' must be an object {name, email?}")
        elif "name" not in manifest["owner"]:
            errors.append("Missing required 'owner.name' field in marketplace.json")

        # --- Metadata shape (HARD ERROR if not an object; WARNING for unknown keys) ---
        if "metadata" in manifest:
            if not isinstance(manifest["metadata"], dict):
                errors.append("'metadata' must be an object, not a list or string")
            else:
                for k in manifest["metadata"].keys():
                    if k not in metadata_fields:
                        warnings.append(f"Unknown metadata key '{k}' (known: {sorted(metadata_fields)})")

        # --- Plugins array ---
        if "plugins" not in manifest:
            errors.append("Missing required 'plugins' field in marketplace.json")
            return errors, warnings
        if not isinstance(manifest["plugins"], list):
            errors.append("'plugins' must be an array")
            return errors, warnings

        seen_names: dict[str, int] = {}
        for i, plugin in enumerate(manifest["plugins"]):
            if not isinstance(plugin, dict):
                errors.append(f"Plugin entry {i} must be an object")
                continue

            # Required: name
            if "name" not in plugin:
                errors.append(f"Plugin entry {i} missing 'name'")
            else:
                # Duplicate-name warning
                pname = plugin["name"]
                if pname in seen_names:
                    warnings.append(
                        f"Duplicate plugin name '{pname}' at entries {seen_names[pname]} and {i}"
                    )
                else:
                    seen_names[pname] = i

            # Required: source (or legacy path with warning)
            has_source = "source" in plugin
            has_path = "path" in plugin
            if has_path and not has_source:
                warnings.append(
                    f"Plugin entry {i} uses legacy 'path' field — migrate to 'source'"
                )
            source = _get_plugin_source(plugin)
            if not source:
                errors.append(f"Plugin entry {i} missing 'source' (or legacy 'path')")
            else:
                # Source type validation
                if isinstance(source, dict):
                    src_type = source.get("source")
                    if src_type and source_type_keys and src_type not in source_type_keys:
                        errors.append(
                            f"Plugin entry {i} unknown source type '{src_type}' "
                            f"(known: {sorted(source_type_keys)})"
                        )
                elif isinstance(source, str):
                    if "../" in source:
                        errors.append(
                            f"Plugin entry {i} source '{source}' contains '../' — paths must stay inside marketplace root"
                        )
                    # Local path resolution & existence check (preserve existing behavior)
                    local_path = _resolve_source_path(marketplace_path, source)
                    if local_path is not None:
                        if not local_path.exists():
                            errors.append(f"Plugin entry {i} source does not exist: {source}")
                        elif not (local_path / ".claude-plugin" / "plugin.json").exists() and source != "./":
                            errors.append(
                                f"Plugin entry {i} source '{source}' missing .claude-plugin/plugin.json"
                            )

            # Author shape (HARD ERROR if present and not an object)
            if "author" in plugin and not isinstance(plugin["author"], dict):
                errors.append(
                    f"Plugin entry {i} 'author' must be an object {{name, email?}}, got "
                    f"{type(plugin['author']).__name__}"
                )
            elif isinstance(plugin.get("author"), dict) and "name" not in plugin["author"]:
                errors.append(f"Plugin entry {i} 'author' object missing required 'name' field")

            # Optional fields missing (WARNINGS)
            pname_for_warn = plugin.get("name", f"entry-{i}")
            for optf in warn_missing_plugin_optionals:
                if optf not in plugin:
                    warnings.append(f"Plugin '{pname_for_warn}' missing optional field '{optf}'")

        return errors, warnings
    ```

    **Change 3: Update the `main()` `validate` branch** (currently lines ~270-281) to handle the new return shape:

    Replace the existing `if args.command == "validate":` block with:
    ```python
        if args.command == "validate":
            errors, warnings = validate_marketplace(marketplace_path)
            if args.json:
                print(json.dumps({
                    "valid": len(errors) == 0,
                    "errors": errors,
                    "warnings": warnings,
                }, indent=2))
            else:
                if errors:
                    print("ERRORS:")
                    for e in errors:
                        print(f"  - {e}")
                if warnings:
                    print("WARNINGS:")
                    for w in warnings:
                        print(f"  - {w}")
                if not errors and not warnings:
                    print("Marketplace is valid.")
                elif not errors:
                    print(f"\nMarketplace is valid (with {len(warnings)} warning(s)).")
            sys.exit(0 if not errors else 1)
    ```

    Do NOT change `add_plugin`, `list_plugins`, `validate_plugin`, `_get_plugin_source`, or `_resolve_source_path` bodies. Exit semantics: any errors → exit 1; warnings alone → exit 0.

    Note on `source == "./"`: in a standalone layout, `source` is `"./"` and the marketplace root IS the plugin root. Skip the "missing plugin.json at source" check in that case (see conditional in source string handling above).
  </action>
  <verify>
    <automated>
      python3 -c "import ast; ast.parse(open('scripts/marketplace_manager.py').read())" &&
      grep -q 'def _load_schema' scripts/marketplace_manager.py &&
      grep -q 'Tuple\[List\[str\], List\[str\]\]' scripts/marketplace_manager.py &&
      grep -q 'reserved by Anthropic' scripts/marketplace_manager.py &&
      grep -q "must be an object {name, email?}" scripts/marketplace_manager.py &&
      python3 -c "
import tempfile, json, subprocess
from pathlib import Path

def make_mk(td, manifest):
    mk = Path(td)/'mk'
    (mk/'.claude-plugin').mkdir(parents=True)
    (mk/'.claude-plugin'/'marketplace.json').write_text(json.dumps(manifest))
    return mk

# Test 1: reserved name → error + exit 1
with tempfile.TemporaryDirectory() as td:
    mk = make_mk(td, {'name':'agent-skills','owner':{'name':'O'},'plugins':[]})
    r = subprocess.run(['python3','scripts/marketplace_manager.py','validate',str(mk),'--json'], capture_output=True, text=True)
    assert r.returncode == 1
    out = json.loads(r.stdout)
    assert out['valid'] is False
    assert any('reserved' in e.lower() for e in out['errors'])

# Test 2: author as string → hard error
with tempfile.TemporaryDirectory() as td:
    # include a plugin dir so path-exists doesn't also fire
    p = Path(td)/'mk'/'p1'; p.mkdir(parents=True)
    (p/'.claude-plugin').mkdir(); (p/'.claude-plugin'/'plugin.json').write_text('{\"name\":\"p1\"}')
    mk = make_mk(td, {'name':'ok','owner':{'name':'O'},'plugins':[{'name':'p1','source':'./p1','author':'bad'}]})
    r = subprocess.run(['python3','scripts/marketplace_manager.py','validate',str(mk),'--json'], capture_output=True, text=True)
    out = json.loads(r.stdout)
    assert r.returncode == 1
    assert any('author' in e.lower() and 'object' in e.lower() for e in out['errors']), out

# Test 3: metadata as list → hard error
with tempfile.TemporaryDirectory() as td:
    mk = make_mk(td, {'name':'ok','owner':{'name':'O'},'metadata':['description','version'],'plugins':[]})
    r = subprocess.run(['python3','scripts/marketplace_manager.py','validate',str(mk),'--json'], capture_output=True, text=True)
    out = json.loads(r.stdout)
    assert r.returncode == 1
    assert any('metadata' in e.lower() and 'object' in e.lower() for e in out['errors']), out

# Test 4: missing optional fields → warning only, exit 0
with tempfile.TemporaryDirectory() as td:
    p = Path(td)/'mk'/'p1'; p.mkdir(parents=True)
    (p/'.claude-plugin').mkdir(); (p/'.claude-plugin'/'plugin.json').write_text('{\"name\":\"p1\"}')
    mk = make_mk(td, {'name':'mymk','owner':{'name':'O'},'plugins':[{'name':'p1','source':'./p1'}]})
    r = subprocess.run(['python3','scripts/marketplace_manager.py','validate',str(mk),'--json'], capture_output=True, text=True)
    out = json.loads(r.stdout)
    assert r.returncode == 0, f'expected 0, got {r.returncode}: {out}'
    assert out['valid'] is True
    assert any('homepage' in w for w in out['warnings']), out

# Test 5: duplicate plugin name → warning (exit 0)
with tempfile.TemporaryDirectory() as td:
    for sub in ['p1','p2']:
        d = Path(td)/'mk'/sub; d.mkdir(parents=True)
        (d/'.claude-plugin').mkdir(); (d/'.claude-plugin'/'plugin.json').write_text('{\"name\":\"x\"}')
    mk = make_mk(td, {'name':'mymk','owner':{'name':'O'},'plugins':[
        {'name':'x','source':'./p1','description':'a','homepage':'h','repository':'r','license':'MIT','keywords':[]},
        {'name':'x','source':'./p2','description':'b','homepage':'h','repository':'r','license':'MIT','keywords':[]},
    ]})
    r = subprocess.run(['python3','scripts/marketplace_manager.py','validate',str(mk),'--json'], capture_output=True, text=True)
    out = json.loads(r.stdout)
    assert r.returncode == 0, out
    assert any('duplicate' in w.lower() for w in out['warnings']), out

# Test 6: unknown source type → hard error
with tempfile.TemporaryDirectory() as td:
    mk = make_mk(td, {'name':'mymk','owner':{'name':'O'},'plugins':[{'name':'p','source':{'source':'ftp','url':'x'}}]})
    r = subprocess.run(['python3','scripts/marketplace_manager.py','validate',str(mk),'--json'], capture_output=True, text=True)
    out = json.loads(r.stdout)
    assert r.returncode == 1
    assert any('unknown source type' in e.lower() for e in out['errors']), out
print('OK')
"
    </automated>
  </verify>
  <acceptance_criteria>
    - `validate_marketplace` signature is `Tuple[List[str], List[str]]` returning `(errors, warnings)`.
    - Test 1: reserved marketplace name → exit 1 with "reserved" in errors.
    - Test 2: `author: "string"` → exit 1 with error mentioning "author" and "object".
    - Test 3: `metadata: [...]` (list, not object) → exit 1 with error mentioning "metadata" and "object".
    - Test 4: minimal-valid manifest missing optional fields → exit 0 with warnings for each of `homepage`, `repository`, `license`, `keywords`, `description`.
    - Test 5: duplicate plugin names → exit 0 with "duplicate" warning.
    - Test 6: unknown source type (e.g. `ftp`) → exit 1.
    - `--json` output includes `errors`, `warnings`, and `valid` keys.
    - `_load_schema` reads from `data/version-manifest.json` (not hardcoded).
    - `add_plugin`, `list_plugins`, `validate_plugin` behavior unchanged (existing CLI subcommands still work).
  </acceptance_criteria>
  <done>All six smoke tests pass; validator tiers severity correctly; no regression in add/list subcommands.</done>
</task>

</tasks>

<verification>
Smoke-test existing behavior preserved:
```bash
# list and add should still work on a known-good marketplace
python3 scripts/marketplace_manager.py list /home/sirtaj/proj/claude-stuff
python3 scripts/marketplace_manager.py validate /home/sirtaj/proj/claude-stuff --json | jq '.warnings | length'
```
Latter should run without errors, possibly emit warnings for missing optionals.
</verification>

<success_criteria>
- validate returns (errors, warnings) not (ok, errors)
- Tiered severity matches CONTEXT.md tier assignments exactly
- Schema facts loaded from version-manifest.json (no hardcoded reserved names or field lists)
- `--json` output structured with valid/errors/warnings
- Exit code: 1 iff errors non-empty
- add/list subcommands unchanged
</success_criteria>

<output>
After completion, create `.planning/phases/01-marketplace-support/01-04-SUMMARY.md` with: final severity tier table, sample outputs for each tier, confirmation that existing subcommands pass regression.
</output>
