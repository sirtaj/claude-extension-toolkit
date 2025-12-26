# Plugin Templates

## Minimal Plugin (Command Only)

**plugin.json**:
```json
{
  "name": "my-command-plugin",
  "description": "A simple command plugin",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  }
}
```

**commands/greet.md**:
```markdown
---
description: Greet the user
---

Say hello to the user in a friendly way.
```

---

## Workflow Plugin (Commands + Agents)

**plugin.json**:
```json
{
  "name": "code-review-plugin",
  "description": "Code review workflow with specialized agents",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "version": "1.0.0",
  "keywords": ["code-review", "quality"]
}
```

**commands/review.md**:
```markdown
---
description: Start a comprehensive code review
argument-hint: [file-or-directory]
---

Review the specified code for quality, bugs, and best practices.

Use the code-reviewer agent for detailed analysis.
```

**agents/code-reviewer.md**:
```markdown
---
name: code-reviewer
description: Use this agent for detailed code review, analyzing code quality, identifying bugs, and suggesting improvements.
tools: Read, Glob, Grep
model: sonnet
color: blue
---

# Code Reviewer Agent

## Role
Thorough code review specialist.

## Responsibilities
- Analyze code for bugs and issues
- Check for best practices adherence
- Identify performance concerns
- Suggest improvements

## Process
1. Read and understand the code
2. Check for common issues
3. Review against best practices
4. Provide actionable feedback

## Output
Structured review with:
- Summary of findings
- Issues by severity
- Specific recommendations
```

---

## Hook Plugin (Security/Automation)

**plugin.json**:
```json
{
  "name": "security-checks",
  "description": "Automated security checks before code changes",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  }
}
```

**hooks/hooks.json**:
```json
{
  "description": "Security validation before file edits",
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/security-check.py",
            "timeout": 5
          }
        ],
        "matcher": "Edit|Write|MultiEdit"
      }
    ]
  }
}
```

**hooks/security-check.py**:
```python
#!/usr/bin/env python3
import json
import os
import sys

def main():
    tool_input = json.loads(os.environ.get("TOOL_INPUT", "{}"))
    file_path = tool_input.get("file_path", "")

    # Block sensitive files
    sensitive = [".env", "credentials", "secrets", "private"]
    if any(s in file_path.lower() for s in sensitive):
        print(json.dumps({
            "decision": "block",
            "reason": f"Cannot modify sensitive file: {file_path}"
        }))
        return

    print(json.dumps({"decision": "approve"}))

if __name__ == "__main__":
    main()
```

---

## MCP Integration Plugin

**plugin.json**:
```json
{
  "name": "api-integration",
  "description": "Integration with external API via MCP",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "homepage": "https://example.com"
}
```

**.mcp.json**:
```json
{
  "mcpServers": {
    "my-api": {
      "type": "http",
      "url": "https://mcp.example.com/api"
    }
  }
}
```

**commands/api-query.md**:
```markdown
---
description: Query the integrated API
argument-hint: <query>
---

Use the my-api MCP server to process the query: $ARGUMENTS
```

---

## Full-Featured Plugin

**plugin.json**:
```json
{
  "name": "comprehensive-plugin",
  "description": "Full-featured plugin demonstrating all extension types",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "version": "1.0.0",
  "repository": "https://github.com/you/comprehensive-plugin",
  "license": "MIT",
  "keywords": ["example", "comprehensive"]
}
```

**Directory structure**:
```
comprehensive-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── setup.md           # /setup
│   └── deploy.md          # /deploy
├── agents/
│   ├── analyzer.md        # Deep analysis
│   └── generator.md       # Code generation
├── skills/
│   └── domain-expert/
│       ├── SKILL.md       # Domain knowledge
│       └── references/
│           └── patterns.md
├── hooks/
│   ├── hooks.json
│   └── validator.py
├── .mcp.json              # API integration
└── README.md
```

---

## Skill Plugin

**plugin.json**:
```json
{
  "name": "domain-expertise",
  "description": "Domain-specific expertise and best practices",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  }
}
```

**skills/my-domain/SKILL.md**:
```markdown
---
name: my-domain
description: This skill should be used when working with [domain] or when the user needs expertise in [area].
---

# My Domain Expertise

## Purpose
Provide specialized knowledge for [domain].

## Key Concepts
- Concept 1: Description
- Concept 2: Description

## Best Practices
1. Always do X before Y
2. Consider Z when designing

## Common Patterns
- Pattern A for situation X
- Pattern B for situation Y

## Resources
- `references/api.md` - API documentation
- `references/patterns.md` - Detailed patterns
```
