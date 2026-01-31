#!/usr/bin/env python3
"""
Validate Claude Code extension structure and frontmatter.

Usage:
    python validate_extension.py <path>           # Validate single file/directory
    python validate_extension.py --all            # Validate all extensions
    python validate_extension.py --type skills    # Validate specific type
    python validate_extension.py --schema         # Validate against version manifest

Exit codes:
    0 - All validations passed
    1 - Validation errors found
    2 - Usage error
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).parent
TOOLKIT_ROOT = SCRIPT_DIR.parent
CLAUDE_DIR = Path.home() / ".claude"
MANIFEST_PATH = TOOLKIT_ROOT / "data" / "version-manifest.json"


def load_schemas() -> Dict:
    """Load schema definitions from version manifest."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            manifest = json.load(f)
            return manifest.get("schemas", {})
    return {}


# Load schemas from manifest if available, otherwise use defaults
_SCHEMAS = load_schemas()

EXTENSION_TYPES = {
    "skills": {
        "pattern": "**/SKILL.md",
        "required_frontmatter": _SCHEMAS.get("skill_frontmatter", {}).get(
            "required", ["name", "description"]
        ),
        "optional_frontmatter": _SCHEMAS.get("skill_frontmatter", {}).get(
            "optional", ["allowed-tools", "model", "context", "agent", "hooks",
                        "argument-hint", "disable-model-invocation", "user-invocable"]
        ),
    },
    "agents": {
        "pattern": "*.md",
        "required_frontmatter": _SCHEMAS.get("agent_frontmatter", {}).get(
            "required", ["name", "description"]
        ),
        "optional_frontmatter": _SCHEMAS.get("agent_frontmatter", {}).get(
            "optional", ["tools", "disallowedTools", "model", "color", "hooks",
                        "permissionMode", "skills"]
        ),
    },
    "commands": {
        "pattern": "*.md",
        "required_frontmatter": _SCHEMAS.get("command_frontmatter", {}).get(
            "required", []
        ),
        "optional_frontmatter": _SCHEMAS.get("command_frontmatter", {}).get(
            "optional", ["description", "allowed-tools", "model", "argument-hint"]
        ),
    },
}

