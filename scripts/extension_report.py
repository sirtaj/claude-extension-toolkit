#!/usr/bin/env python3
"""
Generate a comprehensive report of all installed Claude Code extensions.

Provides an overview of:
- All skills, agents, commands, plugins, hooks
- Token counts and size analysis
- Modification dates
- Structural issues

Usage:
    python extension_report.py              # Full report
    python extension_report.py --summary    # Summary only
    python extension_report.py --type skills  # Specific type
    python extension_report.py --json       # JSON output

Exit codes:
    0 - Success
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

CLAUDE_DIR = Path.home() / ".claude"
AI_DIR = Path.home() / "sirtaj-notes" / "3-Resources" / "AI"

CHARS_PER_TOKEN = 4


@dataclass
class Extension:
    """An individual extension."""
    name: str
    path: str
    extension_type: str
    subtype: str = ""
    tokens: int = 0
    chars: int = 0
    files: int = 1
    modified: str = ""
    source: str = ""  # "claude" or "ai"
    issues: List[str] = field(default_factory=list)


@dataclass
class Report:
    """Full extension report."""
    generated_at: str
    skills: List[Extension] = field(default_factory=list)
    agents: List[Extension] = field(default_factory=list)
    commands: List[Extension] = field(default_factory=list)
    plugins: List[Extension] = field(default_factory=list)
    hooks: List[Extension] = field(default_factory=list)
    claude_md: List[Extension] = field(default_factory=list)

    @property
    def total_extensions(self) -> int:
        return (len(self.skills) + len(self.agents) + len(self.commands) +
                len(self.plugins) + len(self.hooks) + len(self.claude_md))

    @property
    def total_tokens(self) -> int:
        all_ext = self.skills + self.agents + self.commands + self.plugins
        return sum(e.tokens for e in all_ext)


def get_mtime(path: Path) -> str:
    """Get modification time as ISO string."""
    try:
        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "unknown"


def count_tokens(path: Path) -> int:
    """Count tokens in a file."""
    try:
        return len(path.read_text()) // CHARS_PER_TOKEN
    except Exception:
        return 0


def parse_frontmatter_name(path: Path) -> Optional[str]:
    """Extract name from frontmatter."""
    try:
        content = path.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                for line in parts[1].split("\n"):
                    if line.startswith("name:"):
                        return line.split(":", 1)[1].strip().strip("\"'")
    except Exception:
        pass
    return None


def classify_skill_subtype(content: str) -> str:
    """Classify skill subtype based on content patterns."""
    content_lower = content.lower()

    if any(x in content_lower for x in ["persona", "advisor", "coach", "expert"]):
        return "persona"
    elif any(x in content_lower for x in ["api", "integration", "reference"]):
        return "technical"
    elif any(x in content_lower for x in ["create-", "build", "generate"]):
        return "meta"
    else:
        return "utility"


def scan_skills(base_dir: Path, source: str) -> List[Extension]:
    """Scan for skills."""
    skills = []

    for skill_md in base_dir.rglob("SKILL.md"):
        skill_dir = skill_md.parent
        name = parse_frontmatter_name(skill_md) or skill_dir.name

        try:
            content = skill_md.read_text()
            chars = len(content)
            tokens = chars // CHARS_PER_TOKEN
            subtype = classify_skill_subtype(content)
        except Exception:
            chars = tokens = 0
            subtype = "unknown"

        # Count references
        file_count = 1
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            ref_files = list(refs_dir.glob("*.md"))
            file_count += len(ref_files)
            for ref in ref_files:
                tokens += count_tokens(ref)

        ext = Extension(
            name=name,
            path=str(skill_md),
            extension_type="skill",
            subtype=subtype,
            tokens=tokens,
            chars=chars,
            files=file_count,
            modified=get_mtime(skill_md),
            source=source,
        )
        skills.append(ext)

    return skills


def scan_agents(base_dir: Path, source: str) -> List[Extension]:
    """Scan for agents."""
    agents = []
    agents_dir = base_dir / "agents"

    if not agents_dir.exists():
        return agents

    for agent_md in agents_dir.glob("*.md"):
        name = parse_frontmatter_name(agent_md) or agent_md.stem
        tokens = count_tokens(agent_md)

        ext = Extension(
            name=name,
            path=str(agent_md),
            extension_type="agent",
            tokens=tokens,
            modified=get_mtime(agent_md),
            source=source,
        )
        agents.append(ext)

    return agents


def scan_commands(base_dir: Path, source: str) -> List[Extension]:
    """Scan for commands."""
    commands = []
    commands_dir = base_dir / "commands"

    if not commands_dir.exists():
        return commands

    for cmd_md in commands_dir.glob("*.md"):
        name = cmd_md.stem
        tokens = count_tokens(cmd_md)

        ext = Extension(
            name=name,
            path=str(cmd_md),
            extension_type="command",
            tokens=tokens,
            modified=get_mtime(cmd_md),
            source=source,
        )
        commands.append(ext)

    return commands


def scan_plugins(base_dir: Path, source: str) -> List[Extension]:
    """Scan for plugins."""
    plugins = []
    plugins_dir = base_dir / "plugins"

    if not plugins_dir.exists():
        return plugins

    for item in plugins_dir.iterdir():
        if not item.is_dir():
            continue

        plugin_json = item / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            continue

        try:
            with open(plugin_json) as f:
                manifest = json.load(f)
            name = manifest.get("name", item.name)
        except Exception:
            name = item.name

        # Count all files and tokens
        total_tokens = 0
        file_count = 0

        for md_file in item.rglob("*.md"):
            total_tokens += count_tokens(md_file)
            file_count += 1

        for json_file in item.rglob("*.json"):
            total_tokens += count_tokens(json_file)
            file_count += 1

        ext = Extension(
            name=name,
            path=str(item),
            extension_type="plugin",
            tokens=total_tokens,
            files=file_count,
            modified=get_mtime(plugin_json),
            source=source,
        )
        plugins.append(ext)

    return plugins


def scan_hooks(base_dir: Path, source: str) -> List[Extension]:
    """Scan for hooks configuration."""
    hooks = []

    settings_json = base_dir / "settings.json"
    if settings_json.exists():
        try:
            with open(settings_json) as f:
                settings = json.load(f)

            if "hooks" in settings:
                hook_count = sum(len(v) if isinstance(v, list) else 1
                                 for v in settings["hooks"].values())
                ext = Extension(
                    name="settings.json hooks",
                    path=str(settings_json),
                    extension_type="hooks",
                    subtype=f"{hook_count} hooks",
                    modified=get_mtime(settings_json),
                    source=source,
                )
                hooks.append(ext)
        except Exception:
            pass

    # Check for hookify rules
    hookify_rules = list(base_dir.glob("hookify.*.local.md"))
    for rule in hookify_rules:
        ext = Extension(
            name=rule.stem,
            path=str(rule),
            extension_type="hooks",
            subtype="hookify",
            tokens=count_tokens(rule),
            modified=get_mtime(rule),
            source=source,
        )
        hooks.append(ext)

    return hooks


def scan_claude_md(base_dir: Path, source: str) -> List[Extension]:
    """Scan for CLAUDE.md files."""
    claude_mds = []

    for claude_md in base_dir.rglob("CLAUDE.md"):
        # Skip if in plugins
        if "plugins" in str(claude_md):
            continue

        tokens = count_tokens(claude_md)

        # Determine scope
        if claude_md.parent == base_dir:
            scope = "global" if base_dir == CLAUDE_DIR else "source"
        else:
            scope = "nested"

        ext = Extension(
            name=str(claude_md.relative_to(base_dir)),
            path=str(claude_md),
            extension_type="claude_md",
            subtype=scope,
            tokens=tokens,
            modified=get_mtime(claude_md),
            source=source,
        )
        claude_mds.append(ext)

    return claude_mds


def generate_report() -> Report:
    """Generate a full extension report."""
    report = Report(
        generated_at=datetime.now().isoformat(),
    )

    # Scan ~/.claude
    report.skills.extend(scan_skills(CLAUDE_DIR, "claude"))
    report.agents.extend(scan_agents(CLAUDE_DIR, "claude"))
    report.commands.extend(scan_commands(CLAUDE_DIR, "claude"))
    report.plugins.extend(scan_plugins(CLAUDE_DIR, "claude"))
    report.hooks.extend(scan_hooks(CLAUDE_DIR, "claude"))
    report.claude_md.extend(scan_claude_md(CLAUDE_DIR, "claude"))

    # Scan AI directory if exists
    if AI_DIR.exists():
        report.skills.extend(scan_skills(AI_DIR, "ai"))
        report.agents.extend(scan_agents(AI_DIR, "ai"))
        report.commands.extend(scan_commands(AI_DIR, "ai"))
        report.plugins.extend(scan_plugins(AI_DIR, "ai"))
        report.claude_md.extend(scan_claude_md(AI_DIR, "ai"))

    return report


def print_table(title: str, extensions: List[Extension], show_tokens: bool = True):
    """Print a formatted table of extensions."""
    if not extensions:
        return

    print(f"\n## {title} ({len(extensions)})")
    print("-" * 60)

    if show_tokens:
        print(f"{'Name':<30} {'Tokens':>8} {'Files':>6} {'Modified':<16}")
        print("-" * 60)
        for ext in sorted(extensions, key=lambda x: -x.tokens):
            subtype = f" [{ext.subtype}]" if ext.subtype else ""
            name = f"{ext.name}{subtype}"[:30]
            print(f"{name:<30} {ext.tokens:>8} {ext.files:>6} {ext.modified:<16}")
    else:
        print(f"{'Name':<40} {'Modified':<16}")
        print("-" * 60)
        for ext in extensions:
            subtype = f" [{ext.subtype}]" if ext.subtype else ""
            name = f"{ext.name}{subtype}"[:40]
            print(f"{name:<40} {ext.modified:<16}")


def print_report(report: Report, summary_only: bool = False):
    """Print the full report."""
    print("=" * 60)
    print("CLAUDE CODE EXTENSION REPORT")
    print(f"Generated: {report.generated_at}")
    print("=" * 60)

    print(f"\nTotal Extensions: {report.total_extensions}")
    print(f"Total Tokens: {report.total_tokens:,}")

    print(f"\n  Skills:   {len(report.skills):>3}")
    print(f"  Agents:   {len(report.agents):>3}")
    print(f"  Commands: {len(report.commands):>3}")
    print(f"  Plugins:  {len(report.plugins):>3}")
    print(f"  Hooks:    {len(report.hooks):>3}")
    print(f"  CLAUDE.md:{len(report.claude_md):>3}")

    if summary_only:
        return

    print_table("Skills", report.skills)
    print_table("Agents", report.agents)
    print_table("Commands", report.commands)
    print_table("Plugins", report.plugins)
    print_table("Hooks", report.hooks, show_tokens=False)
    print_table("CLAUDE.md Files", report.claude_md)

    print("\n" + "=" * 60)


def report_to_dict(report: Report) -> Dict[str, Any]:
    """Convert report to dictionary for JSON output."""
    def ext_to_dict(e: Extension) -> Dict[str, Any]:
        return {
            "name": e.name,
            "path": e.path,
            "type": e.extension_type,
            "subtype": e.subtype,
            "tokens": e.tokens,
            "chars": e.chars,
            "files": e.files,
            "modified": e.modified,
            "source": e.source,
            "issues": e.issues,
        }

    return {
        "generated_at": report.generated_at,
        "summary": {
            "total_extensions": report.total_extensions,
            "total_tokens": report.total_tokens,
            "skills": len(report.skills),
            "agents": len(report.agents),
            "commands": len(report.commands),
            "plugins": len(report.plugins),
            "hooks": len(report.hooks),
            "claude_md": len(report.claude_md),
        },
        "skills": [ext_to_dict(e) for e in report.skills],
        "agents": [ext_to_dict(e) for e in report.agents],
        "commands": [ext_to_dict(e) for e in report.commands],
        "plugins": [ext_to_dict(e) for e in report.plugins],
        "hooks": [ext_to_dict(e) for e in report.hooks],
        "claude_md": [ext_to_dict(e) for e in report.claude_md],
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Claude Code extension report")
    parser.add_argument("--summary", action="store_true", help="Summary only")
    parser.add_argument("--type", choices=["skills", "agents", "commands", "plugins", "hooks", "claude_md"],
                        help="Report on specific type only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--markdown", action="store_true", help="Output as Markdown")

    args = parser.parse_args()

    report = generate_report()

    if args.json:
        print(json.dumps(report_to_dict(report), indent=2))
    elif args.type:
        # Print specific type only
        type_map = {
            "skills": report.skills,
            "agents": report.agents,
            "commands": report.commands,
            "plugins": report.plugins,
            "hooks": report.hooks,
            "claude_md": report.claude_md,
        }
        print_table(args.type.title(), type_map[args.type])
    else:
        print_report(report, args.summary)


if __name__ == "__main__":
    main()
