#!/usr/bin/env python3
"""
Manage local Claude Code plugin marketplace.

Validates marketplace.json structure and helps register new plugins.

Usage:
    python marketplace_manager.py validate <marketplace_path>
    python marketplace_manager.py add <marketplace_path> <plugin_path>
    python marketplace_manager.py list <marketplace_path>

Exit codes:
    0 - Success
    1 - Validation error
    2 - Usage error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple


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


def _get_plugin_source(entry: dict) -> str | None:
    """Get plugin source from entry, preferring 'source' over legacy 'path'."""
    return entry.get("source") or entry.get("path")


def _resolve_source_path(marketplace_path: Path, source: str) -> Path | None:
    """Resolve a source string to a local path, if it's a relative path source."""
    if source.startswith(("./", "../")) or not any(
        source.startswith(p) for p in ("github:", "http://", "https://", "npm:", "pip:")
    ):
        return marketplace_path / source
    return None


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
    metadata_fields = set(
        mk_schema.get("metadata_fields", ["description", "version", "pluginRoot"])
    )
    plugin_optional = set(plugin_schema.get("optional", []))  # noqa: F841
    source_type_keys = set(plugin_schema.get("source_types", {}).keys())
    # Fields whose absence triggers a warning (per CONTEXT.md tier)
    warn_missing_plugin_optionals = {
        "description",
        "homepage",
        "repository",
        "license",
        "keywords",
    }

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
                    warnings.append(
                        f"Unknown metadata key '{k}' (known: {sorted(metadata_fields)})"
                    )

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
                local_path = _resolve_source_path(marketplace_path, source)
                if local_path is not None:
                    if not local_path.exists():
                        errors.append(
                            f"Plugin entry {i} source does not exist: {source}"
                        )
                    elif (
                        not (local_path / ".claude-plugin" / "plugin.json").exists()
                        and source != "./"
                    ):
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
            errors.append(
                f"Plugin entry {i} 'author' object missing required 'name' field"
            )

        # Optional fields missing (WARNINGS)
        pname_for_warn = plugin.get("name", f"entry-{i}")
        for optf in warn_missing_plugin_optionals:
            if optf not in plugin:
                warnings.append(
                    f"Plugin '{pname_for_warn}' missing optional field '{optf}'"
                )

    return errors, warnings


def validate_plugin(plugin_path: Path) -> Tuple[bool, List[str]]:
    """Validate a plugin structure."""
    errors = []

    plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        errors.append("Missing .claude-plugin/plugin.json")
        return False, errors

    try:
        with open(plugin_json) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid plugin.json: {e}")
        return False, errors

    if "name" not in manifest:
        errors.append("Plugin missing 'name'")
    if "description" not in manifest:
        errors.append("Plugin missing 'description'")

    return len(errors) == 0, errors


def add_plugin(marketplace_path: Path, plugin_path: Path) -> Tuple[bool, str]:
    """Add a plugin to the marketplace."""
    # Validate the plugin first
    is_valid, errors = validate_plugin(plugin_path)
    if not is_valid:
        return False, f"Invalid plugin: {'; '.join(errors)}"

    # Read plugin manifest for metadata
    plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
    with open(plugin_json) as f:
        plugin_manifest = json.load(f)

    plugin_name = plugin_manifest["name"]

    # Read marketplace manifest
    manifest_file = marketplace_path / ".claude-plugin" / "marketplace.json"
    with open(manifest_file) as f:
        marketplace = json.load(f)

    # Check if already registered
    existing = [
        p for p in marketplace.get("plugins", []) if p.get("name") == plugin_name
    ]
    if existing:
        return False, f"Plugin '{plugin_name}' already registered"

    # Calculate relative path
    try:
        rel_path = plugin_path.relative_to(marketplace_path)
    except ValueError:
        return False, "Plugin must be inside marketplace directory"

    # Build entry with canonical 'source' field and metadata from manifest
    entry = {
        "name": plugin_name,
        "source": f"./{rel_path}",
        "description": plugin_manifest.get("description", ""),
        "version": plugin_manifest.get("version", "0.0.0"),
    }

    # Add to plugins list
    if "plugins" not in marketplace:
        marketplace["plugins"] = []

    marketplace["plugins"].append(entry)

    # Write back
    with open(manifest_file, "w") as f:
        json.dump(marketplace, f, indent=2)
        f.write("\n")

    return True, f"Added plugin '{plugin_name}' at ./{rel_path}"


