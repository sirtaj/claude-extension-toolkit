---
description: Sync toolkit schemas with latest Claude Code docs and check for staleness
allowed-tools:
  - Bash
  - Read
---

Run the extension toolkit sync workflow:

1. Execute `${CLAUDE_PLUGIN_ROOT}/scripts/docs_fetcher.py sync` to fetch latest canonical docs
2. Execute `${CLAUDE_PLUGIN_ROOT}/scripts/docs_fetcher.py update-schemas` to regenerate schema definitions
3. Execute `${CLAUDE_PLUGIN_ROOT}/scripts/validate_extension.py --all` to check extensions against new schemas
4. Execute `${CLAUDE_PLUGIN_ROOT}/scripts/pattern_detector.py --all` to detect newly-deprecated patterns

Report what changed: new fields, new hook events, new deprecations. If any extensions have issues, suggest running the extension-auditor agent for fixes.
