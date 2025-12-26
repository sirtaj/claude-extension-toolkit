# Plugin Lifecycle

## Installation

```bash
# From marketplace
/plugin install plugin-name@claude-plugins-official

# Local development
claude --plugin-dir /path/to/my-plugin

# Project-local
cp -r my-plugin .claude-plugin/
```

## Testing

```bash
# 1. Create structure
mkdir -p my-plugin/.claude-plugin
echo '{"name":"my-plugin","description":"Test","author":{"name":"Me","email":"me@ex.com"}}' > my-plugin/.claude-plugin/plugin.json

# 2. Add components, then test
claude --plugin-dir ./my-plugin

# 3. Verify
/plugins        # List active plugins
/my-command     # Test commands
```

## Publishing to Marketplace

1. Fork `anthropics/claude-plugins-official`
2. Add plugin to `plugins/` or `external_plugins/`
3. Add entry to `marketplace.json`:
   ```json
   {"name": "my-plugin", "description": "...", "author": {...}, "source": "./plugins/my-plugin", "category": "development"}
   ```
4. Submit PR

**Categories:** development, productivity, learning, security, integration, language

## Version Management

Use semantic versioning: `"version": "1.2.3"`
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## Troubleshooting

| Issue | Check |
|-------|-------|
| Not loading | Valid plugin.json, required fields |
| Commands missing | Files in `commands/`, `.md` extension |
| Hooks not firing | hooks.json syntax, `${CLAUDE_PLUGIN_ROOT}` paths |
