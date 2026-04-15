---
phase: 01-marketplace-support
plan: 03
type: execute
wave: 2
depends_on: [01]
files_modified:
  - scripts/marketplace_register.py
  - scripts/plugin_scaffolder.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "Running marketplace_register.py from inside an umbrella detects the ancestor marketplace.json and registers a new plugin entry"
    - "Running marketplace_register.py in greenfield with --layout standalone scaffolds a plugin whose marketplace.json is at the plugin root and is immediately installable with /plugin marketplace add <plugin-dir>"
    - "Running marketplace_register.py in greenfield with --layout umbrella scaffolds the umbrella dir plus the first plugin entry"
    - "plugin_scaffolder.py (with --marketplace standalone) creates a marketplace.json at the plugin root by default (auto-create standalone)"
    - "Upward-search detection uses pure pathlib (no subprocess) per zero-dep convention"
    - "Reserved name collision is caught before any file is written"
    - "Plugin path outside marketplace root (../) raises a clear error"
  artifacts:
    - path: "scripts/marketplace_register.py"
      provides: "Upward-search detection, three-flow orchestration, safe JSON append"
      min_lines: 180
      contains: "def find_ancestor_marketplace, def append_plugin_entry, three flow selection"
    - path: "scripts/plugin_scaffolder.py"
      provides: "Plugin scaffolder extended with standalone marketplace.json auto-creation"
      contains: "--marketplace flag and write_marketplace_json function"
  key_links:
    - from: "scripts/marketplace_register.py"
      to: "data/version-manifest.json"
      via: "reads schemas.marketplace_manifest.reserved_names for collision check"
      pattern: "reserved_names"
    - from: "scripts/plugin_scaffolder.py"
      to: "scripts/marketplace_register.py"
      via: "standalone flow can either inline the marketplace.json write OR call marketplace_register.py; pick the simpler one"
      pattern: "marketplace.json"
---

<objective>
Implement the three scaffolder flows (register-into-existing, greenfield-standalone, greenfield-umbrella) via a new `scripts/marketplace_register.py` using pure Python stdlib. Extend `scripts/plugin_scaffolder.py` so that standalone scaffolding auto-creates a marketplace.json at the plugin root (default behavior), making the generated plugin installable with a single `/plugin marketplace add <plugin-dir>`.

Purpose: Close the toolkit's tooling gap. Today, users manually wire marketplace.json. After this plan, `extension-builder` can orchestrate the entire flow via these scripts.

Output: new `scripts/marketplace_register.py` (~200 lines); extended `scripts/plugin_scaffolder.py` with `--marketplace {standalone|none}` flag (default `standalone`).
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
@scripts/plugin_scaffolder.py
@scripts/marketplace_manager.py
@data/version-manifest.json
</context>

<interfaces>
<!-- Existing script pattern all toolkit scripts follow. Reuse. -->

Standard prelude (from scripts/marketplace_manager.py and plugin_scaffolder.py):
```python
#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Tuple

SCRIPT_DIR = Path(__file__).parent
TOOLKIT_ROOT = SCRIPT_DIR.parent
VERSION_MANIFEST = TOOLKIT_ROOT / "data" / "version-manifest.json"
```