VALID_AGENT_COLORS = _SCHEMAS.get("hooks", {}).get(
    "valid_colors", ["blue", "cyan", "green", "yellow", "magenta", "red"]
)
VALID_MODELS = _SCHEMAS.get("hooks", {}).get(
    "valid_models", ["sonnet", "opus", "haiku"]
)
VALID_HOOK_EVENTS = _SCHEMAS.get("hooks", {}).get(
    "events", ["PreToolUse", "PostToolUse", "Stop", "UserPromptSubmit",
              "SessionStart", "SessionEnd", "PermissionRequest",
              "PostToolUseFailure", "Notification", "SubagentStart",
              "SubagentStop", "PreCompact"]
)


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    path: str
    extension_type: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def parse_frontmatter(content: str) -> Tuple[Optional[dict], str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content

    frontmatter_text = parts[1].strip()
    body = parts[2]

    # Simple YAML parsing (key: value)
    frontmatter = {}
    current_key = None
    current_list = None

    for line in frontmatter_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check for list item
        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
                frontmatter[current_key] = current_list
            current_list.append(stripped[2:].strip())
            continue

        # Check for key: value
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            current_key = key
            current_list = None

            if value:
                # Handle quoted strings
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                # Handle booleans
                elif value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                frontmatter[key] = value

    return frontmatter, body


def validate_skill(path: Path) -> ValidationResult:
    """Validate a skill (SKILL.md)."""
    result = ValidationResult(str(path), "skill")

    try:
        content = path.read_text()
    except Exception as e:
        result.errors.append(f"Cannot read file: {e}")
        return result

    frontmatter, body = parse_frontmatter(content)

    # Check frontmatter exists
    if frontmatter is None:
        result.errors.append("Missing YAML frontmatter (must start with ---)")
        return result

    # Required fields
    if "name" not in frontmatter:
        result.errors.append("Missing required frontmatter: 'name'")
    if "description" not in frontmatter:
        result.errors.append("Missing required frontmatter: 'description'")

    # Validate description length
    desc = frontmatter.get("description", "")
    if isinstance(desc, str) and len(desc) > 500:
        result.warnings.append(f"Description is long ({len(desc)} chars), consider shortening")

    # Check for references directory
    references_dir = path.parent / "references"
    if references_dir.exists():
        ref_files = list(references_dir.glob("*.md"))
        if not ref_files:
            result.warnings.append("Empty references/ directory")

    # Check body has content
    if len(body.strip()) < 50:
        result.warnings.append("Skill body is very short")

    # Check for model if specified
    if "model" in frontmatter:
        model = frontmatter["model"]
        if model not in VALID_MODELS:
            result.errors.append(f"Invalid model '{model}', must be one of: {VALID_MODELS}")

    return result


def validate_agent(path: Path) -> ValidationResult:
    """Validate an agent definition."""
    result = ValidationResult(str(path), "agent")

    try:
        content = path.read_text()
    except Exception as e:
        result.errors.append(f"Cannot read file: {e}")
        return result

    frontmatter, body = parse_frontmatter(content)

    if frontmatter is None:
        result.errors.append("Missing YAML frontmatter (must start with ---)")
        return result

    # Required fields
    if "name" not in frontmatter:
        result.errors.append("Missing required frontmatter: 'name'")
    if "description" not in frontmatter:
        result.errors.append("Missing required frontmatter: 'description'")

    # Validate color
    if "color" in frontmatter:
        color = frontmatter["color"]
        if color not in VALID_AGENT_COLORS:
            result.errors.append(f"Invalid color '{color}', must be one of: {VALID_AGENT_COLORS}")

    # Validate model
    if "model" in frontmatter:
        model = frontmatter["model"]
        if model not in VALID_MODELS:
            result.errors.append(f"Invalid model '{model}', must be one of: {VALID_MODELS}")

    # Check description has examples
    desc = frontmatter.get("description", "")
    if isinstance(desc, str) and "<example>" not in desc:
        result.warnings.append("Agent description should include <example> blocks for better triggering")

    return result


def validate_command(path: Path) -> ValidationResult:
    """Validate a command definition."""
    result = ValidationResult(str(path), "command")

    try:
        content = path.read_text()
    except Exception as e:
        result.errors.append(f"Cannot read file: {e}")
        return result

    frontmatter, body = parse_frontmatter(content)

    # Commands don't require frontmatter but if present, validate it
    if frontmatter:
        if "model" in frontmatter:
            model = frontmatter["model"]
            if model not in VALID_MODELS:
                result.errors.append(f"Invalid model '{model}', must be one of: {VALID_MODELS}")

    # Check body has content
    if len(body.strip()) < 10:
        result.warnings.append("Command body is very short")

    return result


def validate_plugin(path: Path) -> ValidationResult:
    """Validate a plugin structure."""
    result = ValidationResult(str(path), "plugin")

    plugin_json = path / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        result.errors.append("Missing .claude-plugin/plugin.json")
        return result

    try:
        with open(plugin_json) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        result.errors.append(f"Invalid plugin.json: {e}")
        return result

    # Required fields
    if "name" not in manifest:
        result.errors.append("Missing 'name' in plugin.json")
    if "description" not in manifest:
        result.errors.append("Missing 'description' in plugin.json")

    # Check bundled components exist
    for component in ["skills", "commands", "agents", "hooks"]:
        component_dir = path / component
        if component_dir.exists() and not any(component_dir.iterdir()):
            result.warnings.append(f"Empty {component}/ directory")

    return result


def validate_hooks_json(path: Path) -> ValidationResult:
    """Validate a hooks.json file."""
    result = ValidationResult(str(path), "hooks")

    try:
        with open(path) as f:
            hooks = json.load(f)
    except json.JSONDecodeError as e:
        result.errors.append(f"Invalid JSON: {e}")
        return result

    for event, handlers in hooks.items():
        if event not in VALID_HOOK_EVENTS:
            result.warnings.append(f"Unknown hook event: '{event}'")

        if not isinstance(handlers, list):
            result.errors.append(f"Hook handlers for '{event}' must be a list")
            continue

        for handler in handlers:
            if "command" not in handler:
                result.errors.append(f"Hook handler missing 'command' in '{event}'")

    return result


def find_extensions(base_dir: Path, ext_type: str) -> List[Path]:
    """Find all extensions of a given type."""
    extensions = []

    if ext_type == "skills":
        for skill_md in base_dir.rglob("SKILL.md"):
            extensions.append(skill_md)
    elif ext_type == "agents":
        agents_dir = base_dir / "agents"
        if agents_dir.exists():
            extensions.extend(agents_dir.glob("*.md"))
    elif ext_type == "commands":
        commands_dir = base_dir / "commands"
        if commands_dir.exists():
            extensions.extend(commands_dir.glob("*.md"))
    elif ext_type == "plugins":
        plugins_dir = base_dir / "plugins"
        if plugins_dir.exists():
            for item in plugins_dir.iterdir():
                if item.is_dir() and (item / ".claude-plugin").exists():
                    extensions.append(item)
    elif ext_type == "hooks":
        # Check settings.json and hooks.json files
        settings = base_dir / "settings.json"
        if settings.exists():
            extensions.append(settings)
        for hooks_json in base_dir.rglob("hooks.json"):
            extensions.append(hooks_json)

    return extensions


def validate_all(base_dir: Path, ext_type: Optional[str] = None) -> List[ValidationResult]:
    """Validate all extensions in a directory."""
    results = []

    types_to_check = [ext_type] if ext_type else ["skills", "agents", "commands", "plugins", "hooks"]

    for t in types_to_check:
        extensions = find_extensions(base_dir, t)
        for ext in extensions:
            if t == "skills":
                results.append(validate_skill(ext))
            elif t == "agents":
                results.append(validate_agent(ext))
            elif t == "commands":
                results.append(validate_command(ext))
            elif t == "plugins":
                results.append(validate_plugin(ext))
            elif t == "hooks":
                results.append(validate_hooks_json(ext))

    return results


def print_results(results: List[ValidationResult]) -> int:
    """Print validation results and return exit code."""
    has_errors = False

    for result in results:
        if result.errors or result.warnings:
            status = "FAIL" if result.errors else "WARN"
            print(f"\n[{status}] {result.extension_type}: {result.path}")

            for error in result.errors:
                print(f"  ERROR: {error}")
                has_errors = True

            for warning in result.warnings:
                print(f"  WARN:  {warning}")

    # Summary
    total = len(results)
    errors = sum(1 for r in results if r.errors)
    warnings = sum(1 for r in results if r.warnings and not r.errors)
    valid = total - errors - warnings

    print(f"\n{'='*50}")
    print(f"Validated {total} extensions: {valid} valid, {warnings} warnings, {errors} errors")

    return 1 if has_errors else 0


def main():
    parser = argparse.ArgumentParser(description="Validate Claude Code extensions")
    parser.add_argument("path", nargs="?", help="Path to validate")
    parser.add_argument("--all", action="store_true", help="Validate all extensions in ~/.claude")
    parser.add_argument("--type", choices=["skills", "agents", "commands", "plugins", "hooks"],
                        help="Validate only specific extension type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.all:
        results = validate_all(CLAUDE_DIR, args.type)
    elif args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            sys.exit(2)

        if path.is_file():
            if path.name == "SKILL.md":
                results = [validate_skill(path)]
            elif path.name == "hooks.json":
                results = [validate_hooks_json(path)]
            elif path.suffix == ".md":
                # Try to determine type from parent directory
                parent = path.parent.name
                if parent == "agents" or "agents" in str(path):
                    results = [validate_agent(path)]
                elif parent == "commands" or "commands" in str(path):
                    results = [validate_command(path)]
                else:
                    results = [validate_skill(path)]
        else:
            results = validate_all(path, args.type)
    else:
        parser.print_help()
        sys.exit(2)

    if args.json:
        output = [
            {
                "path": r.path,
                "type": r.extension_type,
                "valid": r.is_valid,
                "errors": r.errors,
                "warnings": r.warnings,
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
        sys.exit(0 if all(r.is_valid for r in results) else 1)
    else:
        sys.exit(print_results(results))


if __name__ == "__main__":
    main()
