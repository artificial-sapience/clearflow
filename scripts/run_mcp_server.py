#!/usr/bin/env python3
"""Run MCP server for ClearFlow documentation.

This server provides structured access to ClearFlow documentation
for AI assistants through the Model Context Protocol (MCP).
"""

import json
import sys
from pathlib import Path

try:
    from mcpdoc import serve_docs
except ImportError:
    print("Error: mcpdoc not installed. Install with: uv add --dev mcpdoc")
    sys.exit(1)


def main():
    """Start the MCP documentation server."""
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Check if llms files exist
    llms_txt = project_root / "llms.txt"
    llms_full = project_root / "llms-full.txt"
    
    if not llms_txt.exists():
        print(f"Error: {llms_txt} not found")
        print("Generate with: python scripts/generate_llms_full.py")
        sys.exit(1)
    
    if not llms_full.exists():
        print(f"Error: {llms_full} not found")
        print("Generate with: python scripts/generate_llms_full.py")
        sys.exit(1)
    
    # Load configuration
    config_path = project_root / "mcp_server_config.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        print(f"Loaded configuration from {config_path}")
    else:
        # Default configuration
        config = {
            "name": "clearflow-mcp",
            "server": {
                "host": "localhost", 
                "port": 8765
            }
        }
    
    # Start server
    print(f"\n🚀 Starting ClearFlow MCP Server")
    print(f"📍 Host: {config['server']['host']}")
    print(f"🔌 Port: {config['server']['port']}")
    print(f"📚 Serving: {llms_txt.name} and {llms_full.name}")
    print("\nServer ready for AI assistant connections...")
    print("Press Ctrl+C to stop the server\n")
    
    # Serve documentation
    serve_docs(
        docs_path=str(llms_full),
        index_path=str(llms_txt),
        host=config['server']['host'],
        port=config['server']['port']
    )


if __name__ == "__main__":
    main()