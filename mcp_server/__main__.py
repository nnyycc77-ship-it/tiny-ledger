"""Entry point: python3 -m mcp_server  (speaks MCP over stdio)."""
import sys

from mcp_server.recall_mcp import main

sys.exit(main())
