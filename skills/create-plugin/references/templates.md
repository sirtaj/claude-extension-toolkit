# Plugin Templates

## Minimal (Command Only)

**plugin.json:**
```json
{"name": "my-plugin", "description": "A simple plugin", "author": {"name": "You", "email": "you@ex.com"}}
```

**commands/greet.md:**
```markdown
---
description: Greet the user
---
Say hello in a friendly way.
```

## Workflow (Commands + Agents)

**plugin.json:**
```json
{"name": "code-review", "description": "Code review workflow", "author": {"name": "You", "email": "you@ex.com"}, "version": "1.0.0"}
```

**commands/review.md:**
```markdown
---
description: Start code review
argument-hint: [file]
---
Review the code using the code-reviewer agent.
```

**agents/code-reviewer.md:**
```markdown
---
name: code-reviewer
description: Use for code review and quality analysis.
tools: ["Read", "Glob", "Grep"]
model: sonnet
color: blue
---

You are a code review specialist.

**Responsibilities:** Identify bugs, check best practices, suggest improvements.

**Output:** Summary, issues by severity, recommendations.
```

## Hook Plugin (Security)

**hooks/hooks.json:**
```json
{
  "description": "Security checks",
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{"type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/check.py", "timeout": 5}]
    }]
  }
}
```

**hooks/check.py:**
```python
#!/usr/bin/env python3
import json, os
tool_input = json.loads(os.environ.get("TOOL_INPUT", "{}"))
file_path = tool_input.get("file_path", "")
sensitive = [".env", "credentials", "secrets"]
if any(s in file_path.lower() for s in sensitive):
    print(json.dumps({"decision": "block", "reason": f"Sensitive file: {file_path}"}))
else:
    print(json.dumps({"decision": "approve"}))
```

## Skill Plugin

**skills/my-domain/SKILL.md:**
```markdown
---
name: my-domain
description: This skill should be used for [domain] expertise.
---

# My Domain

## Key Concepts
- Concept 1
- Concept 2

## Best Practices
1. Always X before Y
2. Consider Z when designing
```