def list_plugins(marketplace_path: Path) -> List[dict]:
    """List all plugins in marketplace."""
    manifest_file = marketplace_path / ".claude-plugin" / "marketplace.json"
    if not manifest_file.exists():
        return []

    with open(manifest_file) as f:
        marketplace = json.load(f)

    plugins = []
    for entry in marketplace.get("plugins", []):
        source = _get_plugin_source(entry)
        uses_legacy = "path" in entry and "source" not in entry

        # Determine source type
        if source and any(
            source.startswith(p) for p in ("github:", "https://", "http://")
        ):
            source_type = "remote"
        elif source and source.startswith("npm:"):
            source_type = "npm"
        elif source and source.startswith("pip:"):
            source_type = "pip"
        else:
            source_type = "local"

        plugin_info = {
            "name": entry.get("name"),
            "source": source,
            "source_type": source_type,
            "exists": False,
            "valid": False,
            "legacy_path": uses_legacy,
        }

        # Check local paths
        if source_type == "local" and source:
            local_path = _resolve_source_path(marketplace_path, source)
            if local_path:
                plugin_json = local_path / ".claude-plugin" / "plugin.json"
                plugin_info["exists"] = local_path.exists()
                plugin_info["valid"] = plugin_json.exists()

                if plugin_json.exists():
                    try:
                        with open(plugin_json) as f:
                            manifest = json.load(f)
                        plugin_info["version"] = manifest.get("version", "0.0.0")
                        plugin_info["description"] = manifest.get("description", "")
                    except Exception:
                        pass

        # Use marketplace entry metadata as fallback
        if "version" not in plugin_info:
            plugin_info["version"] = entry.get("version", "?")
        if "description" not in plugin_info:
            plugin_info["description"] = entry.get("description", "")

        plugins.append(plugin_info)

    return plugins


def main():
    parser = argparse.ArgumentParser(
        description="Manage Claude Code plugin marketplace"
    )
    parser.add_argument(
        "command", choices=["validate", "add", "list"], help="Command to run"
    )
    parser.add_argument("marketplace_path", help="Path to marketplace root")
    parser.add_argument(
        "plugin_path", nargs="?", help="Path to plugin (for add command)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    marketplace_path = Path(args.marketplace_path).resolve()

    if args.command == "validate":
        errors, warnings = validate_marketplace(marketplace_path)
        if args.json:
            print(
                json.dumps(
                    {
                        "valid": len(errors) == 0,
                        "errors": errors,
                        "warnings": warnings,
                    },
                    indent=2,
                )
            )
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

    elif args.command == "add":
        if not args.plugin_path:
            print("Error: plugin_path required for add command", file=sys.stderr)
            sys.exit(2)

        plugin_path = Path(args.plugin_path).resolve()
        success, message = add_plugin(marketplace_path, plugin_path)

        if args.json:
            print(json.dumps({"success": success, "message": message}))
        else:
            print(message)
        sys.exit(0 if success else 1)

    elif args.command == "list":
        plugins = list_plugins(marketplace_path)
        if args.json:
            print(json.dumps(plugins, indent=2))
        else:
            if not plugins:
                print("No plugins in marketplace.")
            else:
                print(f"Plugins in {marketplace_path.name}:\n")
                for p in plugins:
                    status = "OK" if p.get("valid") else "INVALID"
                    version = p.get("version", "?")
                    source_type = p.get("source_type", "local")
                    legacy = " (legacy 'path' field)" if p.get("legacy_path") else ""
                    print(f"  [{status}] {p['name']} v{version}")
                    print(f"        {p.get('description', 'No description')[:60]}")
                    print(f"        Source: {p['source']} ({source_type}){legacy}")
                    print()


if __name__ == "__main__":
    main()
