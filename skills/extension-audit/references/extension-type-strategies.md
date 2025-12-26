# Extension Type Strategies

Optimization approaches tailored to each Claude Code extension category.

## Technical Skills

### Characteristics
- Domain reference documentation
- API/component quick reference
- Progressive disclosure via references/
- Code examples

### Optimization Priorities

1. **Update for currency**
   - Web search latest API versions
   - Verify code examples still work
   - Check for deprecated features
   - Add newly available features

2. **Maintain reference structure**
   - Keep SKILL.md as quick reference
   - Detailed docs stay in references/
   - Progressive disclosure pattern

3. **Verify external links**
   - Check all documentation URLs
   - Update to current versions
   - Use official sources

### Currency Check Workflow

```
1. Web search: "[technology] documentation [year]"
2. Compare version in skill vs. current
3. If different:
   - Search for migration guide
   - Update code examples
   - Note breaking changes
4. Verify all external links resolve
```

### Expected Savings
Minimal token reduction focus. Priority is currency.

---

## Meta Skills

**Examples**: create-skill, create-command, create-agent, create-rules, claude-dev

### Characteristics
- Documentation about Claude Code itself
- Templates and examples
- Self-referential (skills about skills)
- Need to match current Claude Code capabilities

### Optimization Priorities

1. **Keep extremely lean**
   - These should be quick reference
   - Users invoke when creating, need fast answers
   - Heavy detail in references/ only

2. **Verify current patterns**
   - Web search Anthropic docs
   - Check Claude Code changelog
   - Ensure templates match current syntax

3. **Update for new features**
   - New frontmatter fields
   - New tool capabilities
   - Changed file locations

### Currency Check Sources

- `https://docs.anthropic.com/en/docs/claude-code/`
- Claude Code release notes
- Official examples repository

### Expected Savings
Focus on currency over token reduction.

---

## Utility Skills

### Characteristics
- Operational workflows
- Discrete phases with approval gates
- File manipulation
- Verification steps

### Optimization Priorities

1. **Simplify step sequences**
   - Remove over-explanation
   - Merge approval gates where appropriate
   - Streamline verification

2. **Reduce phase verbosity**
   - Each phase should be 3-5 steps
   - Avoid repeating instructions
   - Clear output format per phase

3. **Improve clarity**
   - Better section headers
   - Clearer completion criteria
   - Simpler approval prompts

---

## Summary Matrix

| Type | Token Priority | Currency Priority | Structure Priority |
|------|---------------|-------------------|-------------------|
| Technical | LOW | HIGH | LOW |
| Meta | MEDIUM | HIGH | LOW |
| Utility | MEDIUM | LOW | MEDIUM |

## Optimization Order

Recommended sequence for full audit:

1. **Technical skills** - Currency updates
2. **Meta skills** - Verify against current docs
3. **Utility skills** - Minor refinements
4. **Domain-specialist agents** - Verify expertise accuracy
5. **Task-runner agents** - Streamline workflows
6. **Collector agents** - Update data sources

---

# Agent Type Strategies

## Domain-Specialist Agents

### Characteristics
- Deep domain expertise in system prompt
- Detailed operational guidelines
- Often include code examples
- May specify model (haiku for speed, sonnet/opus for complexity)

### Optimization Priorities

1. **Verify domain accuracy**
   - Web search for updated APIs/frameworks
   - Check code examples still valid
   - Verify best practices current

2. **Optimize triggering examples**
   - Ensure examples cover common use cases
   - Remove redundant examples
   - Add missing edge cases

3. **Token efficiency in system prompt**
   - Convert verbose guidelines to tables
   - Remove obvious instructions
   - Condense repeated patterns

4. **Model selection review**
   - Haiku for simple, fast tasks
   - Sonnet for balanced needs
   - Opus for complex reasoning

---

## Task-Runner Agents

### Characteristics
- Specific operational workflows
- Clear input/output expectations
- Often integrate with external systems
- Tool access typically scoped

### Optimization Priorities

1. **Streamline workflow steps**
   - Merge redundant phases
   - Remove over-explanation
   - Clear completion criteria

2. **Verify tool access**
   - Ensure listed tools match needs
   - Remove unused tools
   - Add missing required tools

3. **Clarify output format**
   - Explicit output structure
   - Reduce ambiguity
   - Match user expectations

---

## Collector Agents

### Characteristics
- Web scraping/data aggregation
- External data sources
- Database/file updates
- Often need currency checks

### Optimization Priorities

1. **Verify data sources**
   - Check URLs still valid
   - Update scraping patterns if site changed
   - Verify output format matches expectations

2. **Update extraction patterns**
   - Web search for source changes
   - Test against current data
   - Handle new edge cases

3. **Streamline processing**
   - Simplify transformation logic
   - Clear error handling
   - Explicit update criteria

### Currency Check Workflow

```
1. Web fetch target sources
2. Compare structure vs. agent expectations
3. If different:
   - Update selectors/patterns
   - Adjust data transformation
   - Note breaking changes
4. Verify output format still correct
```

---

## Agent Summary Matrix

| Type | Token Priority | Currency Priority | Structure Priority |
|------|---------------|-------------------|-------------------|
| Domain-Specialist | MEDIUM | HIGH | MEDIUM |
| Task-Runner | HIGH | LOW | MEDIUM |
| Collector | LOW | HIGH | LOW |