Existing helper shape (from marketplace_manager.py — mirror its JSON write style):
```python
with open(manifest_file, "w") as f:
    json.dump(marketplace, f, indent=2)
    f.write("\n")
```
</interfaces>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Create scripts/marketplace_register.py with upward-search detection and three flows</name>
  <files>scripts/marketplace_register.py</files>
  <read_first>
    - scripts/marketplace_manager.py (entire file — mirror its style; reuse its add_plugin logic conceptually)
    - scripts/plugin_scaffolder.py (after Plan 01 Task 3 fix — understand existing CLI pattern)
    - data/version-manifest.json (read schemas.marketplace_manifest.reserved_names; schemas.marketplace_plugin_entry.required)
    - .planning/phases/01-marketplace-support/01-RESEARCH.md (Three Scaffolder Flows section lines 176-201; Safe jq-append pattern lines 364-383)
    - .planning/phases/01-marketplace-support/01-CONTEXT.md (Scaffolder behavior section)
  </read_first>
  <action>
    Create new file `scripts/marketplace_register.py`. Make it executable (`chmod +x`). Shebang `#!/usr/bin/env python3`. Python stdlib only.

    **Module docstring** (exact):
    ```
    """
    Detect an ancestor marketplace.json and orchestrate one of three scaffolder flows:
      - Inside umbrella  → register new plugin entry into the existing marketplace.json
      - Greenfield + --layout standalone → scaffold plugin with its own marketplace.json
      - Greenfield + --layout umbrella   → scaffold umbrella dir + first plugin entry

    Upward-search detection is pure pathlib (no subprocess). Safe JSON append uses
    Python json module (no shell jq). Reserved-name collisions and ../ path violations
    are caught before any file is written.

    Usage:
        python marketplace_register.py <plugin_name> [--plugin-path PATH] [--layout {standalone,umbrella}]
                                       [--owner NAME] [--owner-email EMAIL]
                                       [--marketplace-name NAME]

    Exit codes:
        0 - Success
        1 - Runtime error (reserved name, path violation, duplicate plugin, etc.)
        2 - Usage error
    """
    ```

    **Constants (module scope)**:
    ```python
    SCRIPT_DIR = Path(__file__).parent
    TOOLKIT_ROOT = SCRIPT_DIR.parent
    VERSION_MANIFEST = TOOLKIT_ROOT / "data" / "version-manifest.json"
    ```

    **Required functions** (implement each with the exact signatures and behaviors below):

    1. `load_reserved_names() -> set[str]`
       - Read `VERSION_MANIFEST`, return `set(json.load(f)["schemas"]["marketplace_manifest"]["reserved_names"])`.
       - If file missing or malformed, return empty set (graceful degradation — validator will still catch it).

    2. `find_ancestor_marketplace(start: Path) -> Optional[Path]`
       - Walk upward from `start.resolve()` toward filesystem root. At each level check if `<level>/.claude-plugin/marketplace.json` exists as a regular file.
       - Return the level directory (not the manifest path) on first hit.
       - Stop when `parent == current` (filesystem root) and return `None`.
       - Pattern copied verbatim from RESEARCH.md lines 181-193.

    3. `read_manifest(marketplace_root: Path) -> dict`
       - Open `<marketplace_root>/.claude-plugin/marketplace.json`, return `json.load(f)`.

    4. `write_manifest(marketplace_root: Path, manifest: dict) -> None`
       - Open `<marketplace_root>/.claude-plugin/marketplace.json` for writing. `json.dump(manifest, f, indent=2); f.write("\n")`.

    5. `validate_relative_path(plugin_path: Path, marketplace_root: Path) -> str`
       - Resolve both paths. Raise `ValueError` if plugin is not inside marketplace root: `plugin_path.relative_to(marketplace_root)`.
       - Return the source string `"./" + str(rel)` (POSIX separators; use `rel.as_posix()`).

    6. `append_plugin_entry(marketplace_root: Path, entry: dict) -> None`
       - Idempotency: read manifest, check `entry["name"]` not in `{p["name"] for p in manifest.get("plugins", [])}`. Raise `ValueError(f"Plugin '{entry['name']}' already registered")` on collision.
       - `manifest.setdefault("plugins", []).append(entry)`, then `write_manifest`.

    7. `check_reserved_name(name: str) -> None`
       - `if name in load_reserved_names(): raise ValueError(f"Marketplace name '{name}' is reserved by Anthropic. Choose a different name.")`

    8. `scaffold_marketplace_manifest(marketplace_root: Path, marketplace_name: str, owner_name: str, owner_email: Optional[str] = None, first_entry: Optional[dict] = None) -> None`
       - Build manifest dict:
         ```python
         manifest = {
             "name": marketplace_name,
             "owner": {"name": owner_name},
             "plugins": [] if first_entry is None else [first_entry],
         }
         if owner_email:
             manifest["owner"]["email"] = owner_email
         ```
       - `check_reserved_name(marketplace_name)` first (raise before mkdir).
       - `(marketplace_root / ".claude-plugin").mkdir(parents=True, exist_ok=True)`.
       - `write_manifest(marketplace_root, manifest)`.

    9. `build_plugin_entry(plugin_name: str, source: str, plugin_manifest: Optional[dict] = None) -> dict`
       - Minimum: `{"name": plugin_name, "source": source}`.
       - If `plugin_manifest` provided, pull through `description`, `version` (both optional). Do NOT pull through `author` automatically (keep entry minimal; user can add later).

    10. `register_in_existing(plugin_name: str, plugin_path: Path, marketplace_root: Path) -> str`
        - Flow: inside-umbrella registration.
        - `source = validate_relative_path(plugin_path, marketplace_root)`
        - Read plugin.json if present (for optional description/version).
        - Build entry, call `append_plugin_entry`.
        - Return human-readable success string: `f"Registered '{plugin_name}' into {marketplace_root.name}/.claude-plugin/marketplace.json as {source}"`.

    11. `scaffold_standalone(plugin_name: str, plugin_path: Path, owner_name: str, owner_email: Optional[str], marketplace_name: Optional[str]) -> str`
        - Flow: greenfield standalone.
        - `mk_name = marketplace_name or plugin_name` (default marketplace name = plugin name for standalone).
        - `check_reserved_name(mk_name)`.
        - `entry = build_plugin_entry(plugin_name, source="./")` — standalone: source is "./" (marketplace root IS the plugin root).
        - `scaffold_marketplace_manifest(plugin_path, mk_name, owner_name, owner_email, first_entry=entry)`.
        - Return `f"Scaffolded standalone marketplace at {plugin_path}/.claude-plugin/marketplace.json"`.

    12. `scaffold_umbrella(plugin_name: str, umbrella_path: Path, plugin_subdir_path: Path, owner_name: str, owner_email: Optional[str], marketplace_name: str) -> str`
        - Flow: greenfield umbrella (umbrella dir created + first plugin entry).
        - `check_reserved_name(marketplace_name)`.
        - `source = validate_relative_path(plugin_subdir_path, umbrella_path)`.
        - `entry = build_plugin_entry(plugin_name, source)`.
        - `scaffold_marketplace_manifest(umbrella_path, marketplace_name, owner_name, owner_email, first_entry=entry)`.
        - Return `f"Scaffolded umbrella marketplace at {umbrella_path}/.claude-plugin/marketplace.json with first plugin '{plugin_name}'"`.

    **CLI (`main()`)**:
    - argparse with these args:
      - `plugin_name` (positional, required) — plugin identifier to register
      - `--plugin-path PATH` (default: CWD) — where the plugin lives or will live
      - `--layout {standalone,umbrella,auto}` (default: `auto`) — `auto` uses detection; explicit overrides detection
      - `--owner NAME` (required unless layout is register-into-existing)
      - `--owner-email EMAIL` (optional)
      - `--marketplace-name NAME` (required for umbrella; optional for standalone, defaults to plugin_name)
      - `--umbrella-path PATH` (required for greenfield umbrella; marks the umbrella root)
    - Dispatch logic:
      ```
      plugin_path = Path(args.plugin_path).resolve()
      layout = args.layout
      detected = find_ancestor_marketplace(plugin_path.parent if not plugin_path.exists() else plugin_path)
      if detected and layout in ("auto", "umbrella"):
          # Register-in-existing wins when inside umbrella
          msg = register_in_existing(args.plugin_name, plugin_path, detected)
      elif layout == "auto":
          print("Error: no ancestor marketplace.json found; specify --layout standalone or --layout umbrella", file=sys.stderr); sys.exit(2)
      elif layout == "standalone":
          if not args.owner: usage_error
          msg = scaffold_standalone(args.plugin_name, plugin_path, args.owner, args.owner_email, args.marketplace_name)
      elif layout == "umbrella":
          if not args.umbrella_path or not args.owner or not args.marketplace_name: usage_error
          umbrella = Path(args.umbrella_path).resolve()
          msg = scaffold_umbrella(args.plugin_name, umbrella, plugin_path, args.owner, args.owner_email, args.marketplace_name)
      print(msg); sys.exit(0)
      ```
    - Wrap the dispatch in `try/except ValueError as e: print(f"Error: {e}", file=sys.stderr); sys.exit(1)`.

    **Error behavior contract** (user-visible):
    - Reserved name: `Error: Marketplace name '<name>' is reserved by Anthropic. Choose a different name.`
    - `../` / outside-marketplace path: `Error: Plugin must be inside marketplace root; got <plugin_path> not under <marketplace_root>` (catch ValueError from `relative_to` and re-raise with this message).
    - Duplicate plugin: `Error: Plugin '<name>' already registered`.

    End file with `if __name__ == "__main__": main()`.

    Keep the file to ~200 lines. Use docstrings on each public function. No external imports beyond stdlib.
  </action>
  <verify>
    <automated>
      test -x scripts/marketplace_register.py &&
      python3 -c "import ast; ast.parse(open('scripts/marketplace_register.py').read())" &&
      grep -q 'def find_ancestor_marketplace' scripts/marketplace_register.py &&
      grep -q 'def append_plugin_entry' scripts/marketplace_register.py &&
      grep -q 'def scaffold_standalone' scripts/marketplace_register.py &&
      grep -q 'def scaffold_umbrella' scripts/marketplace_register.py &&
      grep -q 'def register_in_existing' scripts/marketplace_register.py &&
      grep -q 'def check_reserved_name' scripts/marketplace_register.py &&
      python3 -c "
