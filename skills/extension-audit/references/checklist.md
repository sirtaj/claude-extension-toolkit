# Audit Checklist

## All Extensions

| Check | Look For |
|-------|----------|
| Token efficiency | Prose→tables, verbose examples, redundancy |
| Structure | Clear hierarchy, progressive disclosure |
| Currency | API versions, working links |

## Skills

| Metric | Target | Red Flag |
|--------|--------|----------|
| SKILL.md | 500-1500 tokens | >3000 |
| references/ | Used if >300 lines | Missing when needed |

**Checks**: Frontmatter (name, description), progressive disclosure, persona voice consistency

## Agents

| Metric | Target | Red Flag |
|--------|--------|----------|
| Total | 1000-2000 tokens | >3000 |
| Description | 2-4 examples | Missing examples |

**Checks**: Triggering examples with commentary, appropriate model (haiku/sonnet/opus), scoped tool access

## Commands

| Metric | Target | Red Flag |
|--------|--------|----------|
| Lines | 5-15 | >20 |
| Tokens | 50-150 | >200 |

**Checks**: Clear purpose, `{}` placeholder for text transforms, explicit output format

## Hooks

**Valid events**: PreToolUse, PostToolUse, Stop, SessionStart, UserPromptSubmit

**Checks**: Safe commands (no rm/sudo), reasonable timeout (1-30s), correct matcher patterns

## Plugins

**Checks**: Valid plugin.json (name, description, author), coherent bundle, README.md

## CLAUDE.md

| Scope | Target Lines |
|-------|--------------|
| Small project | 50-100 |
| Medium | 100-200 |
| Large | 200-400 |

**Checks**: No stale rules, matches project structure, concise (terse rules, not explanations)
