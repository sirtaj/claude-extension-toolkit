# Optimization Patterns

Common transformations for reducing tokens while preserving functionality.

## Prose to Table

### When to Apply
- Listing features/options
- Describing tool usage
- Comparing alternatives
- Mapping inputs to outputs

### Pattern
```markdown
# Before (verbose)
When you need to search for files, use the Glob tool.
For searching content within files, use Grep. If you
need to read a specific file, use Read. For making
changes, use Edit.

# After (table)
| Need | Tool |
|------|------|
| Find files | Glob |
| Search content | Grep |
| Read file | Read |
| Edit file | Edit |
```

**Typical savings**: 40-60%

## Numbered Steps to Concise Flow

### When to Apply
- Workflow steps with excessive explanation
- Obvious sequences
- Steps that could be bullet points

### Pattern
```markdown
# Before (verbose)
### Step 1: Check Configuration
First, you should read the configuration file to
understand the current settings. This file contains
important parameters.

### Step 2: Search for Related Files
Next, search for any related files that might be
relevant to the task at hand.

### Step 3: Validate Input
Finally, validate the input parameters.

# After (concise)
### Initialize
1. Read config file for current settings
2. Search for related files
3. Validate input parameters
```

**Typical savings**: 50-70%

## Redundant Qualifier Removal

| Verbose | Concise |
|---------|---------|
| "You should consider using" | "Use" |
| "It is important to note that" | [delete] |
| "Make sure that you" | [delete or imperative] |
| "In order to" | "To" |
| "Prior to doing X" | "Before X" |
| "At this point in time" | "Now" |
| "In the event that" | "If" |
| "Due to the fact that" | "Because" |

**Savings**: 30-50%

## Example Trimming

### Keep
- Essential demonstration of concept
- Non-obvious usage patterns
- Input/output pairs

### Remove
- Commentary within examples
- Multiple examples of same pattern
- Obvious use cases
- Meta-explanation ("This example shows...")

### Pattern
```markdown
# Before (with commentary)
### Example Response
Here is an example of how you might respond to a
user question:

**User**: How do I create a skill?

**Response**: "Let me help you create a skill.
[reads documentation, searches examples]

Based on my analysis, here are the steps..."
[detailed 300-word response]

This example demonstrates reading docs first.

# After (minimal)
### Example
User: "How do I create a skill?"
Response: Read SKILL.md docs, show directory structure,
provide minimal template.
```

**Typical savings**: 60-80%

## Shared Pattern Extraction

### When to Apply
- Same content in 2+ extensions
- Identical workflows
- Common tool usage patterns

### Pattern
Create shared reference and link:

```markdown
# In each skill's SKILL.md
For API calls, follow the standard
[API patterns](../common/api-patterns.md#rest).

# In common/api-patterns.md
## REST API Calls {#rest}
1. Validate endpoint URL
2. Set appropriate headers
3. Handle response codes
4. Parse and validate response
```

**Typical savings**: 80-90% per duplicated section

## Section Consolidation

### When to Apply
- Multiple sections covering same ground
- "Always/Never" duplicating workflow
- Principles restating instructions

### Pattern
```markdown
# Before (separate sections)
## Workflow
1. Read configuration
2. Validate settings
3. Execute task
4. Report results

## Key Principles
### Always
- Read configuration before executing
- Validate settings

### Never
- Execute without reading config
- Skip validation

# After (consolidated)
## Workflow
1. Read configuration (required before execution)
2. Validate settings
3. Execute task
4. Report results
```

**Typical savings**: 40-60%

## Progressive Disclosure

### Move to references/
- Detailed API documentation
- Exhaustive domain lists
- Advanced techniques
- Edge case handling

### Keep in SKILL.md
- Core workflow (5-10 steps max)
- Quick reference tables
- When to use each tool
- Key principles (3-5 max)

### Pattern
```markdown
# In SKILL.md
## API Quick Reference
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/items | GET | List items |
| /api/v1/items | POST | Create item |

For complete API documentation, see
[references/api.md](references/api.md).

# In references/api.md
[Full 500-line API documentation]
```

**Typical savings**: 70-90% from SKILL.md

## Checklist for Each Transformation

Before applying any pattern:
- [ ] Preserve all essential information
- [ ] Maintain extension functionality
- [ ] Keep extension-specific voice (for personas)
- [ ] Test readability after change
- [ ] Verify no broken references