import tempfile, json, subprocess, os
from pathlib import Path
# Test 1: reserved name rejected
with tempfile.TemporaryDirectory() as td:
    r = subprocess.run(['python3','scripts/marketplace_register.py','my-plugin','--plugin-path',td,'--layout','standalone','--owner','Me','--marketplace-name','agent-skills'], capture_output=True, text=True)
    assert r.returncode == 1, f'expected 1, got {r.returncode}: {r.stderr}'
    assert 'reserved' in r.stderr.lower(), r.stderr

# Test 2: standalone scaffold creates marketplace.json
with tempfile.TemporaryDirectory() as td:
    p = Path(td)/'my-plugin'; p.mkdir()
    r = subprocess.run(['python3','scripts/marketplace_register.py','my-plugin','--plugin-path',str(p),'--layout','standalone','--owner','Me'], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    mf = p/'.claude-plugin'/'marketplace.json'
    assert mf.exists()
    m = json.loads(mf.read_text())
    assert m['name'] == 'my-plugin'
    assert m['owner'] == {'name': 'Me'}
    assert m['plugins'][0]['source'] == './'

# Test 3: register into existing (detection)
with tempfile.TemporaryDirectory() as td:
    um = Path(td)/'umbrella'; (um/'.claude-plugin').mkdir(parents=True)
    (um/'.claude-plugin'/'marketplace.json').write_text(json.dumps({'name':'um','owner':{'name':'O'},'plugins':[]}))
    plug = um/'plugin-a'; plug.mkdir()
    r = subprocess.run(['python3','scripts/marketplace_register.py','plugin-a','--plugin-path',str(plug),'--layout','auto','--owner','O'], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    m = json.loads((um/'.claude-plugin'/'marketplace.json').read_text())
    assert any(p['name']=='plugin-a' for p in m['plugins'])

# Test 4: ../ outside root rejected
with tempfile.TemporaryDirectory() as td:
    um = Path(td)/'umbrella'; (um/'.claude-plugin').mkdir(parents=True)
    (um/'.claude-plugin'/'marketplace.json').write_text(json.dumps({'name':'u','owner':{'name':'O'},'plugins':[]}))
    outside = Path(td)/'outside'; outside.mkdir()
    r = subprocess.run(['python3','scripts/marketplace_register.py','out','--plugin-path',str(outside),'--layout','umbrella','--owner','O','--marketplace-name','u','--umbrella-path',str(um)], capture_output=True, text=True)
    assert r.returncode == 1, f'got {r.returncode}: {r.stdout} / {r.stderr}'
print('OK')
"
    </automated>
  </verify>
  <acceptance_criteria>
    - File `scripts/marketplace_register.py` exists, is executable, is valid Python 3.
    - Contains all 12 required functions with the specified signatures.
    - Test 1: reserved name `agent-skills` → exit 1, stderr says "reserved".
    - Test 2: standalone scaffold creates `marketplace.json` with `name=plugin`, `owner={name:"Me"}`, first plugin entry source `"./"`.
    - Test 3: auto-layout detects ancestor marketplace.json and appends the new plugin.
    - Test 4: plugin path outside umbrella root → exit 1.
    - Imports only from stdlib (no third-party).
    - No subprocess calls to `jq`, `find`, `grep`.
  </acceptance_criteria>
  <done>All smoke tests in the verify block pass; script is ~200 lines stdlib-only.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Extend plugin_scaffolder.py to auto-create standalone marketplace.json</name>
  <files>scripts/plugin_scaffolder.py</files>
  <read_first>
    - scripts/plugin_scaffolder.py (current state after Plan 01 Task 3 mkdir fix)
    - scripts/marketplace_register.py (just created in Task 1 above — may be called from scaffolder OR logic can be inlined; pick simpler)
    - .planning/phases/01-marketplace-support/01-CONTEXT.md (Standalone default: auto-create marketplace.json at plugin root)
  </read_first>
  <action>
    Edit `scripts/plugin_scaffolder.py`. Two changes:

    **Change 1: add a `--marketplace` CLI flag.**

    In `main()` argparse section, add after the existing `--email` argument:
    ```python
        parser.add_argument(
            "--marketplace",
            choices=["standalone", "none"],
            default="standalone",
            help="Auto-create marketplace.json at plugin root (standalone, default) or skip (none)"
        )
        parser.add_argument(
            "--marketplace-name",
            default="",
            help="Marketplace name for standalone layout (default: plugin name)"
        )
    ```

    **Change 2: after plugin structure is created, emit a marketplace.json when `--marketplace standalone`.**

    Extend `create_plugin_structure` to accept two new params:
    ```python
    def create_plugin_structure(
        name: str,
        output_dir: Path,
        description: str = "",
        author_name: str = "",
        author_email: str = "",
        marketplace: str = "standalone",
        marketplace_name: str = "",
    ) -> Path:
    ```

    At the end of `create_plugin_structure` (after README is written, before `return plugin_dir`), add:
    ```python
        if marketplace == "standalone":
            mk_name = marketplace_name or name
            _check_reserved_name(mk_name)
            mk = {
                "name": mk_name,
                "owner": {"name": author_name} if author_name else {"name": name},
                "plugins": [
                    {
                        "name": name,
                        "source": "./",
                        "description": description or f"{name} plugin for Claude Code",
                        "version": "1.0.0",
                    }
                ],
            }
            if author_email and author_name:
                mk["owner"]["email"] = author_email
            with open(plugin_dir / ".claude-plugin" / "marketplace.json", "w") as f:
                json.dump(mk, f, indent=2)
                f.write("\n")
    ```

    Add a module-level helper `_check_reserved_name`:
    ```python
    def _check_reserved_name(name: str) -> None:
        """Raise ValueError if name is reserved per data/version-manifest.json."""
        manifest_path = Path(__file__).parent.parent / "data" / "version-manifest.json"
        try:
            with open(manifest_path) as f:
                reserved = set(json.load(f)["schemas"]["marketplace_manifest"]["reserved_names"])
        except (OSError, KeyError, json.JSONDecodeError):
            return  # graceful degradation; validator will still catch
        if name in reserved:
            raise ValueError(
                f"Marketplace name '{name}' is reserved by Anthropic. Choose a different name."
            )
    ```

    Wire the new args through in `main()`:
    ```python
        plugin_dir = create_plugin_structure(
            name=args.name,
            output_dir=output_dir,
            description=args.description,
            author_name=args.author,
            author_email=args.email,
            marketplace=args.marketplace,
            marketplace_name=args.marketplace_name,
        )
    ```

    Update the "Next steps" printout (around line 184-187) to include, when `marketplace == "standalone"`:
    ```
    print(f"  4. /plugin marketplace add {plugin_dir}")
    print(f"  5. /plugin install {args.name}@{args.marketplace_name or args.name}")
    ```

    Do NOT modify anything else. Keep default behavior (`--marketplace standalone`) so existing calls get marketplace.json for free.
  </action>
  <verify>
    <automated>
      grep -q '"--marketplace"' scripts/plugin_scaffolder.py &&
      grep -q 'def _check_reserved_name' scripts/plugin_scaffolder.py &&
      grep -q '"source": "./"' scripts/plugin_scaffolder.py &&
      python3 -c "
import tempfile, json, subprocess
from pathlib import Path
# Default (standalone) creates marketplace.json
with tempfile.TemporaryDirectory() as td:
    r = subprocess.run(['python3','scripts/plugin_scaffolder.py','demo','--output',td,'--author','Me','--email','me@x.com'], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    mf = Path(td)/'demo'/'.claude-plugin'/'marketplace.json'
    assert mf.exists(), 'standalone marketplace.json not created by default'
    m = json.loads(mf.read_text())
    assert m['name']=='demo'
    assert m['owner']=={'name':'Me','email':'me@x.com'}
    assert m['plugins'][0]['source']=='./'
# --marketplace none skips
with tempfile.TemporaryDirectory() as td:
    r = subprocess.run(['python3','scripts/plugin_scaffolder.py','demo2','--output',td,'--marketplace','none'], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert not (Path(td)/'demo2'/'.claude-plugin'/'marketplace.json').exists()
# Reserved name rejected
with tempfile.TemporaryDirectory() as td:
    r = subprocess.run(['python3','scripts/plugin_scaffolder.py','demo3','--output',td,'--marketplace-name','agent-skills'], capture_output=True, text=True)
    assert r.returncode == 1, f'expected 1, got {r.returncode}'
    assert 'reserved' in r.stderr.lower()
print('OK')
"
    </automated>
  </verify>
  <acceptance_criteria>
    - `--marketplace {standalone,none}` flag exists; defaults to `standalone`.
    - Default scaffold creates `<plugin>/.claude-plugin/marketplace.json` with `name`, `owner`, single-entry `plugins` with `source: "./"`.
    - `--marketplace none` skips marketplace.json creation.
    - Reserved marketplace names rejected with exit 1.
    - Next-steps printout includes `/plugin marketplace add` command.
    - Existing behavior (plugin.json, skills/, etc.) unchanged.
  </acceptance_criteria>
  <done>All smoke tests pass; default scaffold is immediately installable via `/plugin marketplace add`.</done>
</task>

</tasks>

<verification>
Run both tasks' automated verification. End-to-end spot check:
```bash
tmpdir=$(mktemp -d)
python3 scripts/plugin_scaffolder.py test-one --output "$tmpdir" --author "Me"
ls -la "$tmpdir/test-one/.claude-plugin/"
cat "$tmpdir/test-one/.claude-plugin/marketplace.json"
rm -rf "$tmpdir"
```
Should show both `plugin.json` and `marketplace.json` at plugin root with matching plugin name.
</verification>

<success_criteria>
- scripts/marketplace_register.py exists with all three flows + detection
- scripts/plugin_scaffolder.py auto-creates standalone marketplace.json by default
- Reserved-name collisions caught in both scripts before any file write
- Outside-marketplace-root paths rejected with clear error
- Default scaffold → immediately installable with single `/plugin marketplace add`
</success_criteria>

<output>
After completion, create `.planning/phases/01-marketplace-support/01-03-SUMMARY.md` with: CLI surface of both scripts, example end-to-end run transcript, flow selection table.
</output>
