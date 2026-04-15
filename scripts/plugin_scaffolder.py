#!/usr/bin/env python3
"""
Scaffold new Claude Code plugin structure.

Creates the basic directory structure and files for a new plugin.

Usage:
    python plugin_scaffolder.py <name> [--output <dir>]
    python plugin_scaffolder.py my-plugin --output ./plugins/

Exit codes:
    0 - Success
    1 - Error
    2 - Usage error
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional


def _check_reserved_name(name: str) -> None:
    """Raise ValueError if name is reserved per data/version-manifest.json."""
    manifest_path = Path(__file__).parent.parent / "data" / "version-manifest.json"
    try:
        with open(manifest_path) as f:
            reserved = set(
                json.load(f)["schemas"]["marketplace_manifest"]["reserved_names"]
            )
    except (OSError, KeyError, json.JSONDecodeError):
        return  # graceful degradation; validator will still catch
    if name in reserved:
        raise ValueError(
            f"Marketplace name '{name}' is reserved by Anthropic. Choose a different name."
        )


def create_plugin_structure(
    name: str,
    output_dir: Path,
    description: str = "",
    author_name: str = "",
    author_email: str = "",
    marketplace: str = "standalone",
    marketplace_name: str = "",
) -> Path:
    """Create plugin directory structure."""
    plugin_dir = output_dir / name

    if plugin_dir.exists():
        raise ValueError(f"Directory already exists: {plugin_dir}")

    # Create directories
    (plugin_dir / ".claude-plugin").mkdir(parents=True)
    (plugin_dir / "skills").mkdir()
    (plugin_dir / "commands").mkdir()
    (plugin_dir / "agents").mkdir()
    (plugin_dir / "hooks").mkdir()
    (plugin_dir / ".claude").mkdir()

    # Create plugin.json
    manifest = {
        "name": name,
        "description": description or f"{name} plugin for Claude Code",
        "version": "1.0.0",
    }

    if author_name:
        manifest["author"] = {"name": author_name}
        if author_email:
            manifest["author"]["email"] = author_email

    manifest["keywords"] = []

    with open(plugin_dir / ".claude-plugin" / "plugin.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Create settings.local.json for development
    settings = {"permissions": {"allow": []}}
    with open(plugin_dir / ".claude" / "settings.local.json", "w") as f:
        json.dump(settings, f, indent=2)

    # Create a minimal skill as example
    example_skill_dir = plugin_dir / "skills" / "example"
    example_skill_dir.mkdir()

    skill_content = f"""---
name: {name}-example
description: Example skill for {name}. Use as a template for creating new skills.
---

# Example Skill

This is a placeholder skill. Replace with your actual skill content.

## Usage

Describe how to use this skill.

## Workflow

1. First step
2. Second step
"""
    (example_skill_dir / "SKILL.md").write_text(skill_content)

    # Create README
    readme_content = f"""# {name}

A Claude Code plugin.

## Installation

```bash
# From local marketplace
/plugin install {name}@your-marketplace

# Or for development
claude --plugin-dir ./{name}
```

## Contents

- **skills/** - Specialized knowledge skills
- **commands/** - Slash commands
- **agents/** - Autonomous subagents
- **hooks/** - Event hooks

## Development

1. Make changes to skills/commands/agents
2. Restart Claude Code to reload
3. Test with `--plugin-dir`

## License

MIT
"""
    (plugin_dir / "README.md").write_text(readme_content)

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

    return plugin_dir


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new Claude Code plugin")
    parser.add_argument("name", help="Plugin name (will be directory name)")
    parser.add_argument(
        "--output", "-o", default=".", help="Output directory (default: current)"
    )
    parser.add_argument("--description", "-d", default="", help="Plugin description")
    parser.add_argument("--author", default="", help="Author name")
    parser.add_argument("--email", default="", help="Author email")
    parser.add_argument(
        "--marketplace",
        choices=["standalone", "none"],
        default="standalone",
        help="Auto-create marketplace.json at plugin root (standalone, default) or skip (none)",
    )
    parser.add_argument(
        "--marketplace-name",
        default="",
        help="Marketplace name for standalone layout (default: plugin name)",
    )

    args = parser.parse_args()

    # Validate name
    if not args.name.replace("-", "").replace("_", "").isalnum():
        print(
            "Error: Plugin name must be alphanumeric with dashes/underscores",
            file=sys.stderr,
        )
        sys.exit(2)

    output_dir = Path(args.output).resolve()
    if not output_dir.exists():
        print(f"Error: Output directory does not exist: {output_dir}", file=sys.stderr)
        sys.exit(2)

    try:
        plugin_dir = create_plugin_structure(
            name=args.name,
            output_dir=output_dir,
            description=args.description,
            author_name=args.author,
            author_email=args.email,
            marketplace=args.marketplace,
            marketplace_name=args.marketplace_name,
        )
        print(f"Created plugin at: {plugin_dir}")
        print("\nNext steps:")
        print(f"  1. cd {plugin_dir}")
        print("  2. Edit skills/, commands/, or agents/")
        print(f"  3. Test with: claude --plugin-dir {plugin_dir}")
        if args.marketplace == "standalone":
            mk_name = args.marketplace_name or args.name
            print(f"  4. /plugin marketplace add {plugin_dir}")
            print(f"  5. /plugin install {args.name}@{mk_name}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
