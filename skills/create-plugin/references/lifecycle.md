# Plugin Lifecycle

## Installation Methods

### From Marketplace

```bash
# Install from official marketplace
/plugin install plugin-name@claude-plugins-official

# Install specific version
/plugin install plugin-name@marketplace --version 1.2.0
```

### Local Development

```bash
# Test plugin during development
claude --plugin-dir /path/to/my-plugin

# Multiple plugins
claude --plugin-dir ./plugin1 --plugin-dir ./plugin2
```

### Project-Local

Copy plugin to `.claude-plugin/` in project root:

```bash
cp -r my-plugin .claude-plugin/
```

This makes the plugin available only within that project.

## Testing Locally

1. **Create plugin structure**:
   ```bash
   mkdir -p my-plugin/.claude-plugin
   echo '{"name":"my-plugin","description":"Test","author":{"name":"Me","email":"me@example.com"}}' > my-plugin/.claude-plugin/plugin.json
   ```

2. **Add components** (commands, agents, etc.)

3. **Test with Claude**:
   ```bash
   claude --plugin-dir ./my-plugin
   ```

4. **Verify loading**:
   ```
   /plugins          # List active plugins
   /my-command       # Test your commands
   ```

## Update Workflow

### Marketplace Plugins

Marketplace plugins update automatically when new versions are released.

```bash
# Check for updates
/plugin update

# Update specific plugin
/plugin update plugin-name@marketplace
```

### Local Plugins

Manual update via git or file copy:

```bash
cd /path/to/my-plugin
git pull origin main
```

## Publishing to Marketplace

### Prerequisites

1. Valid plugin.json with all required fields
2. Comprehensive README.md
3. All components tested and working
4. License file (recommended)

### Submission Process

1. **Fork the marketplace repository**:
   ```bash
   gh repo fork anthropics/claude-plugins-official
   ```

2. **Add your plugin**:
   ```bash
   # For first-party (Anthropic) plugins
   cp -r my-plugin plugins/my-plugin

   # For third-party (external) plugins
   cp -r my-plugin external_plugins/my-plugin
   ```

3. **Create marketplace entry** in root `marketplace.json`:
   ```json
   {
     "name": "my-plugin",
     "description": "Clear description of what it does",
     "author": {
       "name": "Your Name",
       "email": "you@example.com"
     },
     "source": "./plugins/my-plugin",
     "category": "development",
     "homepage": "https://github.com/you/my-plugin"
   }
   ```

4. **Submit PR**:
   ```bash
   gh pr create --title "Add my-plugin" --body "Description of the plugin..."
   ```

### Categories

- `development` - Dev tools, code quality
- `productivity` - Workflow automation
- `learning` - Educational tools
- `security` - Security scanning, auditing
- `integration` - External service integrations
- `language` - Language/framework specific

## Version Management

### Semantic Versioning

Use semantic versioning in plugin.json:

```json
{
  "version": "1.2.3"
}
```

- **MAJOR** (1.x.x): Breaking changes
- **MINOR** (x.2.x): New features, backward compatible
- **PATCH** (x.x.3): Bug fixes

### Changelog

Maintain a CHANGELOG.md:

```markdown
# Changelog

## [1.1.0] - 2025-01-15
### Added
- New command /analyze
- Security hook for file edits

### Fixed
- Agent timeout issue

## [1.0.0] - 2025-01-01
- Initial release
```

## Uninstalling

```bash
# Uninstall from marketplace
/plugin uninstall plugin-name@marketplace

# Remove project-local
rm -rf .claude-plugin/
```

## Troubleshooting

### Plugin Not Loading

1. Check plugin.json is valid JSON
2. Verify required fields (name, description, author)
3. Check directory structure matches expected layout

### Commands Not Found

1. Verify commands are in `commands/` directory
2. Check file extension is `.md`
3. Ensure frontmatter is valid YAML

### Hooks Not Triggering

1. Check hooks.json syntax
2. Verify script paths use `${CLAUDE_PLUGIN_ROOT}`
3. Test scripts manually outside Claude

## File Locations

| Path | Purpose |
|------|---------|
| `~/.claude/plugins/` | Plugin installation root |
| `~/.claude/plugins/cache/` | Cached plugin versions |
| `~/.claude/plugins/installed_plugins.json` | Installation registry |
| `~/.claude/plugins/marketplaces/` | Marketplace repositories |
