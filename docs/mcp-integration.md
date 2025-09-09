# MCP Server Integration for ClearFlow

The Model Context Protocol (MCP) server provides structured access to ClearFlow documentation for AI assistants.

## Prerequisites

```bash
# Install dependencies
uv add --dev mcpdoc

# Generate documentation files
python scripts/generate_llms_full.py

# Start the server (for local integrations)
python scripts/run_mcp_server.py
```

The server runs on `localhost:8765` by default.

## Terminal AI Assistants

### Claude Code (Primary)

Claude Code is Anthropic's terminal-powered AI coding assistant with deep codebase awareness.

#### Method 1: CLI Wizard (Simple)

```bash
# Add ClearFlow MCP server
claude mcp add clearflow --scope user

# When prompted, configure:
# Command: python
# Args: /path/to/ClearFlow/scripts/run_mcp_server.py
```

#### Method 2: Direct Configuration (Recommended)

Edit the configuration file directly for more control:

**macOS/Linux:**

```bash
# Primary location
vi ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Alternative
vi ~/.claude.json
```

**Windows:**

```bash
# Edit in your preferred editor
%APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration:

```json
{
  "mcpServers": {
    "clearflow": {
      "command": "python",
      "args": ["/absolute/path/to/ClearFlow/scripts/run_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/ClearFlow"
      }
    }
  }
}
```

**Verification:**

```bash
# List configured servers
claude mcp list

# Test the connection
claude mcp get clearflow

# Remove if needed
claude mcp remove clearflow
```

**Usage in Claude Code:**

```bash
# Once configured, Claude Code automatically has access
claude "Explain ClearFlow's Node architecture"
claude "Create a new flow that implements RAG"
```

### Gemini CLI

Gemini CLI supports MCP servers for extending its capabilities.

**Configuration:**

1. Create MCP configuration file:

    ```bash
    mkdir -p ~/.gemini/mcp
    vi ~/.gemini/mcp/clearflow.json
    ```

2. Add server configuration:

    ```json
    {
      "name": "clearflow",
      "type": "python",
      "command": "python",
      "args": ["/path/to/ClearFlow/scripts/run_mcp_server.py"],
      "description": "ClearFlow documentation and code examples"
    }
    ```

3. Register with Gemini CLI:

    ```bash
    gemini mcp register ~/.gemini/mcp/clearflow.json
    ```

**Usage:**

```bash
# Access ClearFlow documentation through Gemini
gemini "Using ClearFlow docs, show me how to build a chat flow"
```

## IDE Integration

### Claude Desktop App

The Claude desktop application (different from Claude Code CLI) can also use MCP servers.

Add to your configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "clearflow": {
      "command": "python",
      "args": ["/path/to/ClearFlow/scripts/run_mcp_server.py"]
    }
  }
}
```

Restart the Claude desktop app after making changes.

### Cursor

1. Open Cursor settings
2. Navigate to Features → Docs
3. Add custom documentation URL: `http://localhost:8765/docs`
4. Ensure MCP server is running

### Windsurf

Similar to Cursor - add `http://localhost:8765/docs` as a custom documentation source.

## API Endpoints

When running, the MCP server exposes:

- `GET /` - Server information
- `GET /docs` - Full documentation (llms-full.txt)
- `GET /index` - Documentation index (llms.txt)
- `POST /search` - Search documentation with query

## Customization

Edit `mcp_server_config.json` to change:

- Server host/port
- Documentation paths
- Server capabilities

## Benefits

- **Reduced context usage** - Server chunks documentation intelligently
- **Better relevance** - AI assistants can search specific topics
- **Live updates** - Changes to documentation reflect immediately
- **IDE integration** - Native support in modern AI-powered editors

## Troubleshooting

### Common Issues

**"Connection closed" error:**

- Ensure Python is in your PATH
- Use absolute paths in configuration
- Check if the MCP server script is executable

**"Server not found" error:**

- Verify llms-full.txt exists: `ls llms-full.txt`
- Regenerate if needed: `python scripts/generate_llms_full.py`
- Ensure mcpdoc is installed: `uv add --dev mcpdoc`

**Configuration not loading:**

- Restart Claude Code/Gemini CLI after config changes
- Check JSON syntax in config files
- Verify file permissions on config files

### Security Notes

⚠️ **Important:** Only use MCP servers you trust. The server has access to execute code and read files.

- Review the source code of MCP servers before installation
- Use project-scoped configurations for sensitive projects
- Avoid global installations of untrusted MCP servers
- Be cautious with servers that fetch external content (prompt injection risk)

## Advanced Configuration

### Project-Specific Settings

For project-specific MCP servers in Claude Code:

```bash
# Add to current project only
claude mcp add clearflow --scope project

# This creates .claude/mcp.json in your project root
```

### Environment Variables

Pass environment variables for dynamic configuration:

```json
{
  "mcpServers": {
    "clearflow": {
      "command": "python",
      "args": ["${HOME}/projects/ClearFlow/scripts/run_mcp_server.py"],
      "env": {
        "CLEARFLOW_ROOT": "${HOME}/projects/ClearFlow",
        "MCP_DEBUG": "true"
      }
    }
  }
}
```