---

# Command Strategies

## Text Transform Commands

**Examples**: eli5, summarize, fix-grammar, shorter, longer

### Characteristics
- Single input via `{}` placeholder
- Clear output directive
- Minimal instructions (5-10 lines)
- No multi-step workflows

### Optimization Priorities

1. **Maximize conciseness**
   - Each line should be essential
   - Remove redundant qualifiers
   - One instruction per line

2. **Clear output format**
   - Explicit "Return only..." directive
   - No ambiguity about output

3. **Placeholder usage**
   - `{}` should be in a clear context
   - Instruction should flow naturally with input

### Expected Size

| Metric | Target |
|--------|--------|
| Lines | 5-10 |
| Tokens | 50-100 |

---

## Action Commands

**Examples**: commit, review-pr, deploy

### Characteristics
- Multi-step workflows
- Tool usage instructions
- May have frontmatter for arguments
- Often interact with external systems

### Optimization Priorities

1. **Clear step sequence**
   - Numbered steps
   - Dependencies explicit
   - Parallel opportunities noted

2. **Tool guidance**
   - Specify which tools to use
   - Note tool-specific patterns

3. **Error handling**
   - What to do on failure
   - Rollback instructions if needed

---

# Hook Strategies

## Notification Hooks

### Characteristics
- Desktop alerts on events
- Quick feedback to user
- Non-blocking operations

### Optimization Priorities

1. **Appropriate timeouts**
   - Short (1-5s) for notifications
   - Longer only if needed

2. **Clear messages**
   - Concise notification text
   - Relevant icons

3. **Event selection**
   - `permission_prompt` for attention-required
   - `idle_prompt` for waiting states

---

## Tool Hooks (Pre/Post)

### Characteristics
- Intercept tool calls
- Validation or logging
- May modify behavior

### Optimization Priorities

1. **Matcher precision**
   - Specific tool patterns
   - Avoid overly broad matching

2. **Safety checks**
   - Non-destructive operations
   - Fail-safe on errors

3. **Performance**
   - Keep hooks fast
   - Avoid blocking operations

---

# Plugin Strategies

## Characteristics
- Bundle multiple extension types
- Shareable packages
- May include MCP servers

### Optimization Priorities

1. **Coherence**
   - All extensions serve plugin purpose
   - Clear naming convention
   - Shared patterns extracted

2. **Documentation**
   - README.md explains usage
   - Installation instructions
   - Dependency requirements

3. **Structure**
   - Standard directory layout
   - Valid plugin.json
   - Clean separation of concerns

### Standard Layout

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json
├── commands/
├── skills/
├── agents/
├── hooks/
│   └── hooks.json
├── .mcp.json (optional)
└── README.md
```

---

# CLAUDE.md Strategies

## Global CLAUDE.md

**Location**: `~/.claude/CLAUDE.md`

### Characteristics
- Cross-project preferences
- User-specific patterns
- File location references

### Optimization Priorities

1. **Keep minimal**
   - Only truly global rules
   - Avoid project-specific content

2. **Reference structure**
   - Point to skill/agent locations
   - Document directory layout

3. **User preferences**
   - Coding style preferences
   - Communication preferences

---

## Project CLAUDE.md

**Location**: `<project>/CLAUDE.md`

### Characteristics
- Project-specific rules
- Architecture documentation
- Available commands/tools

### Optimization Priorities

1. **Stay current**
   - Update when project changes
   - Remove deprecated rules
   - Match actual structure

2. **Appropriate scope**
   - Only project-relevant rules
   - Defer to global for general preferences

3. **Conciseness**
   - Terse rules, not explanations
   - Tables over prose
   - Links over inline docs

### Size Guidelines

| Project Type | Target Lines |
|--------------|--------------|
| Small | 50-100 |
| Medium | 100-200 |
| Large | 200-400 |
| Monorepo | 300-500 + nested files |

---

# Full Extension Summary Matrix

| Extension | Token Priority | Currency Priority | Structure Priority |
|-----------|---------------|-------------------|-------------------|
| Skills (Technical) | LOW | HIGH | LOW |
| Skills (Meta) | MEDIUM | HIGH | LOW |
| Skills (Utility) | MEDIUM | LOW | MEDIUM |
| Agents (Domain) | MEDIUM | HIGH | MEDIUM |
| Agents (Task) | HIGH | LOW | MEDIUM |
| Agents (Collector) | LOW | HIGH | LOW |
| Commands (Text) | HIGH | LOW | LOW |
| Commands (Action) | MEDIUM | MEDIUM | HIGH |
| Hooks | LOW | MEDIUM | MEDIUM |
| Plugins | MEDIUM | MEDIUM | HIGH |
| CLAUDE.md | MEDIUM | HIGH | MEDIUM |

---

# Optimization Order (Full Audit)

Recommended sequence:
1. **Text transform commands** - Quick wins
2. **Technical skills** - Currency updates
3. **Action commands** - Structure improvements
4. **Meta skills** - Match current docs
5. **Hooks** - Validate configuration
6. **Plugins** - Coherence check
7. **CLAUDE.md files** - Currency/staleness
8. **Agents** - Type-specific optimization
