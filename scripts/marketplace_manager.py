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


def validate_marketplace(marketplace_path: Path) -> Tuple[bool, List[str]]:
    """Validate marketplace.json structure."""
    errors = []

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
        errors.append("Missing 'name' field in marketplace.json")

    if "plugins" not in manifest:
        errors.append("Missing 'plugins' field in marketplace.json")
    elif not isinstance(manifest["plugins"], list):
        errors.append("'plugins' must be an array")
    else:
        # Validate each plugin entry
        for i, plugin in enumerate(manifest["plugins"]):
            if not isinstance(plugin, dict):
                errors.append(f"Plugin entry {i} must be an object")
                continue

            if "path" not in plugin:
                errors.append(f"Plugin entry {i} missing 'path'")
            else:
                plugin_dir = marketplace_path / plugin["path"]
                if not plugin_dir.exists():
                    errors.append(f"Plugin path does not exist: {plugin['path']}")
                elif not (plugin_dir / ".claude-plugin" / "plugin.json").exists():
                    errors.append(
                        f"Plugin '{plugin['path']}' missing .claude-plugin/plugin.json"
                    )

            if "name" not in plugin:
                errors.append(f"Plugin entry {i} missing 'name'")

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


def add_plugin(
    marketplace_path: Path,
    plugin_path: Path
) -> Tuple[bool, str]:
    """Add a plugin to the marketplace."""
    # Validate the plugin first
    is_valid, errors = validate_plugin(plugin_path)
    if not is_valid:
        return False, f"Invalid plugin: {'; '.join(errors)}"

    # Read plugin manifest for name
    plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
    with open(plugin_json) as f:
        plugin_manifest = json.load(f)

    plugin_name = plugin_manifest["name"]

    # Read marketplace manifest
    manifest_file = marketplace_path / ".claude-plugin" / "marketplace.json"
    with open(manifest_file) as f:
        marketplace = json.load(f)

    # Check if already registered
    existing = [p for p in marketplace.get("plugins", []) if p.get("name") == plugin_name]
    if existing:
        return False, f"Plugin '{plugin_name}' already registered"

    # Calculate relative path
    try:
        rel_path = plugin_path.relative_to(marketplace_path)
    except ValueError:
        return False, "Plugin must be inside marketplace directory"

    # Add to plugins list
    if "plugins" not in marketplace:
        marketplace["plugins"] = []

    marketplace["plugins"].append({
        "path": str(rel_path),
        "name": plugin_name
    })

    # Write back
    with open(manifest_file, "w") as f:
        json.dump(marketplace, f, indent=2)

    return True, f"Added plugin '{plugin_name}' at {rel_path}"


def list_plugins(marketplace_path: Path) -> List[dict]:
    """List all plugins in marketplace."""
    manifest_file = marketplace_path / ".claude-plugin" / "marketplace.json"
    if not manifest_file.exists():
        return []

    with open(manifest_file) as f:
        marketplace = json.load(f)

    plugins = []
    for entry in marketplace.get("plugins", []):
        plugin_path = marketplace_path / entry.get("path", "")
        plugin_json = plugin_path / ".claude-plugin" / "plugin.json"

        plugin_info = {
            "name": entry.get("name"),
            "path": entry.get("path"),
            "exists": plugin_path.exists(),
            "valid": plugin_json.exists()
        }

        if plugin_json.exists():
            try:
                with open(plugin_json) as f:
                    manifest = json.load(f)
                plugin_info["version"] = manifest.get("version", "0.0.0")
                plugin_info["description"] = manifest.get("description", "")
            except Exception:
                pass

        plugins.append(plugin_info)

    return plugins


def main():
    parser = argparse.ArgumentParser(
        description="Manage Claude Code plugin marketplace"
    )
    parser.add_argument(
        "command",
        choices=["validate", "add", "list"],
        help="Command to run"
    )
    parser.add_argument(
        "marketplace_path",
        help="Path to marketplace root"
    )
    parser.add_argument(
        "plugin_path",
        nargs="?",
        help="Path to plugin (for add command)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON"
    )

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
                    print(f"  [{status}] {p['name']} v{version}")
                    print(f"        {p.get('description', 'No description')[:60]}")
                    print(f"        Path: {p['path']}")
                    print()


if __name__ == "__main__":
    main()
