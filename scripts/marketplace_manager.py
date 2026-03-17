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


def validate_marketplace(marketplace_path: Path) -> Tuple[bool, List[str]]:
    """Validate marketplace.json structure against canonical schema."""
    errors = []
    warnings = []

    manifest_file = marketplace_path / ".claude-plugin" / "marketplace.json"
    if not manifest_file.exists():
        errors.append(f"Missing {manifest_file}")
        return False, errors

    try:
        with open(manifest_file) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in marketplace.json: {e}")
        return False, errors

    # Required fields
    if "name" not in manifest:
        errors.append("Missing required 'name' field in marketplace.json")

    # owner.name is required by canonical schema
    if "owner" not in manifest:
        errors.append("Missing required 'owner' field in marketplace.json")
    elif not isinstance(manifest["owner"], dict):
        errors.append("'owner' must be an object")
    elif "name" not in manifest["owner"]:
        errors.append("Missing required 'owner.name' field in marketplace.json")

    if "plugins" not in manifest:
        errors.append("Missing required 'plugins' field in marketplace.json")
    elif not isinstance(manifest["plugins"], list):
        errors.append("'plugins' must be an array")
    else:
        # Validate each plugin entry
        for i, plugin in enumerate(manifest["plugins"]):
            if not isinstance(plugin, dict):
                errors.append(f"Plugin entry {i} must be an object")
                continue

            # Check for source (preferred) vs path (legacy)
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
                # Validate local paths exist
                local_path = _resolve_source_path(marketplace_path, source)
                if local_path is not None:
                    if not local_path.exists():
                        errors.append(f"Plugin source does not exist: {source}")
                    elif not (local_path / ".claude-plugin" / "plugin.json").exists():
                        errors.append(
                            f"Plugin '{source}' missing .claude-plugin/plugin.json"
                        )

            if "name" not in plugin:
                errors.append(f"Plugin entry {i} missing 'name'")

    # Print warnings
    for warning in warnings:
        print(f"  WARNING: {warning}", file=sys.stderr)

    return len(errors) == 0, errors


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
        is_valid, errors = validate_marketplace(marketplace_path)
        if args.json:
            print(json.dumps({"valid": is_valid, "errors": errors}))
        else:
            if is_valid:
                print("Marketplace is valid.")
            else:
                print("Validation errors:")
                for error in errors:
                    print(f"  - {error}")
        sys.exit(0 if is_valid else 1)

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
